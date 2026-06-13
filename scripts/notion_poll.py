#!/usr/bin/env python3
# notion_poll.py — varre o Notion (Agency OS do Lucas) e ingere AUTOMATICAMENTE como cards
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
PEOPLE = ["Nicolli","Leonardo","Leonam","Saulo","Mauricio","Junior","Júnior","Camila","Henrique","Chris",
          "Gustavo","Nadeer","Cinthia","Kale","Ted","Thiago","Vladia","Vládia","Heaven","Marcelo","Kirsten",
          "Mark","Tami","Abdul","Phil","Ani","Leo","Lucas"]
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
    pessoa = next((x for x in PEOPLE if x.lower() in low), "Automatrix")
    proj = ("Chris Lamm / MortgageOne" if any(k in low for k in ("chris","mortgage","lamm","ted","kirsten","mark","tami","abdul","phil")) else
            "SDR WhatsApp / GVG" if any(k in low for k in ("saulo","gvg","vlád","vladia")) else
            "SDR imobiliária (Plá)" if any(k in low for k in ("junior","júnior","kinbox","salesforce")) else
            "Onboarding / Interno" if any(k in low for k in ("onboarding","worldpackers","scraper","banco de víde","recrutacis","kale")) else
            "Heaven Platform" if "heaven" in low else "Automatrix")
    return pessoa, proj
def rich(b):
    t = b.get("type"); v = b.get(t, {})
    rt = v.get("rich_text") if isinstance(v, dict) else None
    return "".join(x.get("plain_text","") for x in (rt or []))
def page_text(pid):
    try: data = api("GET", f"/v1/blocks/{pid}/children?page_size=100")
    except Exception: return ""
    out = []
    for b in data.get("results", []):
        t = b.get("type", ""); txt = rich(b)
        if t.startswith("heading"): out.append("## " + txt)
        elif t in ("bulleted_list_item","numbered_list_item","to_do"): out.append("- " + txt)
        elif t == "quote": out.append("> " + txt)
        elif t == "audio": out.append("🎙 *(áudio gravado no Notion)*")
        elif txt: out.append(txt)
    return "\n\n".join(out)

def main():
    data = json.load(open("data/calls.json"))
    have = {c.get("notion") for c in data["calls"] if c.get("notion")}
    have_ids = {c["id"] for c in data["calls"]}
    added = []
    # varredura recente ("") + buscas por termo (pega reuniões antigas em DBs por projeto)
    QUERIES = ["", "Call", "Reunião", "Reuniao", "Meeting", "Recording", "Chris", "Onboarding", "Demo"]
    searches = []
    for query in QUERIES:
        cursor = None
        for _ in range(4 if query == "" else 2):
            body = {"page_size": 100}
            if query: body["query"] = query
            else: body["sort"] = {"direction":"descending","timestamp":"last_edited_time"}
            if cursor: body["start_cursor"] = cursor
            try: res = api("POST", "/v1/search", body)
            except Exception as e: log(f"erro search '{query}': {e}"); break
            searches.append(res)
            cursor = res.get("next_cursor")
            if not res.get("has_more"): break
    for res in searches:
        for p in res.get("results", []):
            if p.get("object") != "page": continue
            url = p.get("url")
            if not url or url in have: continue
            name = title_of(p).strip()
            if not name or TASK_RE.search(name) or not MEET_RE.search(name): continue
            date = date_of(p)
            cid = "notion_" + date + "_" + slug(name)
            if cid in have_ids: continue
            pessoa, proj = derive(name)
            md = f"# {name}\n\n> **Gravado/transcrito no Notion** · {date}\n\n" + page_text(p["id"].replace("-",""))
            notes = f"library/notes/{cid}.md"
            os.makedirs("library/notes", exist_ok=True); open(notes, "w").write(md)
            data["calls"].append({"id":cid,"pessoa":pessoa,"title":name,"date":date,"projeto":proj,
                "assunto":["Notion"],"participantes":["Lucas F. N. Alves"]+([pessoa] if pessoa!="Automatrix" else []),
                "type":"notion","notion":url,"github":None,"driveVideoId":None,"sizeMB":None,
                "durationApprox":None,"geminiOk":True,"notes":notes,"transcript":None,"video":None,"status":"transcribed"})
            added.append((cid, url)); have.add(url); have_ids.add(cid)
            time.sleep(0.35)   # respeita rate-limit do Notion
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
