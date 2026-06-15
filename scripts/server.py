#!/usr/bin/env python3
# server.py — serve a Meeting Library E executa baixar/transcrever sob demanda.
# Uso:  ASSEMBLYAI_API_KEY=xxxx python3 scripts/server.py   (porta 8009)
import http.server, socketserver, subprocess, os, json, urllib.parse, threading, hashlib, secrets
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
AAI = os.environ.get("ASSEMBLYAI_API_KEY", "")
RUNNING = {}   # call_id -> "transcribe" | "download"
CHECKLISTS = {"projetos": "data/checklist.json", "kinbox": "data/checklist_kinbox.json",
              "brazika": "data/checklist_brazika.json"}

# ── auth (login/registro) ──
AUTH_SALT   = os.environ.get("AUTH_SALT", "ml-2026-automatrix")
INVITE_CODE = os.environ.get("INVITE_CODE", "958462")
USERS_F = "data/users.json"; SESS_F = "data/sessions.json"
def _hash(u, p): return hashlib.sha256(f"{u}:{p}:{AUTH_SALT}".encode()).hexdigest()
def load_users():
    try: return json.load(open(USERS_F))
    except Exception:
        u = {"automatrix": _hash("automatrix", "958462")}   # conta padrão
        json.dump(u, open(USERS_F, "w")); return u
def load_sess():
    try: return json.load(open(SESS_F))
    except Exception: return {}
def save_sess(s):
    try: json.dump(s, open(SESS_F, "w"))
    except Exception: pass
load_users()  # garante a conta padrão no boot

def run_job(cid, action):
    RUNNING[cid] = action
    try:
        env = dict(os.environ)
        if action == "transcribe":
            env["ASSEMBLYAI_API_KEY"] = AAI
            subprocess.run(["bash", "scripts/process_calls.sh", cid], env=env)
        elif action == "process":   # upload manual: pipeline + auto-preenche por IA
            env["ASSEMBLYAI_API_KEY"] = AAI
            subprocess.run(["bash", "scripts/process_calls.sh", cid], env=env)
            subprocess.run(["python3", "scripts/autofill.py", cid], env=env)
        elif action == "download":
            subprocess.run(["bash", "scripts/download_one.sh", cid], env=env)
    finally:
        RUNNING.pop(cid, None)

class H(http.server.SimpleHTTPRequestHandler):
    def _json(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers(); self.wfile.write(b)
    def _read_body(self):
        n = int(self.headers.get("Content-Length", 0) or 0)
        try: return json.loads(self.rfile.read(n) or b"{}")
        except Exception: return {}
    def _token(self):
        for part in (self.headers.get("Cookie", "") or "").split(";"):
            part = part.strip()
            if part.startswith("mlsess="): return part[7:]
        return None
    def _user(self):
        t = self._token()
        return load_sess().get(t) if t else None
    def _set_cookie(self, ok_obj, token=None, clear=False):
        b = json.dumps(ok_obj).encode()
        self.send_response(200)
        if clear: self.send_header("Set-Cookie", "mlsess=; Path=/; Max-Age=0")
        elif token: self.send_header("Set-Cookie", f"mlsess={token}; Path=/; Max-Age=2592000; HttpOnly; SameSite=Lax")
        self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b)))
        self.end_headers(); self.wfile.write(b)
    def do_POST(self):
        u = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(u.query)
        cid = (q.get("id") or [None])[0]
        # ── auth pública ──
        if u.path == "/api/login":
            b = self._read_body(); user = (b.get("user") or "").strip(); pw = b.get("pw") or ""
            if load_users().get(user) == _hash(user, pw):
                tok = secrets.token_hex(24); s = load_sess(); s[tok] = user; save_sess(s)
                return self._set_cookie({"ok": True, "user": user}, token=tok)
            return self._json({"ok": False, "error": "Usuário ou senha inválidos"}, 401)
        if u.path == "/api/register":
            b = self._read_body(); user = (b.get("user") or "").strip(); pw = b.get("pw") or ""; code = b.get("code") or ""
            if code != INVITE_CODE: return self._json({"ok": False, "error": "Código de convite inválido"}, 403)
            if not user or not pw: return self._json({"ok": False, "error": "Preencha usuário e senha"}, 400)
            users = load_users()
            if user in users: return self._json({"ok": False, "error": "Usuário já existe"}, 409)
            users[user] = _hash(user, pw); json.dump(users, open(USERS_F, "w"))
            tok = secrets.token_hex(24); s = load_sess(); s[tok] = user; save_sess(s)
            return self._set_cookie({"ok": True, "user": user}, token=tok)
        if u.path == "/api/logout":
            t = self._token(); s = load_sess(); s.pop(t, None); save_sess(s)
            return self._set_cookie({"ok": True}, clear=True)
        # ── daqui pra baixo exige login ──
        if not self._user(): return self._json({"ok": False, "error": "auth"}, 401)
        if u.path == "/api/check":
            item = (q.get("item") or [None])[0]
            clkey = (q.get("cl") or ["projetos"])[0]
            fn = CHECKLISTS.get(clkey, "data/checklist.json")
            if not item: return self._json({"ok": False}, 400)
            try: cl = json.load(open(fn))
            except Exception: return self._json({"ok": False}, 500)
            found = None
            for g in cl.get("groups", []):
                for t in g.get("tasks", []):
                    if t.get("id") == item:
                        t["done"] = not t.get("done", False); found = t["done"]
            if found is None: return self._json({"ok": False, "msg": "item não encontrado"})
            json.dump(cl, open(fn, "w"), ensure_ascii=False, indent=2)
            return self._json({"ok": True, "done": found})
        if u.path == "/api/chat":
            b = self._read_body(); q = (b.get("q") or "").strip()
            key = os.environ.get("GEMINI_API_KEY", "")
            if not key: return self._json({"ok": False, "fallback": True})
            if not q: return self._json({"ok": False, "error": "vazio"}, 400)
            try:
                import urllib.request as _u
                calls = json.load(open("data/calls.json"))["calls"]
                try: meta = json.load(open("data/meta.json"))
                except Exception: meta = {}
                lines = []
                for c in calls:
                    m = meta.get(c["id"], {})
                    lines.append(" ┃ ".join([c["id"], c.get("date",""), c.get("pessoa",""),
                        c.get("projeto",""), (c.get("title","") or "")[:70],
                        ",".join(c.get("assunto",[])[:5]), c.get("type","video"),
                        ("notion" if m.get("notion") else ""), ("github" if m.get("github") else ""),
                        ("transcrita" if c.get("transcript") else "")]))
                ctx = "\n".join(lines)
                prompt = ("Você é o assistente da Meeting Library (catálogo de calls da Automatrix). "
                    "Cada linha do catálogo: id ┃ data ┃ pessoa ┃ projeto ┃ título ┃ tópicos ┃ tipo ┃ notion ┃ github ┃ transcrita.\n\n"
                    f"CATÁLOGO:\n{ctx}\n\nPERGUNTA DO USUÁRIO: {q}\n\n"
                    "Responda em PT-BR, curto e direto. Use as datas/projetos/pessoas do catálogo. "
                    "Liste os ids das calls realmente relevantes (no máximo 12). "
                    'Responda APENAS JSON: {"answer":"texto curto e útil","ids":["id",...]}')
                payload = json.dumps({"contents":[{"parts":[{"text":prompt}]}],
                    "generationConfig":{"temperature":0.3,"responseMimeType":"application/json",
                        "thinkingConfig":{"thinkingBudget":0}}}).encode()
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{os.environ.get('GEMINI_MODEL','gemini-2.5-flash')}:generateContent?key={key}"
                req = _u.Request(url, data=payload, headers={"Content-Type":"application/json"}, method="POST")
                with _u.urlopen(req, timeout=45) as r: gj = json.load(r)
                txt = gj["candidates"][0]["content"]["parts"][0]["text"]
                ans = json.loads(txt)
                return self._json({"ok": True, "answer": ans.get("answer",""), "ids": ans.get("ids",[])})
            except Exception as e:
                return self._json({"ok": False, "fallback": True, "error": str(e)[:120]})
        if u.path == "/api/ingest":
            b = self._read_body(); card = b.get("card"); notes = b.get("notes", "")
            if not card or not card.get("id"): return self._json({"ok": False, "error": "card inválido"}, 400)
            if card.get("notes") and notes:
                os.makedirs(os.path.dirname(card["notes"]), exist_ok=True)
                open(card["notes"], "w").write(notes)
            data = json.load(open("data/calls.json"))
            data["calls"] = [c for c in data["calls"] if c.get("id") != card["id"]] + [card]
            json.dump(data, open("data/calls.json", "w"), ensure_ascii=False, indent=2)
            if card.get("notion"):
                try: meta = json.load(open("data/meta.json"))
                except Exception: meta = {}
                meta.setdefault(card["id"], {})["notion"] = card["notion"]
                json.dump(meta, open("data/meta.json", "w"), ensure_ascii=False, indent=2)
            return self._json({"ok": True})
        if u.path == "/api/meta" and cid:
            body = self._read_body()
            try: meta = json.load(open("data/meta.json"))
            except Exception: meta = {}
            meta.setdefault(cid, {})
            for k in ("notion", "github"):
                if k in body: meta[cid][k] = body[k]
            json.dump(meta, open("data/meta.json", "w"), ensure_ascii=False, indent=2)
            return self._json({"ok": True, "meta": meta[cid]})
        if u.path == "/api/upload":
            import re as _re, time as _t
            filename = (q.get("filename") or ["upload"])[0]
            tipo = (q.get("tipo") or ["video"])[0]
            tipo = "audio" if tipo == "audio" else "video"
            title = (q.get("title") or [""])[0].strip()
            base = title or os.path.splitext(filename)[0]
            sl = _re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")[:48] or "gravacao"
            date = (q.get("date") or [_t.strftime("%Y-%m-%d")])[0]
            cid = f"up_{date}_{sl}_{secrets.token_hex(3)}"
            ext = (os.path.splitext(filename)[1].lower().lstrip(".") or ("mp3" if tipo == "audio" else "mp4"))
            if tipo == "audio":
                os.makedirs("library/audio", exist_ok=True); dest = f"library/audio/{cid}.{ext}"
            else:
                os.makedirs("library/videos", exist_ok=True); dest = f"library/videos/{cid}_raw.mp4"
            n = int(self.headers.get("Content-Length", 0) or 0)
            if n <= 0: return self._json({"ok": False, "error": "arquivo vazio"}, 400)
            tmp = dest + ".part"; remaining = n
            try:
                with open(tmp, "wb") as fh:
                    while remaining > 0:
                        chunk = self.rfile.read(min(1 << 20, remaining))
                        if not chunk: break
                        fh.write(chunk); remaining -= len(chunk)
                os.replace(tmp, dest)
            except Exception as e:
                try: os.remove(tmp)
                except Exception: pass
                return self._json({"ok": False, "error": f"upload falhou: {str(e)[:120]}"}, 500)
            ferr = [t.strip() for t in (q.get("ferramentas") or [""])[0].split(",") if t.strip()]
            card = {"id": cid, "pessoa": (q.get("pessoa") or [""])[0].strip(), "title": base,
                    "date": date, "projeto": (q.get("projeto") or [""])[0].strip(),
                    "assunto": [], "ferramentas": ferr, "participantes": [], "type": tipo,
                    "sizeMB": round(n / 1048576), "uploadedBy": self._user(), "source": "upload",
                    "status": "processing", "transcript": None, "video": None}
            data = json.load(open("data/calls.json"))
            data["calls"] = [c for c in data["calls"] if c.get("id") != cid] + [card]
            json.dump(data, open("data/calls.json", "w"), ensure_ascii=False, indent=2)
            if not AAI:
                return self._json({"ok": True, "id": cid, "warn": "salvo, mas sem ASSEMBLYAI_API_KEY p/ transcrever"})
            threading.Thread(target=run_job, args=(cid, "process"), daemon=True).start()
            return self._json({"ok": True, "id": cid})
        if u.path in ("/api/transcribe", "/api/download") and cid:
            if cid in RUNNING:
                return self._json({"ok": False, "msg": "já em andamento"})
            act = "transcribe" if u.path.endswith("transcribe") else "download"
            if act == "transcribe" and not AAI:
                return self._json({"ok": False, "msg": "sem ASSEMBLYAI_API_KEY no servidor"})
            threading.Thread(target=run_job, args=(cid, act), daemon=True).start()
            return self._json({"ok": True, "action": act})
        self._json({"ok": False}, 404)
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        # rotas públicas de auth
        if path == "/api/me":
            return self._json({"user": self._user()})
        if path in ("/login", "/login.html"):
            try:
                b = open("login.html", "rb").read()
                self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b); return
            except Exception: return self._json({"error": "login.html ausente"}, 500)
        # tudo o resto exige login
        if not self._user():
            if path.startswith("/api/"): return self._json({"ok": False, "error": "auth"}, 401)
            self.send_response(302); self.send_header("Location", "/login"); self.end_headers(); return
        if self.path.startswith("/api/health"):
            try: return self._json(json.load(open("data/health.json")))
            except Exception: return self._json({"status": "unknown", "problems": ["healthcheck ainda não rodou"]})
        if self.path.startswith("/api/status"):
            try:
                with open("data/calls.json") as f: data = json.load(f)
                try: meta = json.load(open("data/meta.json"))
                except Exception: meta = {}
                try: sb = json.load(open("data/supabase.json"))
                except Exception: sb = {}
                cls = {}
                for k, fn in CHECKLISTS.items():
                    try: cls[k] = json.load(open(fn))
                    except Exception: pass
                return self._json({"calls": data["calls"], "running": RUNNING, "meta": meta,
                                   "supabase": sb, "checklist": cls.get("projetos", {}), "checklists": cls})
            except Exception as e:
                return self._json({"error": str(e)}, 500)
        return super().do_GET()
    def log_message(self, *a): pass

socketserver.ThreadingTCPServer.allow_reuse_address = True
HOST = os.environ.get("HOST", "127.0.0.1"); PORT = int(os.environ.get("PORT", "8009"))
with socketserver.ThreadingTCPServer((HOST, PORT), H) as s:
    print(f"Meeting Library em http://{HOST}:{PORT}  (AAI={'ok' if AAI else 'OFF'})")
    s.serve_forever()
