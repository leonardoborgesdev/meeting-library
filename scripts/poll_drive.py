#!/usr/bin/env python3
# poll_drive.py — varre a pasta "Meet Recordings" do Drive (rclone) e abastece o catálogo.
#   FASE 1 (catalogar): adiciona TODA gravação ainda não presente como card (status "catalog").
#   FASE 2 (drenar):     processa até POLL_MAX_PER_RUN cards pendentes (mais novos primeiro),
#                        download -> transcrição -> walkthrough(55 frames) -> Supabase -> apaga local.
# Resumível e idempotente (dedup por driveVideoId). Roda em loop (cron interno do container).
#
#   POLL_SINCE=2025-01-01 POLL_MAX_PER_RUN=4 python3 scripts/poll_drive.py
import os, sys, json, re, subprocess, unicodedata, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
FOLDER = "1TDBW8XhTJPJ6cavHd3JkhVEut3vgDw22"   # pasta "Meet Recordings" (lucas@automatrix-ia.com)
LOCK = "data/.poll.lock"

# lock simples (tolera lock obsoleto após restart da máquina)
if os.path.exists(LOCK):
    try:
        pid = int(open(LOCK).read().strip())
        os.kill(pid, 0)
        print("já rodando, saindo"); sys.exit(0)
    except Exception:
        pass
open(LOCK, "w").write(str(os.getpid()))

def log(m): print(m); open("data/poll.log","a").write(m+"\n")

PEOPLE = ["Nicolli","Nikolli","Leonardo","Leonam","Saulo","Mauricio","Maurício","Junior","Júnior",
          "Camila","Henrique","Chris","Gustavo","Nadeer","Cíntia","Cinthia","Cintia","HVN","Kale",
          "Ted","Thiago","Vladia","Vládia","Lucas"]
def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+","-", s).strip("-").lower()
    return s[:60]
def derive(name, modtime=None):
    name = name.replace("／", "/")   # Meet usa solidus fullwidth (U+FF0F) na data
    m = re.search(r"(\d{4})/(\d{2})/(\d{2})", name)
    if m:   date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    elif modtime: date = modtime[:10]            # fallback: data de upload
    else:   date = "2026-01-01"
    base = re.sub(r"\s*-\s*\d{4}/\d{2}/\d{2}.*$","", name).strip()  # tira data + "- Recording"
    base = re.sub(r"\s*-\s*Recording.*$","", base).strip()         # tira "- Recording" se sobrou
    base = base.strip(" -") or "Gravação"
    pessoa = next((p for p in PEOPLE if p.lower() in name.lower()), "Automatrix")
    low = name.lower()
    proj = ("Chris Lamm / MortgageOne" if "chris" in low or "mortgage" in low or "lamm" in low else
            "Vistoria (Confere)" if "vistoria" in low else
            "Telemedicina (UBS)" if "telemedic" in low else
            "SDR WhatsApp / GVG" if "saulo" in low or "gvg" in low or "vladia" in low or "vládia" in low else
            "Automatrix Lead System" if "aquisic" in low or "aquisiç" in low else
            "SDR imobiliária (Plá)" if "junior" in low or "júnior" in low or "kinbox" in low else
            "HVN — Edição com IA" if low.startswith("hvn") else
            "Onboarding / Interno" if "onboarding" in low or "interna" in low else
            "Brazika (loja + painel)" if "brazika" in low else
            "Automatrix")
    return date, base, pessoa, proj

def catalog(data, files, since):
    seen = {c.get("driveVideoId") for c in data["calls"]}
    ids  = {c["id"] for c in data["calls"]}
    added = []
    for f in files:
        name = f.get("Name",""); fid = f.get("ID","")
        if "video" not in (f.get("MimeType","") or ""): continue
        if "Recording" not in name: continue
        if re.search(r"Recording \d+\s*$", name): continue   # pula "Recording 2/3" (partes)
        if not fid or fid in seen: continue
        date, base, pessoa, proj = derive(name, f.get("ModTime"))
        if date < since: continue
        cid = "auto_" + date + "_" + slug(base)
        if cid in ids: continue
        data["calls"].append({"id":cid,"pessoa":pessoa,"title":base,"date":date,"projeto":proj,
            "assunto":[],"participantes":["Lucas F. N. Alves"]+([pessoa] if pessoa!="Automatrix" else []),
            "driveVideoId":fid,"sizeMB":round(int(f.get("Size",0))/1048576) or None,
            "durationApprox":None,"geminiOk":True,"notes":None,"transcript":None,"video":None,"status":"catalog"})
        added.append(cid); seen.add(fid); ids.add(cid)
    return added

def main():
    try:
        out = subprocess.run(["rclone","lsjson","--drive-root-folder-id="+FOLDER,"gdrive:"],
                             capture_output=True, text=True, timeout=180)
        files = json.loads(out.stdout or "[]")
    except Exception as e:
        log(f"erro rclone: {e}"); return
    data = json.load(open("data/calls.json"))
    sb = json.load(open("data/supabase.json")) if os.path.exists("data/supabase.json") else {}
    since = os.environ.get("POLL_SINCE", "2025-01-01")
    maxrun = int(os.environ.get("POLL_MAX_PER_RUN", "4"))

    added = catalog(data, files, since)
    if added and not os.environ.get("DRY"):
        json.dump(data, open("data/calls.json","w"), ensure_ascii=False, indent=2)
        log(f"+ catalogadas {len(added)} gravação(ões)")

    # fila = cards de vídeo que precisam de trabalho: sem transcrição OU transcritos mas
    # sem frames no Supabase (interrompidos) → process_calls.sh re-baixa e completa (auto-cura)
    def needs_work(c):
        if c.get("type","video") != "video" or not c.get("driveVideoId"): return False
        if not c.get("transcript"): return True
        return not bool(sb.get(c["id"], {}).get("frames"))
    pending = [c for c in data["calls"] if needs_work(c)]
    pending.sort(key=lambda c: c.get("date",""), reverse=True)   # mais novas primeiro (call do dia tem prioridade)

    # cota DIÁRIA: processa poucos por dia (espalhado), nunca esvazia a fila de uma vez
    daily_max = int(os.environ.get("POLL_DAILY_MAX", "6"))
    today = datetime.date.today().isoformat()
    st_path = "data/.backfill_day"
    try: st = json.load(open(st_path))
    except Exception: st = {"date": today, "count": 0}
    if st.get("date") != today: st = {"date": today, "count": 0}
    left_today = max(0, daily_max - int(st.get("count", 0)))
    n = min(maxrun, left_today, len(pending))
    todo = pending[:n]
    log(f"catálogo: {len(data['calls'])} cards | pendentes: {len(pending)} | "
        f"hoje {st.get('count',0)}/{daily_max} | processando {len(todo)} neste run")

    if os.environ.get("DRY"):
        log("DRY: " + (", ".join(c["id"] for c in todo) or "— (cota do dia cheia ou fila vazia)")); return

    env = dict(os.environ)
    for c in todo:
        cid = c["id"]
        log(f"→ processando {cid} ({c.get('sizeMB','?')}MB)")
        subprocess.run(["bash","scripts/process_calls.sh",cid], env=env)   # já sincroniza Supabase + NOLOCAL
        if os.environ.get("AUTO_SUMMARY") == "1":
            subprocess.run(["python3","scripts/auto_summary.py",cid], env=env)
        st["date"] = today; st["count"] = int(st.get("count", 0)) + 1
        json.dump(st, open(st_path, "w"))
    if todo and len(pending) > len(todo):
        log(f"restam ~{len(pending)-len(todo)} na fila (cota diária {daily_max}/dia)")

try:
    main()
finally:
    try: os.remove(LOCK)
    except Exception: pass
