#!/usr/bin/env python3
# Roda DENTRO do vexa-lite. Conversa em tempo real (stream Redis -> Groq -> edge-tts -> paplay)
# e, quando a call termina, publica uma ANÁLISE no painel meet.automatrix-ai.com.
import os,sys,json,time,subprocess,urllib.request,urllib.parse,urllib.error,re,redis,http.cookiejar
NID=os.environ["NID"]; NATIVE=os.environ.get("NATIVE",""); GK=os.environ["GROQ_API_KEY"]; VKEY=os.environ["VEXA_API_KEY"]
PANEL=os.environ.get("PANEL_URL","https://meet.automatrix-ai.com"); PUSER=os.environ.get("PANEL_USER","automatrix"); PPW=os.environ.get("PANEL_PW","958462"); PHOST=os.environ.get("PANEL_HOST","meet.automatrix-ai.com")
# só dispara com o NOME claro (evita falar sozinho com sílabas soltas tipo "vex/bex")
WAKE_RE=re.compile(r"\b(v[eé]xa|b[eé]xa|veksa|beksa|becsa|vekissa|vex[ -]a|bex[ -]a)\b"); UA="curl/8.4.0"; COOLDOWN=7
FOCUS_KW=["foca","foco","focar","presta atenção","presta atencao","anota","anote","marca isso","marque","importante isso","grava isso"]
r=redis.Redis(host="127.0.0.1",port=6379,decode_responses=True)
ctx=[]; qa=[]; focus=[]; STATE={"sess":""}

PROVIDERS=[
 {"n":"cerebras","u":"https://api.cerebras.ai/v1/chat/completions","k":os.environ.get("CEREBRAS_API_KEY",""),"m":"gpt-oss-120b"},
 {"n":"groq","u":"https://api.groq.com/openai/v1/chat/completions","k":GK,"m":"llama-3.1-8b-instant"},
 {"n":"gemini","u":"https://generativelanguage.googleapis.com/v1beta/openai/chat/completions","k":os.environ.get("GEMINI_API_KEY",""),"m":"gemini-2.0-flash"},
]
def groq(messages,max_tokens=120):
    # rodízio com fallback: cerebras -> groq -> gemini (nunca cai)
    last=None
    for p in PROVIDERS:
        if not p["k"]: continue
        body=json.dumps({"model":p["m"],"temperature":0.3,"max_tokens":max_tokens,"messages":messages}).encode()
        try:
            req=urllib.request.Request(p["u"],data=body,headers={"Authorization":f"Bearer {p['k']}","Content-Type":"application/json","User-Agent":UA})
            with urllib.request.urlopen(req,timeout=25) as x:
                print(f"[llm] {p['n']} ok",flush=True)
                return json.load(x)["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[llm] {p['n']} falhou: {str(e)[:80]}",flush=True); last=e; continue
    raise last or RuntimeError("sem provedor LLM disponível")

def load_kb():
    try: return r.lrange("vexa:memory",0,-1)
    except Exception: return []
KB=load_kb()
def answer(q):
    kb="\n".join(KB)[:3500]
    return groq([{"role":"system","content":"Você é o Vexa, copiloto de voz numa reunião da Automatrix. Você CONHECE o histórico de reuniões abaixo. Responda em 1-2 frases curtas, diretas, PT-BR falado natural, sem markdown, com base no histórico e no contexto da call."},
                 {"role":"user","content":(f"Histórico de reuniões Automatrix:\n{kb}\n\n" if kb else "")+"Contexto da call atual: "+" ".join(ctx[-30:])+f"\n\nAlguém te chamou e disse: \"{q}\". Responda."}])

def speak(t):
    if os.environ.get("SPEAK_OFF"): return   # Realtime cuida da voz; aqui só análise/painel
    t=re.sub(r'["\\`$]'," ",t)
    subprocess.run(["sh","-lc",f'SRC=$(pactl get-default-source); SINK=$(echo "$SRC" | sed "s/virtual_mic/tts_sink/"); pactl set-sink-mute "$SINK" 0; pactl set-source-mute "$SRC" 0; python3 -m edge_tts --rate=+15% --voice pt-BR-AntonioNeural --text "{t}" --write-media /tmp/r.mp3 && ffmpeg -y -loglevel error -i /tmp/r.mp3 -ar 44100 -ac 2 /tmp/r.wav && paplay -d "$SINK" /tmp/r.wav'],check=False)

def vexa_status():
    try:
        req=urllib.request.Request(f"http://localhost:8056/meetings/{NID}",headers={"X-API-Key":VKEY})
        with urllib.request.urlopen(req,timeout=10) as x: return json.load(x).get("status")
    except Exception: return None

def push_panel():
    import glob
    full=" ".join(ctx); date=time.strftime("%Y-%m-%d")
    foco_txt="; ".join(f["pedido"] for f in focus)
    title=f"Vexa · {NATIVE or NID} · {date}"+(f" · 🎯 {foco_txt[:50]}" if foco_txt else "")
    auds=[]
    for _ in range(20):  # espera a gravação (master.webm) finalizar após a call
        auds=glob.glob(f"/var/lib/vexa/recordings/recordings/*/*/{STATE['sess']}/audio/master.webm") if STATE['sess'] else []
        if auds and os.path.getsize(auds[0])>2000: break
        time.sleep(3)
    # OPÇÃO A: tem áudio -> mp3 (toca em qqer browser) -> sobe -> espera transcrever -> completa card (audio+entendimento+falas)
    if auds:
        mp3="/tmp/vexa_up.mp3"
        subprocess.run(["sh","-lc",f'ffmpeg -y -loglevel error -i "{auds[0]}" -vn -ar 44100 -ac 2 "{mp3}"'],check=False)
        src=mp3 if (os.path.exists(mp3) and os.path.getsize(mp3)>2000) else auds[0]
        fn,ext=("vexa.mp3","mp3") if src==mp3 else ("vexa.webm","webm")
        try:
            sysmsg="Você analisa uma reunião. PT-BR markdown: resumo de 4-6 linhas do que foi tratado, depois '## Tópicos', '## Decisões', '## Ações' (bullets)."
            if foco_txt: sysmsg+=f" Inclua '## 🎯 Foco' detalhando bem: {foco_txt}."
            understanding=groq([{"role":"system","content":sysmsg},{"role":"user","content":"Transcrição da reunião:\n"+full[:9000]}],max_tokens=900)
        except Exception as e: understanding=f"(análise falhou: {e})"
        falas="\n".join(f"- **{x['t']}** — perguntaram: \"{x['q']}\" → **Vexa:** \"{x['a']}\"" for x in qa) or "_(o Vexa não foi chamado por voz nesta call)_"
        notes=f"# 🤖 Entendimento do Vexa sobre a call\n\n{understanding}\n\n## 🎤 Falas do Vexa (o que respondeu na call)\n{falas}\n"
        cj=http.cookiejar.CookieJar(); op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        try: op.open(urllib.request.Request(f"{PANEL}/api/login",data=json.dumps({"user":PUSER,"pw":PPW}).encode(),headers={"Content-Type":"application/json","Host":PHOST}),timeout=20)
        except Exception as e: print("[ctr] login painel falhou:",e,flush=True); return
        q=urllib.parse.urlencode({"filename":fn,"tipo":"audio","title":title,"date":date,"pessoa":"Vexa Bot","projeto":"Vexa Notetaker","ferramentas":"Vexa,Groq,Google Meet"})
        try:
            blob=open(src,"rb").read()
            cid=json.load(op.open(urllib.request.Request(f"{PANEL}/api/upload?{q}",data=blob,headers={"Content-Type":"application/octet-stream","Host":PHOST}),timeout=300)).get("id")
            print(f"[ctr] áudio enviado, cid={cid}",flush=True)
        except Exception as e: print("[ctr] upload falhou:",e,flush=True); cid=None
        if cid:
            card=None
            for _ in range(40):  # espera AssemblyAI (~4min)
                time.sleep(6)
                try:
                    cs=json.load(op.open(f"{PANEL}/data/calls.json",timeout=20)).get("calls",[])
                    card=next((c for c in cs if c.get("id")==cid),None)
                    if card and card.get("status")=="done": break
                except Exception: pass
            if not card: card={"id":cid,"date":date,"type":"audio","assunto":[],"ferramentas":["Vexa"]}
            card.update({"audio":f"/library/audio/{cid}.{ext}","notes":f"library/notes/{cid}.md","title":title,"pessoa":"Vexa Bot","projeto":"Vexa Notetaker","type":"audio","status":"done"})
            try:
                op.open(urllib.request.Request(f"{PANEL}/api/ingest",data=json.dumps({"card":card,"notes":notes}).encode(),headers={"Content-Type":"application/json","Host":PHOST}),timeout=30)
                print(f"[ctr] card COMPLETO: áudio({ext}) tocável + transcrição + entendimento + falas ({cid})",flush=True)
            except Exception as e: print("[ctr] ingest falhou:",e,flush=True)
        return
    # OPÇÃO B (fallback): sem áudio -> publica só a análise em texto
    if not full.strip(): print("[ctr] sem áudio e sem transcript, nada a publicar",flush=True); return
    try:
        sysmsg="Você analisa reuniões. Em PT-BR markdown: resumo 3-5 linhas, '## Tópicos', '## Decisões', '## Ações'."
        if foco_txt: sysmsg+=f" FOCO especial em: {foco_txt}. Dê seção '## 🎯 Foco' detalhada."
        summary=groq([{"role":"system","content":sysmsg},{"role":"user","content":"Transcrição:\n"+full[:9000]}],max_tokens=800)
    except Exception as e: summary=f"(resumo falhou: {e})"
    men="\n".join(f"- **{x['t']}** — \"{x['q']}\" → Vexa: \"{x['a']}\"" for x in qa) or "_(não mencionado)_"
    notes=f"# 🤖 Vexa — Análise\n\n{summary}\n\n## 🎤 Menções\n{men}\n\n## 📝 Transcrição\n{full}\n"
    card={"id":f"vexa_{date}_{NATIVE or NID}","title":title,"date":date,"pessoa":"Vexa Bot","projeto":"Vexa Notetaker","type":"audio","source":"vexa","status":"done","assunto":[],"ferramentas":["Vexa","Groq"],"transcript":None}
    try:
        cj=http.cookiejar.CookieJar(); op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        op.open(urllib.request.Request(f"{PANEL}/api/login",data=json.dumps({"user":PUSER,"pw":PPW}).encode(),headers={"Content-Type":"application/json","Host":PHOST}),timeout=20)
        op.open(urllib.request.Request(f"{PANEL}/api/ingest",data=json.dumps({"card":card,"notes":notes}).encode(),headers={"Content-Type":"application/json","Host":PHOST}),timeout=30)
        print(f"[ctr] análise (texto) no painel",flush=True)
    except Exception as e: print("[ctr] erro push painel:",e,flush=True)

def main():
    print(f"[ctr] meeting {NID} (native {NATIVE}) — conversa + análise no fim",flush=True)
    last="$"; lastans=0; seen=set(); lastcheck=time.time()
    while True:
        try:  # texto do cockpit (vexa:say) -> responde em voz, mesmo no modo grátis
            sv=r.lpop("vexa:say")
            if sv:
                a=answer(sv); print(f"[ctr] 💬 cockpit: {sv[:40]} -> {a}",flush=True); speak(a)
                it={"t":time.strftime("%H:%M"),"q":sv,"a":a}; qa.append(it)
                r.lpush(f"vexa:qa:{NID}",json.dumps(it,ensure_ascii=False)); r.ltrim(f"vexa:qa:{NID}",0,49)
        except Exception: pass
        try: res=r.xread({"transcription_segments":last},block=2000,count=20)
        except Exception as e: print("xread err",e,flush=True); time.sleep(1); res=None
        for _,entries in res or []:
            for eid,f in entries:
                last=eid
                try: d=json.loads(f.get("payload","{}"))
                except: continue
                if str(d.get("meeting_id"))!=NID: continue
                if d.get("uid"): STATE["sess"]=d.get("uid")
                for s in d.get("segments",[]):
                    sid=s.get("segment_id",""); txt=(s.get("text") or "").strip()
                    if not txt: continue
                    if sid not in seen: ctx.append(txt); seen.add(sid)
                    low=txt.lower()
                    if WAKE_RE.search(low) and (time.time()-lastans)>COOLDOWN:
                        lastans=time.time()
                        if any(k in low for k in FOCUS_KW):
                            # COMANDO DE FOCO: marca o ponto + contexto, confirma e destaca no relatório
                            foc={"t":time.strftime("%H:%M"),"pedido":txt,"contexto":" ".join(ctx[-6:])}
                            focus.append(foc); print(f"[ctr] 🎯 FOCO: {txt}",flush=True)
                            try: r.lpush(f"vexa:focus:{NID}",json.dumps(foc,ensure_ascii=False)); r.ltrim(f"vexa:focus:{NID}",0,49)
                            except Exception: pass
                            try:
                                tema=groq([{"role":"system","content":"Diga em no máx 12 palavras, PT-BR falado, que você vai focar no tema pedido. Sem markdown."},{"role":"user","content":f"O usuário pediu pra focar nisto: \"{txt}\". Confirme curto."}])
                                speak(tema)
                            except Exception: speak("Anotado, vou focar nisso e destacar na transcrição.")
                        else:
                            print(f"[ctr] menção: {txt}",flush=True)
                            try:
                                a=answer(txt); print(f"[ctr] VEXA: {a}",flush=True); speak(a)
                                item={"t":time.strftime("%H:%M"),"q":txt,"a":a}; qa.append(item)
                                try: r.lpush(f"vexa:qa:{NID}",json.dumps(item,ensure_ascii=False)); r.ltrim(f"vexa:qa:{NID}",0,49); r.set(f"vexa:native:{NID}",NATIVE)
                                except Exception: pass
                            except Exception as e: print("[ctr] erro:",e,flush=True)
                        lastans=time.time()
        if time.time()-lastcheck>30:
            lastcheck=time.time()
            if vexa_status() in ("completed","failed","stopping"):
                print("[ctr] call encerrada — publicando análise",flush=True); push_panel(); return

if __name__=="__main__": main()
