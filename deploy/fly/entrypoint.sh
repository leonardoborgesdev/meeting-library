#!/usr/bin/env bash
# entrypoint.sh — roda DENTRO do container Fly.
#  1) restaura estado no volume /data (1º boot) e aponta /app/data e /app/library pra lá
#  2) restaura o token do rclone (Drive) e as creds do Supabase a partir dos secrets
#  3) sobe o loop de auto-pull (a cada POLL_INTERVAL) em background
#  4) executa o servidor (porta 8009) em foreground
set -e
cd /app

# 1) estado persistente
mkdir -p /data/data /data/library
cp -rn /seed/data/.    /data/data/    2>/dev/null || true   # só copia o que falta (não apaga estado)
cp -rn /seed/library/. /data/library/ 2>/dev/null || true
rm -rf /app/data /app/library
ln -sfn /data/data    /app/data
ln -sfn /data/library /app/library
mkdir -p /app/library/videos /app/library/audio /app/library/transcripts /app/library/walkthroughs
# limpa downloads/áudios transitórios de um run interrompido (NOLOCAL: vídeo nunca deve persistir)
rm -f /app/library/videos/*.mp4 /app/library/audio/* /app/data/.poll.lock 2>/dev/null || true

# 2) token do Drive (persiste no volume p/ sobreviver ao refresh do OAuth)
if [ -n "${RCLONE_CONF_B64:-}" ] && [ ! -f /data/rclone.conf ]; then
  echo "$RCLONE_CONF_B64" | base64 -d > /data/rclone.conf
fi
export RCLONE_CONFIG=/data/rclone.conf
# creds Supabase via arquivo (compat com os scripts)
if [ -n "${SUPABASE_URL:-}" ]; then
  printf 'SUPABASE_URL=%s\nSUPABASE_KEY=%s\n' "$SUPABASE_URL" "$SUPABASE_KEY" > /app/data/.supabase.env
fi

# 3) auto-pull (cron interno) — lista o Drive, processa calls novas, sobe pro Supabase
(
  sleep 45
  while true; do
    echo "[$(date '+%F %T')] poll_drive…" >> /data/poll.cron.log
    python3 scripts/poll_drive.py >> /data/poll.cron.log 2>&1 || true
    sleep "${POLL_INTERVAL:-1200}"
  done
) &

# 3b) healthcheck (cron interno) — verifica entrada/transcrição/frames/fila e escreve data/health.json
(
  sleep 75
  while true; do
    python3 scripts/healthcheck.py >> /data/health.log 2>&1 || true
    sleep "${HEALTH_INTERVAL:-900}"
  done
) &

# 3c) notion-pull (cron interno) — ingere reuniões/calls do Notion como cards (antigas + novas)
(
  sleep 90
  while true; do
    echo "[$(date '+%F %T')] notion_poll…" >> /data/notion_poll.log
    python3 scripts/notion_poll.py >> /data/notion_poll.log 2>&1 || true
    sleep "${NOTION_INTERVAL:-1800}"
  done
) &

# 4) servidor
exec python3 scripts/server.py
