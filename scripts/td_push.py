#!/usr/bin/env python3
# td_push.py — sobe UM arquivo de mídia pro Brazika Drive (Teldrive) e registra
# o id no card (calls.json) + no mapa (data/teldrive.json). Roda no Fly (online),
# usa TD_TOKEN (secret, sem fly ssh/Postgres). Idempotente: pula se já tem id.
#
# Uso:  TD_TOKEN=... python3 scripts/td_push.py <call_id> <arquivo>
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backup_media_teldrive as td

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)

def set_card_field(cid, key, val):
    try: data = json.load(open("data/calls.json"))
    except Exception: return
    for c in data.get("calls", []):
        if c.get("id") == cid: c[key] = val
    json.dump(data, open("data/calls.json", "w"), ensure_ascii=False, indent=2)

def main():
    if len(sys.argv) < 3:
        sys.exit("uso: td_push.py <call_id> <arquivo>")
    cid, fpath = sys.argv[1], sys.argv[2]
    if not os.path.isfile(fpath):
        sys.exit(f"arquivo não existe: {fpath}")
    if not os.environ.get("TD_TOKEN"):
        print("[td_push] TD_TOKEN ausente — pulando backup pro drive"); return
    name = os.path.basename(fpath)

    try: mapping = json.load(open(td.MAP_F))
    except Exception: mapping = {}
    if name in mapping and mapping[name].get("fileId"):
        print(f"[td_push] {name} já no drive ({mapping[name]['fileId']})")
        set_card_field(cid, "teldrive", mapping[name]["fileId"]); return

    token = td.mint_token()  # lê TD_TOKEN do env
    cfg = td.api("GET", "/users/config", token)
    channel = cfg["channelId"]
    if not cfg.get("bots"):
        print("[td_push] sem bots no Teldrive — upload bloqueado"); return
    td.ensure_folder(token)
    t0 = time.time()
    print(f"[td_push] → {name} ({os.path.getsize(fpath)//(1024*1024)}MB) pro drive...")
    fid, sz = td.upload_file(token, channel, fpath, name)
    mapping[name] = {"fileId": fid, "size": sz, "path": td.FOLDER, "call": cid}
    json.dump(mapping, open(td.MAP_F, "w"), ensure_ascii=False, indent=2)
    set_card_field(cid, "teldrive", fid)
    print(f"[td_push] ✓ {name} em {int(time.time()-t0)}s  id={fid}")

if __name__ == "__main__":
    main()
