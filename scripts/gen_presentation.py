#!/usr/bin/env python3
"""gen_presentation.py <pid> — gera o vídeo de apresentação de um repositório.
Pipeline: clona/descompacta → agente escreve content.ts → ícones → TTS+áudio → render → publica.
Roda LOCAL (Mac): precisa git, node/npx, ffmpeg, ELEVENLABS_API_KEY e um agente (gemini/codex) logado.
Config por env:
  AGENT_CMD   default 'gemini -y -p {prompt_file}'  (use {prompt_file} ou {prompt})
  ELEVENLABS_API_KEY  (senão renderiza sem narração)
"""
import sys, os, json, re, subprocess, shutil, tempfile, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
TEMPLATE = os.path.join(ROOT, "presentation-template")
PRES_F = "data/presentations.json"
EL_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
EL_MODEL = "eleven_multilingual_v2"
VOICE_IDS = {  # nomes mostrados no site → voice id ElevenLabs (multilingual)
    "Eric": "cjVigY5qzO86Huf0OWal", "Sarah": "EXAVITQu4vr4xnSDxMaL",
    "Daniel": "onwK4e9ZLuTAKqWW03F9", "George": "JBFqnCBsd6RMkjVDRZzb",
    "Antonio": "cjVigY5qzO86Huf0OWal",
}
LANG_NAME = {"pt": "português do Brasil", "en": "English"}

def load(): return json.load(open(PRES_F))
def save(d): json.dump(d, open(PRES_F, "w"), ensure_ascii=False, indent=2)
def set_status(pid, **kw):
    d = load()
    for p in d["presentations"]:
        if p["id"] == pid: p.update(kw)
    save(d)
def entry(pid):
    for p in load()["presentations"]:
        if p["id"] == pid: return p
    raise SystemExit(f"pid {pid} não encontrado")

def sh(cmd, cwd=None, env=None, timeout=None):
    print("›", " ".join(cmd) if isinstance(cmd, list) else cmd, flush=True)
    return subprocess.run(cmd, cwd=cwd, env=env, timeout=timeout)

def get_source(p, work):
    repodir = os.path.join(work, "repo")
    if p.get("source") == "zip" and p.get("zip") and os.path.exists(p["zip"]):
        os.makedirs(repodir, exist_ok=True)
        sh(["unzip", "-q", os.path.abspath(p["zip"]), "-d", repodir])
        subs = [d for d in os.listdir(repodir) if os.path.isdir(os.path.join(repodir, d))]
        if len(subs) == 1 and not os.path.exists(os.path.join(repodir, "README.md")):
            return os.path.join(repodir, subs[0])
        return repodir
    # github
    r = sh(["git", "clone", "--depth", "1", p["repo"], repodir], timeout=180)
    if r.returncode != 0: raise SystemExit("git clone falhou")
    return repodir

def repo_digest(repodir, limit=60000):
    """Resumo do repo p/ o modo API: README + manifestos + árvore + trechos de UI/CSS."""
    parts = []
    def add(title, text):
        if text: parts.append(f"### {title}\n{text[:8000]}")
    import glob
    for name in ("README.md", "README", "readme.md", "DOCUMENTATION.md", "STATUS.md"):
        fp = os.path.join(repodir, name)
        if os.path.exists(fp): add(name, open(fp, errors="ignore").read()); break
    for name in ("package.json", "requirements.txt", "pyproject.toml", "go.mod", "Cargo.toml", "composer.json"):
        fp = os.path.join(repodir, name)
        if os.path.exists(fp): add(name, open(fp, errors="ignore").read())
    # árvore (até 200 arquivos relevantes)
    tree = []
    for root, dirs, files in os.walk(repodir):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "dist", "build", ".next", "vendor", "__pycache__")]
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), repodir)
            tree.append(rel)
        if len(tree) > 400: break
    add("Estrutura de arquivos", "\n".join(sorted(tree)[:300]))
    # trechos de UI/CSS/entrypoints
    cand = []
    for pat in ("**/*.css", "**/globals.css", "**/index.html", "**/App.*", "**/main.*", "**/layout.*", "**/server.*", "**/index.*"):
        cand += glob.glob(os.path.join(repodir, pat), recursive=True)
    seen = 0
    for fp in cand:
        if "node_modules" in fp or seen >= 6: continue
        try: add(os.path.relpath(fp, repodir), open(fp, errors="ignore").read()); seen += 1
        except Exception: pass
    return "\n\n".join(parts)[:limit]

def gen_content_api(repodir, p, work):
    """Gera content.ts via API do Gemini (sem CLI) — roda 100% online."""
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key: return None
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    digest = repo_digest(repodir)
    spec = open("scripts/agent_prompt.md").read()
    lang_name = LANG_NAME.get(p.get("lang", "pt"), "português")
    instr = ("\n\nINSTRUÇÕES EXTRAS DO USUÁRIO (prioridade alta): " + p["instructions"]) if p.get("instructions") else ""
    prompt = (f"{spec}\n\n=== DIGEST DO REPOSITÓRIO ===\n{digest}\n\n"
        f"Gere o objeto `content` (NÃO o arquivo .ts, só o JSON) para um vídeo {p.get('format')} "
        f"em {lang_name}, voz {p.get('voice')}, tipo {p.get('tipo')}. "
        f"Use os campos do tipo Content (brand, format, lang, voice, scenes[]). {instr}\n"
        "Responda APENAS JSON do objeto content.")
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "responseMimeType": "application/json"}})
    bf = os.path.join(work, "_gemini_req.json"); open(bf, "w").write(body)
    # tenta o modelo escolhido e cai p/ alternativos; retry com backoff em sobrecarga transitória
    models = [model, "gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash"]
    models = list(dict.fromkeys(models))  # dedup mantendo ordem
    import time as _t
    obj = None
    for attempt in range(6):
        m = models[min(attempt, len(models) - 1)]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}"
        r = subprocess.run(["curl", "-s", "--max-time", "120", "-X", "POST", url, "-H", "Content-Type: application/json",
            "--data-binary", f"@{bf}"], capture_output=True, text=True)
        try:
            gj = json.loads(r.stdout)
            txt = gj["candidates"][0]["content"]["parts"][0]["text"]
            obj = json.loads(txt); break
        except Exception as e:
            msg = (r.stdout or "")[:160]
            transient = any(w in r.stdout for w in ("high demand", "UNAVAILABLE", "overloaded", "RESOURCE_EXHAUSTED", "try again", "503", "500"))
            print(f"  ⚠ Gemini {m} tentativa {attempt+1} falhou: {str(e)[:80]} · {msg}", flush=True)
            if not transient and "candidates" not in r.stdout and attempt >= len(models) - 1:
                pass  # erro não-transitório e já tentou os modelos → segue tentando até esgotar attempts
            _t.sleep(min(5 * (attempt + 1), 30))
    if obj is None:
        print("  ⚠ API Gemini esgotou tentativas", flush=True); return None
    # força format/lang/voice escolhidos no site
    obj["format"] = p.get("format", "16:9"); obj["lang"] = p.get("lang", "pt"); obj["voice"] = p.get("voice", "Eric")
    return 'import type { Content } from "./content";\nexport const CONTENT: Content = ' + json.dumps(obj, ensure_ascii=False, indent=2) + ";\n"

def run_agent(prompt_path, work):
    tmpl = os.environ.get("AGENT_CMD", "gemini -y -p {prompt_file}")
    prompt = open(prompt_path).read()
    if "{prompt_file}" in tmpl:
        cmd = tmpl.replace("{prompt_file}", "@" + prompt_path if "gemini" in tmpl else prompt_path)
        # gemini lê stdin; passamos o prompt por stdin de forma robusta:
    # forma robusta p/ ambos: passa o prompt por stdin
    if tmpl.startswith("gemini"):
        cmd = ["gemini", "-y", "--skip-trust", "-p", prompt]
    elif tmpl.startswith("codex"):
        cmd = ["codex", "exec", "--dangerously-bypass-approvals-and-sandbox", "--skip-git-repo-check", "-C", work, prompt]
    else:
        cmd = tmpl.split()
    print("› agente:", cmd[0], "(headless)", flush=True)
    aenv = dict(os.environ, GEMINI_CLI_TRUST_WORKSPACE="true")
    r = subprocess.run(cmd, cwd=work, env=aenv, timeout=900)
    return r.returncode == 0

PLACEHOLDER_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
    '<circle cx="12" cy="12" r="9" fill="#94A3B8"/></svg>')
def fetch_icons(content_ts, composer):
    # aceita aspas simples ou duplas
    icons = set(re.findall(r"""["']?icon["']?\s*:\s*['"]([a-z0-9.\-]+)['"]""", content_ts))
    icondir = os.path.join(composer, "public", "icons")
    os.makedirs(icondir, exist_ok=True)
    have = {os.path.splitext(f)[0] for f in os.listdir(icondir)}
    for slug in icons:
        if slug in have: continue
        ok = False
        for url in (f"https://cdn.simpleicons.org/{slug}",
                    f"https://cdn.jsdelivr.net/npm/simple-icons/icons/{slug}.svg"):
            try:
                with urllib.request.urlopen(url, timeout=15) as resp:
                    data = resp.read()
                if data and b"<svg" in data:
                    open(os.path.join(icondir, slug + ".svg"), "wb").write(data); ok = True; break
            except Exception: continue
        if not ok:  # garante que o arquivo exista (senão o render Remotion quebra com 404)
            open(os.path.join(icondir, slug + ".svg"), "w").write(PLACEHOLDER_SVG)
            print(f"  ⚠ ícone '{slug}' não encontrado → placeholder", flush=True)

def narrations(content_ts):
    # casa tanto `narration: "..."` (TS) quanto `"narration": "..."` (JSON do modo API)
    return re.findall(r'"?narration"?\s*:\s*"((?:[^"\\]|\\.)*)"', content_ts)

def el_tts(text, voice_id, out):
    body = json.dumps({"text": text, "model_id": EL_MODEL,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "use_speaker_boost": True}})
    subprocess.run(["curl", "-s", "--max-time", "90", "-X", "POST",
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        "-H", f"xi-api-key: {EL_KEY}", "-H", "Content-Type: application/json",
        "--data-binary", body, "-o", out], check=True)
    head = open(out, "rb").read(3)
    return head in (b"ID3", b"\xff\xf3", b"\xff\xfb")

def dur_of(p):
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip()
    return float(o) if o else 0.0

def build_audio(seg_durs, narr_dir, composer):
    """voz por cena (lead-in 0.45s + pad até dur) + cama Dm ducked → narration-final.mp3"""
    segs = []
    for i, d in enumerate(seg_durs):
        mp3 = os.path.join(narr_dir, f"{i:02d}.mp3")
        wav = os.path.join(narr_dir, f"seg{i:02d}.wav")
        if not os.path.exists(mp3):  # cena sem narração → silêncio
            subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-t", str(d/30.0), "-i",
                "anullsrc=r=44100:cl=stereo", wav], capture_output=True)
        else:
            subprocess.run(["ffmpeg", "-y", "-i", mp3, "-af",
                f"adelay=450|450,apad,atrim=0:{d/30.0},aresample=44100", "-ac", "2", wav], capture_output=True)
        segs.append(wav)
    concat = os.path.join(narr_dir, "_c.txt")
    open(concat, "w").write("".join(f"file '{s}'\n" for s in segs))
    voice = os.path.join(narr_dir, "voice.wav")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat, "-c", "copy", voice], capture_output=True)
    total = dur_of(voice)
    out = os.path.join(composer, "public", "audio", "narration-final.mp3")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    # 1) BASE GARANTIDA: narração (voz) já vira o mp3 final. Sempre existe.
    try:
        subprocess.run(["ffmpeg", "-y", "-i", voice, "-t", str(total), "-ac", "2", "-ar", "44100",
            "-b:a", "192k", out], capture_output=True, timeout=120, check=True)
    except Exception as e:
        print("  ⚠ voz→mp3 falhou:", str(e)[:120], flush=True)
    # 2) BEST-EFFORT: adiciona cama ambiente por cima (se falhar, fica a voz pura)
    try:
        bed = os.path.join(narr_dir, "bed.wav")
        subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"sine=frequency=146.83:duration={total}",
            "-f", "lavfi", "-i", f"sine=frequency=220:duration={total}",
            "-f", "lavfi", "-i", f"sine=frequency=293.66:duration={total}",
            "-filter_complex", "[0:a]volume=0.5[a];[1:a]volume=0.32[b];[2:a]volume=0.22[c];"
            "[a][b][c]amix=inputs=3:normalize=0,lowpass=f=600,highpass=f=70,volume=0.15,aresample=44100[bed]",
            "-map", "[bed]", "-t", str(total), "-ac", "2", bed], capture_output=True, timeout=90, check=True)
        mixed = os.path.join(narr_dir, "mixed.mp3")
        subprocess.run(["ffmpeg", "-y", "-i", voice, "-i", bed, "-filter_complex",
            "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=0,alimiter=limit=0.95,aresample=44100[o]",
            "-map", "[o]", "-t", str(total), "-ac", "2", "-b:a", "192k", mixed], capture_output=True, timeout=90, check=True)
        if os.path.exists(mixed) and os.path.getsize(mixed) > 1000:
            os.replace(mixed, out)
    except Exception as e:
        print("  ⚠ cama musical pulada (voz pura):", str(e)[:120], flush=True)
    return os.path.exists(out) and os.path.getsize(out) > 1000

def main():
    pid = sys.argv[1]
    p = entry(pid)
    set_status(pid, status="generating", error=None)
    work = tempfile.mkdtemp(prefix=f"mlpres_{pid}_")
    try:
        repodir = get_source(p, work)
        composer = os.path.join(work, "composer")
        shutil.copytree(TEMPLATE, composer, ignore=shutil.ignore_patterns("node_modules", "renders-tmp", "stills"))
        os.symlink(os.path.join(TEMPLATE, "node_modules"), os.path.join(composer, "node_modules"))

        out_file = os.path.join(composer, "src", "content.ts")
        prompt = open("scripts/agent_prompt.md").read()
        repl = {"{REPO_DIR}": repodir, "{OUT_FILE}": out_file, "{FORMAT}": p.get("format", "16:9"),
                "{LANG}": p.get("lang", "pt"), "{LANG_NAME}": LANG_NAME.get(p.get("lang", "pt"), "português"),
                "{VOICE}": p.get("voice", "Eric")}
        for k, v in repl.items(): prompt = prompt.replace(k, v)
        if p.get("instructions"):
            prompt += ("\n\n## INSTRUÇÕES EXTRAS DO USUÁRIO (prioridade alta)\n"
                       + p["instructions"])
        ppath = os.path.join(work, "PROMPT.md"); open(ppath, "w").write(prompt)

        # modo de geração: API (online, default se houver GEMINI_API_KEY) ou CLI (gemini/codex no Mac)
        mode = os.environ.get("GEN_MODE", "api" if os.environ.get("GEMINI_API_KEY") else "cli")
        content_ts = None
        if mode == "api":
            content_ts = gen_content_api(repodir, p, work)
            if content_ts: open(out_file, "w").write(content_ts)
        if not content_ts:  # fallback CLI
            if not run_agent(ppath, work): raise SystemExit("agente falhou")
            if not os.path.exists(out_file): raise SystemExit("agente não escreveu content.ts")
            content_ts = open(out_file).read()
        fetch_icons(content_ts, composer)

        # narração + durações
        durs = None
        if EL_KEY:
            narrs = narrations(content_ts)
            narr_dir = os.path.join(work, "narr"); os.makedirs(narr_dir, exist_ok=True)
            vid = VOICE_IDS.get(p.get("voice", "Eric"), VOICE_IDS["Eric"])
            seg_durs = []
            for i, t in enumerate(narrs):
                mp3 = os.path.join(narr_dir, f"{i:02d}.mp3")
                ok = el_tts(t.encode().decode("unicode_escape"), vid, mp3)
                d = dur_of(mp3) if ok else 4.0
                seg_durs.append(round(d * 30) + 39)
            audio_ok = build_audio(seg_durs, narr_dir, composer)
            durs = seg_durs
            open(os.path.join(composer, "src", "durations.ts"), "w").write(
                f"export const DURS: number[] | null = {json.dumps(durs)};\nexport const AUDIO = {str(bool(audio_ok)).lower()};\n")

        # render
        out_mp4 = os.path.join(work, "out.mp4")
        r = sh(["npx", "remotion", "render", "src/index.tsx", "Presentation", out_mp4], cwd=composer, timeout=1200)
        if r.returncode != 0 or not os.path.exists(out_mp4):
            raise SystemExit("render falhou")

        # publica
        os.makedirs("library/presentations", exist_ok=True)
        final = f"library/presentations/{pid}.mp4"
        shutil.copy(out_mp4, final)
        thumb = f"library/presentations/{pid}.jpg"
        subprocess.run(["ffmpeg", "-y", "-ss", "2", "-i", final, "-vframes", "1", "-vf", "scale=480:-1", thumb], capture_output=True)
        dd = dur_of(final); mm = int(dd // 60); ss = int(dd % 60)
        set_status(pid, status="done", video=final, thumb=thumb, durationApprox=f"{mm}:{ss:02d}", error=None)
        print("✅ pronto:", final, flush=True)
    except Exception as e:
        set_status(pid, status="error", error=str(e)[:200])
        print("❌ erro:", e, flush=True)
        raise
    finally:
        shutil.rmtree(work, ignore_errors=True)

if __name__ == "__main__":
    main()
