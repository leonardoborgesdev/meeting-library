#!/usr/bin/env bash
# setup.sh — roda NO XEON. Instala deps, sobe o servidor (systemd) e o cron do auto-pull.
set -e
APP="$(cd "$(dirname "$0")/../.." && pwd)"
echo "== Meeting Library em $APP =="
sudo apt-get update -y
sudo apt-get install -y rclone jq ffmpeg python3 rsync curl
mkdir -p "$APP/data" "$APP/library/videos" "$APP/library/audio" "$APP/library/transcripts" "$APP/library/walkthroughs"

# --- systemd: servidor da app ---
sudo tee /etc/systemd/system/meeting-library.service >/dev/null <<EOF
[Unit]
Description=Meeting Library (server.py)
After=network.target
[Service]
WorkingDirectory=$APP
EnvironmentFile=$APP/deploy/xeon/meeting-library.env
ExecStart=/usr/bin/python3 scripts/server.py
Restart=always
[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now meeting-library
echo "✓ servidor ativo (systemctl status meeting-library)"

# --- cron: auto-pull de novas calls a cada 20 min ---
LINE="*/20 * * * * cd $APP && bash deploy/xeon/poll_cron.sh >> data/poll.log 2>&1"
( crontab -l 2>/dev/null | grep -v 'poll_cron.sh' ; echo "$LINE" ) | crontab -
echo "✓ cron do auto-pull instalado (*/20 min)"

# --- primeira varredura + regenera walkthroughs (formato Morfeu) ---
set -a; . "$APP/deploy/xeon/meeting-library.env"; [ -f "$APP/data/.supabase.env" ] && . "$APP/data/.supabase.env"; set +a
echo "== rodando primeira varredura do Drive =="
cd "$APP" && python3 scripts/poll_drive.py || true
echo "== setup concluído. App em http://<IP-tailscale-do-xeon>:${PORT:-8009} =="
