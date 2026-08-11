#!/usr/bin/env python3
# notion_poll.py — varre o seu workspace do Notion e ingere AUTOMATICAMENTE como cards
# toda página com cara de reunião/call/gravação (antigas e novas), com o conteúdo + link direto.
# Roda no container (loop do entrypoint). Idempotente: dedup por URL do Notion.
#   NOTION_TOKEN=ntn_… python3 scripts/notion_poll.py
import os, sys, json, re, time, unicodedata, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
TOK = os.environ.get("NOTION_TOKEN", "")
if not TOK:
    print("sem NOTION_TOKEN — pulando"); sys.exit(0)
H = {"Authorization": f"Bearer {TOK}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
LOCK = "data/.notion.lock"

def log(m): print(m); open("data/notion_poll.log", "a").write(m + "\n")
def api(method, path, body=None):
    req = urllib.request.Request("https://api.notion.com" + path,
        data=json.dumps(body).encode() if body else None, headers=H, method=method)
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)

# lock (tolera obsoleto após restart)
if os.path.exists(LOCK):
    try:
        os.kill(int(open(LOCK).read().strip()), 0); print("já rodando"); sys.exit(0)
    except Exception: pass
open(LOCK, "w").write(str(os.getpid()))

MEET_RE = re.compile(r"\b(call\b|reuni[ãa]o|meeting|recording|kickoff|onboarding|demo\b|screen recording|"
                     r"an[áa]lise.*reuni|transcri[çc][ãa]o da reuni|daily)\b", re.I)
TASK_RE = re.compile(r"^(criar|configurar|confirmar|receber|implementar|acessar|instalar|comprimir|marcar|"
                     r"transcrever|clonar|melhorar|revisar|enviar|preencher|adicionar|task)\b", re.I)
# PEOPLE: nomes usados para identificar de quem é a call. Preencha via env (CALL_PEOPLE=a,b,c)
# com os nomes da sua equipe/clientes.
PEOPLE = os.environ.get("CALL_PEOPLE", "").split(",") if os.environ.get("CALL_PEOPLE") else []
def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+","-", s).strip("-").lower()[:55]
def title_of(p):
    for v in p.get("properties", {}).values():
        if v.get("type") == "title": return "".join(x.get("plain_text","") for x in v["title"])
    return ""
def date_of(p):
    dp = p.get("properties", {}).get("Date")
    if dp and dp.get("type") == "date" and dp.get("date"): return (dp["date"].get("start") or "")[:10]
    return (p.get("created_time") or "")[:10]
def derive(name):
    low = name.lower()
    pessoa = next((x for x in PEOPLE if x.lower() in low), "")
    # personalize essa heurística com os nomes reais dos seus projetos/clientes
    proj = "Onboarding / Interno" if any(k in low for k in ("onboarding","interno")) else ""
    return pessoa, proj
def rich(b):
    t = b.get("type"); v = b.get(t, {})
    rt = v.get("rich_text") if isinstance(v, dict) else None
    return "".join(x.get("plain_text","") for x in (rt or []))
def page_text(pid):
    """retorna (markdown, tem_audio). tem_audio=True só se a página tiver bloco de áudio (gravação do Notion)."""
    try: data = api("GET", f"/v1/blocks/{pid}/children?page_size=100")
    except Exception: return "", False
    out = []; has_audio = False
    for b in data.get("results", []):
        t = b.get("type", ""); txt = rich(b)
        if t == "audio": has_audio = True; out.append("🎙 *(áudio gravado no Notion)*")
        elif t.startswith("heading"): out.append("## " + txt)
        elif t in ("bulleted_list_item","numbered_list_item","to_do"): out.append("- " + txt)
        elif t == "quote": out.append("> " + txt)
        elif txt: out.append(txt)
    return "\n\n".join(out), has_audio

def main():
    data = json.load(open("data/calls.json"))
    have = {c.get("notion") for c in data["calls"] if c.get("notion")}
    have_ids = {c["id"] for c in data["calls"]}
    added = []
    # SÓ áudios transcritos do Notion: busca por termos de áudio + páginas recentes,
    # e importa APENAS se a página tiver um bloco de áudio (gravação real do Notion).
    QUERIES = ["áudio", "audio", "gravação", "gravacao", "recording", "transcri", ""]
    cap = int(os.environ.get("NOTION_MAX", "15"))
    candidates = {}   # url -> page
    for query in QUERIES:
        body = {"page_size": 100}
        if query: body["query"] = query
        else: body["sort"] = {"direction":"descending","timestamp":"last_edited_time"}
        try: res = api("POST", "/v1/search", body)
        except Exception as e: log(f"erro search '{query}': {e}"); continue
        for p in res.get("results", []):
            if p.get("object") == "page" and p.get("url") and p["url"] not in have:
                candidates.setdefault(p["url"], p)
    for url, p in candidates.items():
        if len(added) >= cap: break
        md, has_audio = page_text(p["id"].replace("-",""))
        time.sleep(0.35)
        if not has_audio: continue   # ← só páginas com áudio gravado
        name = (title_of(p).strip() or "Áudio do Notion")
        date = date_of(p)
        cid = "naudio_" + date + "_" + slug(name)
        if cid in have_ids: continue
        pessoa, proj = derive(name)
        body_md = f"# 🎙 {name}\n\n> **Áudio transcrito no Notion** · {date}\n\n" + md
        notes = f"library/notes/{cid}.md"
        os.makedirs("library/notes", exist_ok=True); open(notes, "w").write(body_md)
        data["calls"].append({"id":cid,"pessoa":pessoa,"title":"🎙 "+name,"date":date,"projeto":proj,
            "assunto":["áudio Notion"],"participantes":[pessoa] if pessoa else [],
            "type":"audio","audio":None,"notion":url,"github":None,"driveVideoId":None,"sizeMB":None,
            "durationApprox":None,"geminiOk":True,"notes":notes,"transcript":None,"video":None,"status":"transcribed"})
        added.append((cid, url)); have.add(url); have_ids.add(cid)
    if added:
        json.dump(data, open("data/calls.json","w"), ensure_ascii=False, indent=2)
        try: meta = json.load(open("data/meta.json"))
        except Exception: meta = {}
        for cid, url in added: meta.setdefault(cid, {})["notion"] = url
        json.dump(meta, open("data/meta.json","w"), ensure_ascii=False, indent=2)
        log(f"+ {len(added)} card(s) do Notion: {', '.join(c for c,_ in added[:6])}{'…' if len(added)>6 else ''}")
    else:
        log("nenhuma reunião nova no Notion")

try: main()
finally:
    try: os.remove(LOCK)
    except Exception: pass
