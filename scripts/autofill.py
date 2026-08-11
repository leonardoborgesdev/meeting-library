#!/usr/bin/env python3
# autofill.py — depois de transcrever, preenche por IA (Gemini) os campos do card
# que vierem EM BRANCO: pessoa, projeto, assunto[], ferramentas[], participantes[].
# Respeita o que o usuário já digitou (só completa o que falta). Online, usa
# GEMINI_API_KEY (já no env do Fly). Sem chave/erro → não altera nada.
#
# Uso:  GEMINI_API_KEY=... python3 scripts/autofill.py <call_id>
import os, sys, json, ssl, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
_SSL = ssl.create_default_context(); _SSL.check_hostname = False; _SSL.verify_mode = ssl.CERT_NONE

def main():
    cid = sys.argv[1] if len(sys.argv) > 1 else sys.exit("uso: autofill.py <call_id>")
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key: print("[autofill] sem GEMINI_API_KEY — pulando"); return
    data = json.load(open("data/calls.json"))
    card = next((c for c in data["calls"] if c.get("id") == cid), None)
    if not card: sys.exit(f"card {cid} não encontrado")
    tr = card.get("transcript")
    if not tr or not os.path.isfile(tr): print("[autofill] sem transcrição — pulando"); return
    txt = open(tr, encoding="utf-8", errors="ignore").read()[:18000]

    need = {
        "pessoa":   not card.get("pessoa"),
        "projeto":  not card.get("projeto"),
        "assunto":  not card.get("assunto"),
        "ferramentas": not card.get("ferramentas"),
        "participantes": not card.get("participantes"),
        "title":    not card.get("title"),
    }
    if not any(need.values()): print("[autofill] nada em branco — ok"); return

    prompt = (
        "Você organiza um catálogo de calls/reuniões de uma equipe. A partir da TRANSCRIÇÃO abaixo, "
        "extraia metadados objetivos: quem é a pessoa principal, o nome do projeto/cliente da call, "
        "um título curto, os tópicos discutidos, as ferramentas/apps citadas e os participantes.\n\n"
        f"TRANSCRIÇÃO:\n{txt}\n\n"
        'Responda APENAS JSON: {"pessoa":"nome principal","projeto":"um dos projetos","title":"título curto",'
        '"assunto":["tópico",...max5],"ferramentas":["ferramenta",...],"participantes":["nome",...]}')
    payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json",
                             "thinkingConfig": {"thinkingBudget": 0}}}).encode()
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    try:
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=60, context=_SSL) as r: gj = json.load(r)
        ans = json.loads(gj["candidates"][0]["content"]["parts"][0]["text"])
    except Exception as e:
        print("[autofill] Gemini falhou:", str(e)[:120]); return

    changed = []
    for k in ("pessoa", "projeto", "title"):
        if need[k] and ans.get(k): card[k] = ans[k]; changed.append(k)
    for k in ("assunto", "ferramentas", "participantes"):
        if need[k] and isinstance(ans.get(k), list) and ans[k]:
            card[k] = ans[k][:8]; changed.append(k)
    card["autofilled"] = True
    json.dump(data, open("data/calls.json", "w"), ensure_ascii=False, indent=2)
    print("[autofill] preenchido:", ", ".join(changed) or "nada")

if __name__ == "__main__":
    main()
