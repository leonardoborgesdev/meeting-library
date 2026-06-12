#!/usr/bin/env python3
# server.py — serve a Meeting Library E executa baixar/transcrever sob demanda.
# Uso:  ASSEMBLYAI_API_KEY=xxxx python3 scripts/server.py   (porta 8009)
import http.server, socketserver, subprocess, os, json, urllib.parse, threading
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
AAI = os.environ.get("ASSEMBLYAI_API_KEY", "")
RUNNING = {}   # call_id -> "transcribe" | "download"
CHECKLISTS = {"projetos": "data/checklist.json", "kinbox": "data/checklist_kinbox.json"}

def run_job(cid, action):
    RUNNING[cid] = action
    try:
        env = dict(os.environ)
        if action == "transcribe":
            env["ASSEMBLYAI_API_KEY"] = AAI
            subprocess.run(["bash", "scripts/process_calls.sh", cid], env=env)
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
    def do_POST(self):
        u = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(u.query)
        cid = (q.get("id") or [None])[0]
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
        if u.path == "/api/meta" and cid:
            body = self._read_body()
            try: meta = json.load(open("data/meta.json"))
            except Exception: meta = {}
            meta.setdefault(cid, {})
            for k in ("notion", "github"):
                if k in body: meta[cid][k] = body[k]
            json.dump(meta, open("data/meta.json", "w"), ensure_ascii=False, indent=2)
            return self._json({"ok": True, "meta": meta[cid]})
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
