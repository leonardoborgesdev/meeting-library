#!/usr/bin/env python3
"""render_worker.py — worker de render de apresentações (pode rodar em host separado do app
principal, poupando o servidor principal do trabalho pesado de renderização).
Faz POLL de jobs 'queued' na main app, gera o vídeo (Gemini API + Remotion) e envia o
resultado de volta pra main app via upload HTTP. Roda de forma independente (headless).
Env: MAIN_APP (url da main app), WORKER_TOKEN, GEMINI_API_KEY, ELEVENLABS_API_KEY.
"""
import os, sys, json, time, shutil, tempfile, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_presentation as g

MAIN = os.environ.get("MAIN_APP", "http://localhost:8009").rstrip("/")
TOKEN = os.environ.get("WORKER_TOKEN", "")
POLL = int(os.environ.get("RENDER_POLL", "20"))
TEMPLATE = os.path.join(g.ROOT, "presentation-template")

def post(path, body=None):
    data = json.dumps(body or {}).encode()
    req = urllib.request.Request(MAIN + path, data=data, method="POST",
        headers={"Content-Type": "application/json", "X-Worker-Token": TOKEN})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read() or b"{}")

def claim():
    try: return post("/api/presentations/claim").get("job")
    except Exception as e: print("claim erro:", str(e)[:120], flush=True); return None

def complete(pid, **kw):
    kw["id"] = pid
    try: post("/api/presentations/complete", kw)
    except Exception as e: print("complete erro:", str(e)[:120], flush=True)

def upload_result(pid, fpath, kind):
    data = open(fpath, "rb").read()
    req = urllib.request.Request(
        f"{MAIN}/api/presentations/upload_result?id={pid}&kind={kind}",
        data=data, method="POST",
        headers={"Content-Type": "application/octet-stream", "X-Worker-Token": TOKEN})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read() or b"{}")

def fetch_zip(pid, work):
    """Baixa o .zip do repo da main app (volume) via HTTP autenticado, retorna caminho local."""
    dest = os.path.join(work, f"{pid}.zip")
    req = urllib.request.Request(f"{MAIN}/api/presentations/zip?id={pid}",
        headers={"X-Worker-Token": TOKEN})
    with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as fh:
        while True:
            chunk = r.read(1 << 16)
            if not chunk: break
            fh.write(chunk)
    return dest

def process(job):
    pid = job["id"]; print(f"▶ gerando {pid} ({job.get('repo')})", flush=True)
    work = tempfile.mkdtemp(prefix=f"rw_{pid}_")
    try:
        if job.get("source") == "zip":
            job["zip"] = fetch_zip(pid, work)
            print(f"  ↓ zip baixado: {job['zip']}", flush=True)
        repodir = g.get_source(job, work)
        composer = os.path.join(work, "composer")
        shutil.copytree(TEMPLATE, composer, ignore=shutil.ignore_patterns("node_modules", "renders-tmp", "stills"))
        os.symlink(os.path.join(TEMPLATE, "node_modules"), os.path.join(composer, "node_modules"))
        out_file = os.path.join(composer, "src", "content.ts")
        content_ts = g.gen_content_api(repodir, job, work)
        if not content_ts: raise SystemExit("Gemini API não gerou content")
        open(out_file, "w").write(content_ts)
        g.fetch_icons(content_ts, composer)
        if g.EL_KEY:
            narrs = g.narrations(content_ts)
            nd = os.path.join(work, "narr"); os.makedirs(nd, exist_ok=True)
            vid = g.VOICE_IDS.get(job.get("voice", "Eric"), g.VOICE_IDS["Eric"])
            durs = []
            for i, t in enumerate(narrs):
                mp3 = os.path.join(nd, f"{i:02d}.mp3")
                ok = g.el_tts(t.encode().decode("unicode_escape"), vid, mp3)
                durs.append(round((g.dur_of(mp3) if ok else 4.0) * 30) + 39)
            audio_ok = g.build_audio(durs, nd, composer)
            if not os.path.exists(os.path.join(composer, "public", "audio", "narration-final.mp3")):
                audio_ok = False
            open(os.path.join(composer, "src", "durations.ts"), "w").write(
                f"export const DURS: number[] | null = {json.dumps(durs)};\nexport const AUDIO = {str(bool(audio_ok)).lower()};\n")
            print(f"  🔊 áudio: {'ok' if audio_ok else 'mudo (sem narração)'}", flush=True)
        out_mp4 = os.path.join(work, "out.mp4")
        print("  ⏳ renderizando (Remotion)...", flush=True)
        r = g.sh(["npx", "remotion", "render", "src/index.tsx", "Presentation", out_mp4,
                  "--concurrency=2"], cwd=composer, timeout=1800)
        if r.returncode != 0 or not os.path.exists(out_mp4): raise SystemExit("render falhou")
        # thumb
        thumb = os.path.join(work, "thumb.jpg")
        g.subprocess.run(["ffmpeg", "-y", "-ss", "2", "-i", out_mp4, "-vframes", "1", "-vf", "scale=480:-1", thumb], capture_output=True)
        # envia mp4 + thumb pra main app (volume) → servidos direto
        upload_result(pid, out_mp4, "mp4")
        if os.path.exists(thumb): upload_result(pid, thumb, "thumb")
        dd = g.dur_of(out_mp4); mm = int(dd // 60); ss = int(dd % 60)
        complete(pid, status="done", video=f"library/presentations/{pid}.mp4",
                 thumb=f"library/presentations/{pid}.jpg", durationApprox=f"{mm}:{ss:02d}", error=None)
        print(f"✅ {pid} pronto", flush=True)
    except Exception as e:
        complete(pid, status="error", error=str(e)[:200])
        print(f"❌ {pid}: {e}", flush=True)
    finally:
        shutil.rmtree(work, ignore_errors=True)

def main():
    print(f"render_worker no ar · main={MAIN} · poll={POLL}s", flush=True)
    while True:
        job = claim()
        if job: process(job)
        else: time.sleep(POLL)

if __name__ == "__main__":
    main()
