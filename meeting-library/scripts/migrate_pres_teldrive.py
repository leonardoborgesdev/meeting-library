#!/usr/bin/env python3
# migrate_pres_teldrive.py — sobe os 3 mp4 de apresentação pro Brazika Drive
# (Teldrive, /meeting-library) e atualiza data/presentations.json LOCAL:
#   - adiciona  "teldrive": "<fileId>"
#   - troca     "video": "/api/presentations/video?id=<pid>"
#
# NÃO mexe na prod (volume do Fly) — só prepara o JSON local pro deploy.
# Reaproveita o uploader idempotente de backup_media_teldrive.py.
# Idempotente: se o arquivo já está em data/teldrive.json, só reusa o fileId.
#
# Uso:  python3 scripts/migrate_pres_teldrive.py
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backup_media_teldrive as td

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
PRES_F = "data/presentations.json"
PRES_DIR = "library/presentations"

def log(*a): print("[migrate-pres]", *a, flush=True)

def main():
    pres = json.load(open(PRES_F))
    items = pres.get("presentations", [])
    if not items:
        sys.exit("nenhuma apresentação em " + PRES_F)

    token = td.mint_token()
    cfg = td.api("GET", "/users/config", token)
    channel = cfg["channelId"]
    log("canal", channel, "| bots:", len(cfg.get("bots", [])))
    if not cfg.get("bots"):
        sys.exit("sem bots no Teldrive — upload bloqueado. Add bots na UI primeiro.")
    td.ensure_folder(token)
    done = td.existing_names(token)
    log(f"{len(done)} arquivos já na pasta {td.FOLDER}")

    try: mapping = json.load(open(td.MAP_F))
    except Exception: mapping = {}

    up = skip = fail = 0
    for ent in items:
        pid = ent.get("id")
        vid = ent.get("video") or ""
        # nome esperado do mp4 no disco
        fname = os.path.basename(vid) if vid.endswith(".mp4") else f"{pid}.mp4"
        fpath = os.path.join(PRES_DIR, fname)
        if not os.path.isfile(fpath):
            log(f"  ✗ {pid}: mp4 não encontrado em {fpath} — pulando")
            fail += 1; continue

        fid = None
        # já mapeado?
        if fname in mapping and mapping[fname].get("fileId"):
            fid = mapping[fname]["fileId"]
            log(f"  = {fname} já no drive ({fid}) — reusando")
            skip += 1
        else:
            size = os.path.getsize(fpath)
            log(f"  → {fname} ({size//(1024*1024)}MB) pro drive...")
            t0 = time.time()
            try:
                fid, sz = td.upload_file(token, channel, fpath, fname)
                mapping[fname] = {"fileId": fid, "size": sz, "path": td.FOLDER, "pres": pid}
                json.dump(mapping, open(td.MAP_F, "w"), ensure_ascii=False, indent=2)
                up += 1
                log(f"    ✓ {fname} em {int(time.time()-t0)}s  id={fid}")
            except Exception as e:
                fail += 1
                log(f"    ✗ {fname} FALHOU: {str(e)[:160]}")
                continue

        # atualiza o card local
        ent["teldrive"] = fid
        ent["video"] = f"/api/presentations/video?id={pid}"

    json.dump(pres, open(PRES_F, "w"), ensure_ascii=False, indent=2)
    log(f"FIM — enviados={up} reusados={skip} falhas={fail}")
    log(f"presentations.json atualizado (teldrive + video proxy). Mapa: {td.MAP_F}")

if __name__ == "__main__":
    main()
