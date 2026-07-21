#!/usr/bin/env python3
"""Vexa Control — cockpit web (status dos bots, Q&A ao vivo, disparar/parar).
Roda no HOST da VPS :8060. Env: VEXA_API_KEY, CTRL_TOKEN (auth ?k=)."""
import os,json,re,subprocess,urllib.request,urllib.parse,urllib.error
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
VKEY=os.environ["VEXA_API_KEY"]; TOKEN=os.environ.get("CTRL_TOKEN","vexa")
VEXA="http://localhost:8056"
MEET_RE=re.compile(r"meet\.google\.com/([a-z]{3}-[a-z]{4}-[a-z]{3})")

def vexa(path,method="GET",body=None):
    req=urllib.request.Request(f"{VEXA}{path}",method=method,
        data=json.dumps(body).encode() if body else None,
        headers={"X-API-Key":VKEY,"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=15) as r: return json.load(r)
    except Exception as e: return {"error":str(e)}

def dexec(*a):
    try: return subprocess.run(["docker","exec","vexa-lite",*a],capture_output=True,text=True,timeout=15).stdout
    except Exception: return ""

def state():
    st=vexa("/bots/status").get("running_bots",[])
    bots=[]
    for b in st:
        nid=b.get("meeting_id_from_name"); native=b.get("native_meeting_id")
        qa=[]
        if nid:
            raw=dexec("redis-cli","LRANGE",f"vexa:qa:{nid}","0","8")
            for ln in raw.splitlines():
                ln=ln.strip()
                if ln.startswith("{"):
                    try: qa.append(json.loads(ln))
                    except: pass
        brain=subprocess.run(["systemctl","is-active",f"vexa-brain@{native}"],capture_output=True,text=True).stdout.strip()
        bots.append({"native":native,"nid":nid,"status":b.get("meeting_status"),"brain":brain,"qa":qa})
    rt_status=(dexec("redis-cli","GET","vexa:rt:status") or "").strip() or "offline"
    rt_mic=(dexec("redis-cli","GET","vexa:rt:mic") or "").strip() or "on"
    rt_qa=[]
    for ln in (dexec("redis-cli","LRANGE","vexa:rt:qa","0","6") or "").splitlines():
        ln=ln.strip()
        if ln.startswith("{"):
            try: rt_qa.append(json.loads(ln))
            except: pass
    kb_count=(dexec("redis-cli","HLEN","vexa:kb") or "0").strip()
    alert=(dexec("redis-cli","GET","vexa:rt:alert") or "").strip()
    return {"bots":bots,"rt":{"status":rt_status,"mic":rt_mic,"qa":rt_qa},"kb":kb_count,"alert":alert}

PAGE="""<!doctype html><html lang=pt><head><meta charset=utf-8><title>Vexa</title>
<meta name=viewport content="width=device-width,initial-scale=1,maximum-scale=1">
<link rel=preconnect href=https://fonts.googleapis.com><link rel=preconnect href=https://fonts.gstatic.com crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel=stylesheet>
<style>
:root{--bg:#0e0f14;--card:#171922;--card2:#1f2230;--line:#2a2e3d;--txt:#e7e9f0;--mut:#8b90a6;--acc:#7c5cff;--acc2:#9b85ff;--ok:#2fbf71;--bad:#ff5d6c}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--txt);margin:0;padding:0 0 40px;line-height:1.45}
.wrap{max-width:680px;margin:0 auto;padding:0 14px}
header{position:sticky;top:0;z-index:9;background:rgba(14,15,20,.85);backdrop-filter:blur(12px);border-bottom:1px solid var(--line);padding:13px 0;margin-bottom:14px}
header .wrap{display:flex;align-items:center;gap:10px}
.logo{width:34px;height:34px;border-radius:10px;background:linear-gradient(135deg,var(--acc),var(--acc2));display:grid;place-items:center;font-size:18px}
.brand{font-weight:800;font-size:17px;letter-spacing:-.3px}.brand small{display:block;font-weight:500;font-size:11px;color:var(--mut)}
.dot{width:9px;height:9px;border-radius:50%;background:var(--bad);box-shadow:0 0 0 0 rgba(47,191,113,.5)}
.dot.on{background:var(--ok);animation:pulse 2s infinite}@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(47,191,113,.5)}70%{box-shadow:0 0 0 7px rgba(47,191,113,0)}}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px;margin:12px 0}
.hero{background:linear-gradient(160deg,#1c1830,#171922);border-color:#2e2848}
.lbl{font-size:12px;font-weight:600;color:var(--mut);text-transform:uppercase;letter-spacing:.5px;margin-bottom:10px}
.row{display:flex;gap:8px;align-items:center}
input[type=text],input:not([type]){flex:1;font-family:inherit;font-size:15px;padding:13px 14px;border-radius:12px;border:1px solid var(--line);background:#0c0d12;color:var(--txt);outline:none;width:100%}
input:focus{border-color:var(--acc)}
button{font-family:inherit;font-size:14px;font-weight:600;padding:13px 16px;border-radius:12px;border:0;background:var(--acc);color:#fff;cursor:pointer;transition:.15s;white-space:nowrap}
button:active{transform:scale(.96)}button.ghost{background:var(--card2);color:var(--txt)}button.red{background:#33222a;color:var(--bad)}
.pills{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.pill{display:flex;align-items:center;gap:6px;background:var(--card2);border:1px solid var(--line);border-radius:999px;padding:7px 12px;font-size:12.5px;font-weight:500}
.pill b{font-weight:700}.pill .d{width:7px;height:7px;border-radius:50%;background:var(--mut)}.pill .d.on{background:var(--ok)}.pill .d.off{background:var(--bad)}
.switch{margin-left:auto;display:flex;align-items:center;gap:8px;font-size:12.5px;color:var(--mut);cursor:pointer}
.tog{width:42px;height:24px;border-radius:999px;background:#3a2030;position:relative;transition:.2s}.tog.on{background:var(--acc)}
.tog i{position:absolute;top:3px;left:3px;width:18px;height:18px;border-radius:50%;background:#fff;transition:.2s}.tog.on i{left:21px}
.feed{max-height:300px;overflow:auto}
.msg{background:var(--card2);border-radius:12px;padding:10px 12px;margin:8px 0;font-size:14px}
.msg .t{font-size:11px;color:var(--mut);margin-bottom:3px}.msg.you{border-left:3px solid var(--mut)}.msg.vx{border-left:3px solid var(--acc)}
.alert{background:#3a1f24;border:1px solid #5a2630;color:#ffb3bb;border-radius:12px;padding:11px 14px;font-size:13.5px;font-weight:500;margin:12px 0}
.det{cursor:pointer;user-select:none;font-size:13px;color:var(--mut);font-weight:600}
.empty{color:var(--mut);font-size:13.5px;text-align:center;padding:14px}
a.unstyled{color:var(--acc2);text-decoration:none}
</style></head>
<body>
<header><div class=wrap><div class=logo>🤖</div><div class=brand>Vexa <small>copiloto de voz · ao vivo</small></div><div id=dot class=dot style=margin-left:auto></div></div></header>
<div class=wrap>
<div id=alert></div>
<div class="card hero">
  <div class=row style=margin-bottom:10px><div class=lbl style=margin:0>💬 Fala com o Vexa</div>
    <div class=switch onclick=togmic()>escuta<div id=tog class=tog><i></i></div></div></div>
  <div class=row><input id=say placeholder="escreve e ele FALA na call…" onkeydown="if(event.key=='Enter')sendsay()">
    <button onclick=sendsay()>Enviar 🔊</button></div>
  <div class=pills>
    <div class=pill><div id=pdot class=d></div> Voz <b id=pvoz>—</b></div>
    <div class=pill>🎤 Bot <b id=pbot>—</b></div>
    <div class=pill>🧠 Sabe <b id=pkb>—</b> calls</div>
  </div>
</div>
<div class=card><div class=lbl>🔊 Conversa ao vivo</div><div id=feed class=feed></div></div>
<div class=card><div class=det onclick="var e=document.getElementById('dbox');e.style.display=e.style.display=='none'?'block':'none'">➕ Entrar numa call manualmente</div>
  <div id=dbox style=display:none;margin-top:12px><div class=row><input id=url placeholder="https://meet.google.com/xxx-xxxx-xxx"><button onclick=disp()>Entrar</button></div><div id=msg class=empty style=text-align:left></div></div></div>
<div id=bots></div>
</div>
<script>const K=new URLSearchParams(location.search).get('k')||'';
function esc(s){return (s||'').replace(/[<>&]/g,c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]))}
async function sendsay(){let i=document.getElementById('say');if(!i.value)return;let v=i.value;i.value='';await fetch('/api/say?k='+K,{method:'POST',body:JSON.stringify({text:v})});}
async function togmic(){await fetch('/api/mic?k='+K,{method:'POST',body:JSON.stringify({})});setTimeout(load,400);}
async function disp(){let u=document.getElementById('url').value;document.getElementById('msg').innerText='disparando…';let r=await fetch('/api/dispatch?k='+K,{method:'POST',body:JSON.stringify({url:u})});let d=await r.json();document.getElementById('msg').innerText=d.ok?'✅ entrando na call':('erro: '+(d.error||''));load();}
async function stop(n){await fetch('/api/stop?k='+K,{method:'POST',body:JSON.stringify({native:n})});load();}
async function load(){let d;try{d=await (await fetch('/api/state?k='+K)).json()}catch(e){return}
let rt=d.rt||{},on=rt.status=='online';
document.getElementById('dot').className='dot'+(on?' on':'');
document.getElementById('pdot').className='d'+(on?' on':' off');
document.getElementById('pvoz').innerText=on?'online':'off';
document.getElementById('pkb').innerText=d.kb||'0';
document.getElementById('tog').className='tog'+(rt.mic!='off'?' on':'');
let bot=(d.bots||[]).find(b=>b.status=='active');document.getElementById('pbot').innerText=bot?'na call':'—';
document.getElementById('alert').innerHTML=d.alert?`<div class=alert>⚠️ ${esc(d.alert)}</div>`:'';
let f='';for(const q of (rt.qa||[]))f+=`<div class="msg vx"><div class=t>${q.t} · Vexa</div>${esc(q.a)}</div>`;
for(const b of (d.bots||[]))for(const q of (b.qa||[]))f+=`<div class="msg you"><div class=t>${q.t} · alguém</div>${esc(q.q)}</div>`;
document.getElementById('feed').innerHTML=f||'<div class=empty>Sem conversa ainda. Manda algo acima ☝️</div>';
let h='';for(const b of (d.bots||[])){let cls=b.status=='active';
h+=`<div class=card><div class=row><b>${b.native}</b><span class=pill style=margin-left:auto><div class="d ${cls?'on':'off'}"></div>${b.status||'?'}</span><button class=red onclick="stop('${b.native}')">Parar</button></div></div>`}
document.getElementById('bots').innerHTML=h;}
load();setInterval(load,3000);</script></body></html>"""

class H(BaseHTTPRequestHandler):
    def _auth(self):
        q=urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        return (q.get("k") or [""])[0]==TOKEN
    def _send(self,code,body,ct="application/json"):
        b=body.encode() if isinstance(body,str) else json.dumps(body).encode()
        self.send_response(code);self.send_header("Content-Type",ct);self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def log_message(self,*a): pass
    def do_GET(self):
        p=urllib.parse.urlparse(self.path).path
        if p=="/" :
            if not self._auth(): return self._send(401,"<h3>token? use ?k=...</h3>","text/html")
            return self._send(200,PAGE,"text/html")
        if p=="/api/state":
            if not self._auth(): return self._send(401,{"error":"auth"})
            return self._send(200,state())
        self._send(404,{"error":"nf"})
    def do_POST(self):
        if not self._auth(): return self._send(401,{"error":"auth"})
        p=urllib.parse.urlparse(self.path).path
        ln=int(self.headers.get("Content-Length",0) or 0); body=json.loads(self.rfile.read(ln) or "{}")
        if p=="/api/dispatch":
            m=MEET_RE.search(body.get("url",""));
            if not m: return self._send(200,{"ok":False,"error":"link inválido"})
            code=m.group(1)
            res=vexa("/bots","POST",{"platform":"google_meet","native_meeting_id":code,"meeting_url":body["url"],"bot_name":"Vexa Notetaker","language":"pt","recording_enabled":True,"transcribe_enabled":True,"authenticated":True})
            subprocess.run(["systemctl","start",f"vexa-brain@{code}"])
            return self._send(200,{"ok":"error" not in res,"error":res.get("error")})
        if p=="/api/stop":
            n=body.get("native"); vexa(f"/bots/google_meet/{n}","DELETE"); subprocess.run(["systemctl","stop",f"vexa-brain@{n}"])
            return self._send(200,{"ok":True})
        if p=="/api/say":
            txt=(body.get("text") or "").strip()
            if txt:
                # realtime (se ligado) E pipeline grátis — quem estiver rodando responde
                subprocess.run(["docker","exec","vexa-lite","redis-cli","LPUSH","vexa:rt:cmd",json.dumps({"type":"say","text":txt})])
                subprocess.run(["docker","exec","vexa-lite","redis-cli","LPUSH","vexa:say",txt])
            return self._send(200,{"ok":True})
        if p=="/api/mic":
            cur=(dexec("redis-cli","GET","vexa:rt:mic") or "on").strip()
            newon=(cur=="off")
            subprocess.run(["docker","exec","vexa-lite","redis-cli","LPUSH","vexa:rt:cmd",json.dumps({"type":"mic","on":newon})])
            return self._send(200,{"ok":True,"mic":"on" if newon else "off"})
        self._send(404,{"error":"nf"})

if __name__=="__main__":
    ThreadingHTTPServer(("0.0.0.0",8060),H).serve_forever()
