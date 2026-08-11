#!/usr/bin/env python3
# Sync data/ + library/ from your LIVE deployment (source of truth) into a local copy.
# Usage: SYNC_BASE_URL=https://your-domain SYNC_USER=... SYNC_PW=... python3 sync_live.py
import json, os, sys, urllib.request, http.cookiejar, ssl, re

BASE = os.environ.get("SYNC_BASE_URL", "http://localhost:8009")
ROOT = os.environ.get("SYNC_LOCAL_ROOT", "/opt/meeting-library")
USER, PW = os.environ.get("SYNC_USER", ""), os.environ.get("SYNC_PW", "")

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def login():
    body = json.dumps({"user": USER, "pw": PW}).encode()
    req = urllib.request.Request(BASE + "/api/login", data=body,
                                 headers={"Content-Type": "application/json"})
    r = opener.open(req, timeout=30)
    print("login:", r.read().decode())

def get(path):
    req = urllib.request.Request(BASE + path)
    return opener.open(req, timeout=120)

total_bytes = 0
ok = 0
fail = 0

def fetch_to(path, dest):
    global total_bytes, ok, fail
    try:
        r = get(path)
        if r.status != 200:
            print("  MISS", r.status, path); fail += 1; return False
        data = r.read()
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
        total_bytes += len(data); ok += 1
        return True
    except Exception as e:
        print("  ERR", path, str(e)[:80]); fail += 1; return False

def list_dir(path):
    # SimpleHTTPRequestHandler directory listing -> parse hrefs
    try:
        r = get(path)
        if r.status != 200:
            return []
        html = r.read().decode("utf-8", "replace")
    except Exception as e:
        print("  list ERR", path, str(e)[:80]); return []
    hrefs = re.findall(r'href="([^"]+)"', html)
    out = []
    for h in hrefs:
        if h in ("../", "/"): continue
        if h.startswith("http"): continue
        out.append(h)
    return out

login()

# 1) data/*.json (explicit list)
data_files = ["calls.json","meta.json","supabase.json","presentations.json",
              "users.json","sessions.json","checklist.json","health.json"]
print("=== data/ ===")
for fn in data_files:
    fetch_to(f"/data/{fn}", os.path.join(ROOT, "data", fn))

# 2) library subfolders — recursive directory walk
def walk(rel):
    # rel like "library/transcripts/"
    entries = list_dir("/" + rel)
    for e in entries:
        if e.endswith("/"):
            walk(rel + e)
        else:
            fetch_to("/" + rel + e, os.path.join(ROOT, rel + e))

for sub in ["library/transcripts/","library/notes/","library/walkthroughs/",
            "library/audio/","library/presentations/"]:
    print("===", sub, "===")
    walk(sub)

# 3) Also pull file paths referenced in calls.json (in case dir listing missed any)
print("=== calls.json referenced files ===")
try:
    calls = json.load(open(os.path.join(ROOT, "data", "calls.json")))["calls"]
    refs = set()
    for c in calls:
        for k in ("transcript","notes","walkthrough","frames_dir","audio"):
            v = c.get(k)
            if isinstance(v, str) and v.startswith("library/") and not v.endswith("/"):
                refs.add(v)
    for v in sorted(refs):
        dest = os.path.join(ROOT, v)
        if not os.path.exists(dest):
            fetch_to("/" + v, dest)
except Exception as e:
    print("calls ref ERR", str(e)[:120])

print(f"\nDONE ok={ok} fail={fail} total={total_bytes/1024/1024:.1f} MB")
