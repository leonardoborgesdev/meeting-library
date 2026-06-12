#!/usr/bin/env python3
# poll_drive.py — varre a pasta "Meet Recordings" do Drive (rclone), detecta gravações
# NOVAS (não presentes em calls.json) e processa cada uma: download -> transcrição ->
# walkthrough -> Supabase. Idempotente (dedup por driveVideoId). Rode via cron.
#
#   ASSEMBLYAI_API_KEY=… python3 scripts/poll_drive.py
import os, sys, json, re, subprocess, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
FOLDER = "1TDBW8XhTJPJ6cavHd3JkhVEut3vgDw22"   # pasta "Meet Recordings" (lucas@automatrix-ia.com)
LOCK = "data/.poll.lock"

# lock simples
if os.path.exists(LOCK):
    try:
        pid = int(open(LOCK).read().strip())
        os.kill(pid, 0)   # existe? -> outra execução rodando
        print("já rodando, saindo"); sys.exit(0)
    except Exception:
        pass
open(LOCK, "w").write(str(os.getpid()))

def log(m): print(m); open("data/poll.log","a").write(m+"\n")

PEOPLE = ["Nicolli","Nikolli","Leonardo","Leonam","Saulo","Mauricio","Maurício","Junior","Júnior",
          "Camila","Henrique","Chris","Gustavo","Nadeer","Cíntia","Cinthia","HVN","Kale","Ted","Thiago"]
def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+","-", s).strip("-").lower()
    return s[:60]
def derive(name):
    m = re.search(r"(\d{4})/(\d{2})/(\d{2})", name)
    date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else "2026-01-01"
    base = re.sub(r"\s*-\s*\d{4}/\d{2}/\d{2}.*$","", name).strip()  # tira a data + "- Recording"
    pessoa = next((p for p in PEOPLE if p.lower() in name.lower()), "Automatrix")
    low = name.lower()
    proj = ("Vistoria (Confere)" if "vistoria" in low else
            "Telemedicina (UBS)" if "telemedic" in low else
            "SDR WhatsApp / GVG" if "saulo" in low else
            "Automatrix Lead System" if "aquisic" in low or "aquisiç" in low else
            "SDR imobiliária (Plá)" if "junior" in low or "júnior" in low or "whatsapp" in low else
            "HVN — Edição com IA" if low.startswith("hvn") else
            "Automatrix")
    return date, base, pessoa, proj

def main():
    # lista a pasta de gravações
    try:
        out = subprocess.run(["rclone","lsjson","--drive-root-folder-id="+FOLDER,"gdrive:"],
                             capture_output=True, text=True, timeout=120)
        files = json.loads(out.stdout or "[]")
    except Exception as e:
        log(f"erro rclone: {e}"); return
    data = json.load(open("data/calls.json"))
    seen = {c.get("driveVideoId") for c in data["calls"]}
    SINCE = os.environ.get("POLL_SINCE", "2026-06-12")   # só processa gravações DESTA data em diante
    novos = []
    for f in files:
        name = f.get("Name",""); fid = f.get("ID","")
        if "video" not in (f.get("MimeType","") or ""): continue
        if "Recording" not in name: continue
        if re.search(r"Recording \d+\s*$", name): continue   # pula "Recording 2/3"
        if not fid or fid in seen: continue
        date, base, pessoa, proj = derive(name)
        if date < SINCE: continue   # ignora histórico (auto-pull só do que for novo a partir de hoje)
        cid = "auto_" + date + "_" + slug(base)
        if any(c["id"]==cid for c in data["calls"]): continue
        data["calls"].append({"id":cid,"pessoa":pessoa,"title":base,"date":date,"projeto":proj,
            "assunto":[],"participantes":["Lucas F. N. Alves"]+([pessoa] if pessoa!="Automatrix" else []),
            "driveVideoId":fid,"sizeMB":round(int(f.get("Size",0))/1048576) or None,
            "durationApprox":None,"geminiOk":True,"notes":None,"transcript":None,"video":None,"status":"catalog"})
        novos.append(cid); seen.add(fid)
    if os.environ.get("DRY"):
        log(f"DRY: {len(novos)} nova(s) detectada(s): {', '.join(novos) or '—'} (nada processado)")
        return
    if novos:
        json.dump(data, open("data/calls.json","w"), ensure_ascii=False, indent=2)
        log(f"{len(novos)} call(s) nova(s): {', '.join(novos)}")
    else:
        log("nenhuma call nova")
    # processa cada nova (download -> transcrição -> walkthrough), depois sobe pro Supabase
    env = dict(os.environ)
    for cid in novos:
        log(f"→ processando {cid}")
        subprocess.run(["bash","scripts/process_calls.sh",cid], env=env)
        subprocess.run(["bash","scripts/supabase_sync.sh",cid], env=env)
        # card de resumo/checklist automático (se houver LLM local configurado)
        if os.environ.get("AUTO_SUMMARY") == "1":
            subprocess.run(["python3","scripts/auto_summary.py",cid], env=env)

try:
    main()
finally:
    try: os.remove(LOCK)
    except Exception: pass
