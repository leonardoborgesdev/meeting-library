#!/usr/bin/env python3
# auto_summary.py <call_id>
# Gera library/notes/<id>_resumo.md (Resumo + Tópicos + Próximas etapas + Apps) a partir da
# transcrição, usando um LLM local via OLLAMA_URL (ex http://localhost:11434). Sem LLM, sai sem fazer nada.
# Liga a nota na call (campo notes). Usado pelo poll_drive quando AUTO_SUMMARY=1.
import sys, os, json, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
OLLAMA = os.environ.get("OLLAMA_URL"); MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
if not OLLAMA:
    print("OLLAMA_URL não setado — pulando auto_summary"); sys.exit(0)
cid = sys.argv[1]
data = json.load(open("data/calls.json"))
c = next((x for x in data["calls"] if x["id"] == cid), None)
if not c or not c.get("transcript") or not os.path.exists(c["transcript"]):
    print("sem transcrição"); sys.exit(0)
txt = open(c["transcript"]).read()[:14000]
prompt = ("Você é um assistente que documenta calls. A partir da transcrição em português, gere um "
          "markdown em pt-BR com exatamente estas seções:\n"
          "## Resumo\n## Tópicos\n## Próximas etapas (use checklist '- [ ] ')\n## Aplicações/ferramentas citadas\n\n"
          "Seja específico e fiel ao que foi dito.\n\nTRANSCRIÇÃO:\n" + txt)
req = urllib.request.Request(OLLAMA.rstrip("/") + "/api/generate",
        data=json.dumps({"model": MODEL, "prompt": prompt, "stream": False}).encode(),
        headers={"Content-Type": "application/json"})
try:
    md = json.loads(urllib.request.urlopen(req, timeout=600).read()).get("response", "")
except Exception as e:
    print("erro LLM:", e); sys.exit(0)
if not md.strip(): sys.exit(0)
path = f"library/notes/{cid}_resumo.md"
open(path, "w").write(f"# Resumo automático — {c['title']}\n\n*Gerado por LLM ({MODEL}) a partir da transcrição.*\n\n{md}")
c["notes"] = path
json.dump(data, open("data/calls.json", "w"), ensure_ascii=False, indent=2)
print(f"✓ resumo automático: {path}")
