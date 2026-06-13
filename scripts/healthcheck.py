#!/usr/bin/env python3
# healthcheck.py — roda no container (sem Mac). Verifica se o backfill está REALMENTE
# funcionando: calls entrando, download/transcrição/frames/Supabase completos, fila andando.
# Escreve data/health.json (lido por /api/health + banner do app) e data/health.log.
# Push opcional no Telegram (env TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID).
import os, json, time, datetime, re, glob, subprocess, urllib.request, urllib.parse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

def jload(p, d):
    try: return json.load(open(p))
    except Exception: return d

def notify(text):
    tok = os.environ.get("TELEGRAM_BOT_TOKEN"); chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not tok or not chat: return
    try:
        data = urllib.parse.urlencode({"chat_id": chat, "text": text, "disable_web_page_preview": "true"}).encode()
        urllib.request.urlopen(f"https://api.telegram.org/bot{tok}/sendMessage", data=data, timeout=15)
    except Exception: pass

def main():
    calls = jload("data/calls.json", {"calls": []})["calls"]
    sb    = jload("data/supabase.json", {})
    prev  = jload("data/health.json", {})

    vids   = [c for c in calls if c.get("type", "video") == "video" and c.get("driveVideoId")]
    done   = [c for c in vids if c.get("transcript")]
    pend   = [c for c in vids if not c.get("transcript")]
    procing = [os.path.basename(p) for p in glob.glob("library/videos/*_raw.mp4")]

    # completude por call concluída: transcrição (volume) + walkthrough + frames no Supabase
    incomplete = []
    for c in done:
        cid = c["id"]; e = sb.get(cid, {})
        t_ok  = bool(c.get("transcript")) and os.path.exists(c["transcript"])
        wt_ok = bool(e.get("walkthrough")) or (c.get("walkthrough") and os.path.exists(c["walkthrough"]))
        fr_ok = bool(e.get("frames"))
        if not (t_ok and wt_ok and fr_ok):
            incomplete.append({"id": cid, "transcript": t_ok, "walkthrough": bool(wt_ok), "frames": fr_ok})

    # cota diária
    bf = jload("data/.backfill_day", {"date": "", "count": 0})
    today = datetime.date.today().isoformat()
    today_count = bf.get("count", 0) if bf.get("date") == today else 0
    daily_max = int(os.environ.get("POLL_DAILY_MAX", "6"))

    # última atividade (mtime do log do poller)
    last_mtime = 0
    for p in ("data/poll.cron.log", "data/poll.log", "data/process.log"):
        if os.path.exists(p): last_mtime = max(last_mtime, os.path.getmtime(p))
    mins_idle = round((time.time() - last_mtime) / 60) if last_mtime else None

    # erros recentes da AssemblyAI (últimas linhas do process.log)
    aai_err = 0
    try:
        tail = subprocess.run(["tail", "-n", "120", "data/process.log"], capture_output=True, text=True).stdout
        aai_err = len(re.findall(r"AAI falhou|submit AAI|upload AAI falhou|too many", tail, re.I))
    except Exception: pass

    # disco do volume
    disk_pct = None
    try:
        out = subprocess.run(["df", "-P", "/data"], capture_output=True, text=True).stdout.splitlines()
        disk_pct = int(out[-1].split()[4].rstrip("%"))
    except Exception: pass

    # progresso: comparou done com a checagem anterior
    prev_done = prev.get("done", 0)
    progressed = len(done) > prev_done

    # diagnóstico
    problems = []
    if incomplete:
        problems.append(f"{len(incomplete)} call(s) concluída(s) sem transcrição/frames completos")
    quota_full = today_count >= daily_max
    if pend and not quota_full and not procing and mins_idle is not None and mins_idle > 150:
        problems.append(f"sem atividade há {mins_idle}min com {len(pend)} na fila e cota do dia livre")
    if aai_err >= 2:
        problems.append(f"{aai_err} erro(s) recentes da AssemblyAI (possível cota)")
    if disk_pct is not None and disk_pct >= 90:
        problems.append(f"disco do volume em {disk_pct}%")

    status = "ok" if not problems else "warn"
    pct = round(len(done) / len(vids) * 100) if vids else 0

    health = {
        "ts": int(time.time()),
        "checked_at": datetime.datetime.now().strftime("%d/%m %H:%M"),
        "status": status,
        "total_videos": len(vids),
        "done": len(done),
        "pending": len(pend),
        "pct": pct,
        "processing": procing,
        "today": today_count, "daily_max": daily_max, "quota_full": quota_full,
        "incomplete": incomplete[:10],
        "incomplete_n": len(incomplete),
        "aai_errors": aai_err,
        "mins_idle": mins_idle,
        "disk_pct": disk_pct,
        "progressed_since_last": progressed,
        "problems": problems,
    }
    json.dump(health, open("data/health.json", "w"), ensure_ascii=False, indent=2)
    line = (f"[{health['checked_at']}] {status.upper()} · {len(done)}/{len(vids)} ({pct}%) "
            f"· fila {len(pend)} · hoje {today_count}/{daily_max} · idle {mins_idle}min "
            f"· incompletas {len(incomplete)} · aai_err {aai_err} · disco {disk_pct}%")
    open("data/health.log", "a").write(line + "\n")
    print(line)

    # push: alerta quando vira problema, + resumo 1x/dia
    last_status = prev.get("status")
    last_daily  = prev.get("daily_push_date")
    if status == "warn" and last_status != "warn":
        notify("⚠️ Meeting Library: " + "; ".join(problems) +
               f"\n{len(done)}/{len(vids)} ok · fila {len(pend)} · meet.brazika.online")
    elif status == "ok" and last_status == "warn":
        notify("✅ Meeting Library normalizou. " + line)
    if last_daily != today and datetime.datetime.now().hour >= 20:
        notify(f"📊 Meeting Library (resumo do dia)\n{line}\nmeet.brazika.online")
        health["daily_push_date"] = today
        json.dump(health, open("data/health.json", "w"), ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
