#!/usr/bin/env python3
# backup_media_teldrive.py — sobe TODA a mídia (library/videos + library/audio)
# pro Brazika Drive (Teldrive, storage "infinito" via Telegram), idempotente.
#
# - Cunha o JWT lendo a sessão mais recente no Postgres (fly ssh, 1x) + JWT_SECRET local.
# - Garante a pasta /meeting-library e pula o que já está lá (por nome).
# - Arquivos > ~1.8GB são enviados em PARTES (limite Telegram 2GB/parte).
# - Grava o mapa em data/teldrive.json: { "<arquivo>": {fileId, size, path} }.
#
# Uso:  python3 scripts/backup_media_teldrive.py [--dir library/videos] [--one arquivo.mp4]
import os, sys, json, time, hmac, hashlib, base64, subprocess, urllib.parse, urllib.request, mimetypes, ssl, secrets as _secrets
_SSL = ssl.create_default_context()
_SSL.check_hostname = False; _SSL.verify_mode = ssl.CERT_NONE  # Homebrew py sem certs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
DRIVE_DIR = os.environ.get("BRAZIKA_DRIVE_DIR", os.path.expanduser("~/Desktop/brazika-drive"))
API = "https://drive.brazika.online/api"
PGAPP = "brazika-drive-pg"
FOLDER = "/meeting-library"
CHUNK = int(os.environ.get("TD_CHUNK_BYTES", str(1800 * 1024 * 1024)))  # 1.8GB/parte
MAP_F = "data/teldrive.json"
MEDIA_EXT = (".mp4", ".mp3", ".wav", ".m4a", ".mov", ".mkv", ".webm")

def log(*a): print("[backup]", *a, flush=True)

def mint_token():
    tok = os.environ.get("TD_TOKEN")
    if tok: return tok
    sec_f = os.path.join(DRIVE_DIR, ".secrets.local")
    jwt_secret = None
    for line in open(sec_f):
        if line.startswith("JWT_SECRET="): jwt_secret = line.strip().split("=", 1)[1]
    if not jwt_secret: sys.exit("JWT_SECRET ausente em .secrets.local")
    log("lendo sessão do Postgres (fly ssh)...")
    row = subprocess.run(
        ["fly", "ssh", "console", "-a", PGAPP, "-C",
         "psql -U teldrive -d teldrive -At -F| -c \"SELECT user_id, hash FROM teldrive.sessions ORDER BY created_at DESC LIMIT 1;\""],
        capture_output=True, text=True).stdout.strip().splitlines()
    row = [r for r in row if "|" in r][-1]
    uid, h = row.split("|", 1)
    b = lambda x: base64.urlsafe_b64encode(x).rstrip(b"=")
    now = int(time.time())
    seg = b".".join([
        b(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode()),
        b(json.dumps({"sub": uid, "iat": now, "exp": now + 30 * 86400, "name": "Leo",
                      "userName": "", "isPremium": False, "hash": h}, separators=(",", ":")).encode())])
    return (seg + b"." + b(hmac.new(jwt_secret.encode(), seg, hashlib.sha256).digest())).decode()

def api(method, path, token, data=None, ctype=None, raw=False):
    url = API + path
    headers = {"Cookie": f"access_token={token}"}
    if ctype: headers["Content-Type"] = ctype
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=3600, context=_SSL) as r:
        body = r.read()
    return body if raw else (json.loads(body) if body else {})

def ensure_folder(token):
    try:
        api("POST", "/files", token,
            data=json.dumps({"name": "meeting-library", "type": "folder", "path": "/"}).encode(),
            ctype="application/json")
        log("pasta /meeting-library criada")
    except urllib.error.HTTPError as e:
        if e.code in (409, 400, 500): log("pasta /meeting-library já existe")
        else: raise

def existing_names(token):
    names = set()
    try:
        q = urllib.parse.urlencode({"path": FOLDER, "limit": 1000})
        d = api("GET", f"/files?{q}", token)
        for f in d.get("files", d.get("items", [])):
            names.add(f.get("name"))
    except Exception as e:
        log("aviso: não listei a pasta:", str(e)[:80])
    return names

def upload_part(token, upid, partname, partno, channel, blob):
    q = urllib.parse.urlencode({"partName": partname, "fileName": partname,
                                "partNo": partno, "channelId": channel, "encrypted": "false"})
    d = api("POST", f"/uploads/{upid}?{q}", token, data=blob, ctype="application/octet-stream")
    return d["partId"]

def upload_file(token, channel, fpath, name):
    size = os.path.getsize(fpath)
    upid = _secrets.token_hex(16)
    parts = []
    with open(fpath, "rb") as fh:
        n = 0
        while True:
            blob = fh.read(CHUNK)
            if not blob: break
            n += 1
            pname = f"{name}.part{n}"
            log(f"    parte {n} ({len(blob)//(1024*1024)}MB)...")
            pid = upload_part(token, upid, pname, n, channel, blob)
            parts.append({"id": int(pid)})
    mime = mimetypes.guess_type(name)[0] or "application/octet-stream"
    payload = {"name": name, "type": "file", "path": FOLDER, "mimeType": mime,
               "size": size, "channelId": int(channel), "encrypted": False,
               "uploadId": upid, "parts": parts}
    d = api("POST", "/files", token, data=json.dumps(payload).encode(), ctype="application/json")
    return d.get("id"), size

def main():
    dirs = ["library/videos", "library/audio"]
    only = None
    args = sys.argv[1:]
    if "--dir" in args: dirs = [args[args.index("--dir") + 1]]
    if "--one" in args: only = args[args.index("--one") + 1]

    token = mint_token()
    cfg = api("GET", "/users/config", token)
    channel = cfg["channelId"]
    log("canal", channel, "| bots:", len(cfg.get("bots", [])))
    if not cfg.get("bots"):
        sys.exit("sem bots no Teldrive — upload bloqueado. Add bots na UI primeiro.")
    ensure_folder(token)
    done = existing_names(token)
    log(f"{len(done)} arquivos já no drive (serão pulados)")

    try: mapping = json.load(open(MAP_F))
    except Exception: mapping = {}

    files = []
    for d in dirs:
        if not os.path.isdir(d): continue
        for fn in sorted(os.listdir(d)):
            if fn.lower().endswith(MEDIA_EXT) and not fn.endswith("_raw.mp4"):
                if only and fn != only: continue
                files.append(os.path.join(d, fn))

    log(f"{len(files)} arquivos de mídia candidatos")
    up = skip = fail = 0
    for fpath in files:
        name = os.path.basename(fpath)
        if name in done or name in mapping:
            skip += 1; continue
        size = os.path.getsize(fpath)
        log(f"→ {name} ({size//(1024*1024)}MB)")
        t0 = time.time()
        try:
            fid, sz = upload_file(token, channel, fpath, name)
            mapping[name] = {"fileId": fid, "size": sz, "path": FOLDER}
            json.dump(mapping, open(MAP_F, "w"), ensure_ascii=False, indent=2)
            up += 1
            log(f"  ✓ {name} em {int(time.time()-t0)}s  id={fid}")
        except Exception as e:
            fail += 1
            log(f"  ✗ {name} FALHOU: {str(e)[:160]}")
    log(f"FIM — enviados={up} pulados={skip} falhas={fail} | mapa em {MAP_F}")

if __name__ == "__main__":
    main()
