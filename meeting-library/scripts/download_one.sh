#!/usr/bin/env bash
# download_one.sh <call_id> — baixa só o vídeo de UMA call (sem transcrever).
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
ID="$1"; VID="library/videos"; LOG="data/process.log"; mkdir -p "$VID"
FID=$(jq -r --arg id "$ID" '.calls[]|select(.id==$id)|.driveVideoId' data/calls.json)
[ -z "$FID" ] && { echo "id não encontrado"; exit 1; }
echo "[$(date '+%H:%M:%S')] ⬇ baixando $ID..." | tee -a "$LOG"
rclone backend copyid gdrive: "$FID" "$VID/$ID.mp4" </dev/null 2>>"$LOG"
if [ -s "$VID/$ID.mp4" ]; then
  tmp=$(mktemp); jq --arg id "$ID" --arg v "$VID/$ID.mp4" \
    '(.calls[]|select(.id==$id)) |= (.video=$v|.status=(if .transcript then "done" else "downloaded" end))' \
    data/calls.json > "$tmp" && mv "$tmp" data/calls.json
  echo "[$(date '+%H:%M:%S')] ✓ baixado $ID ($(du -h "$VID/$ID.mp4"|cut -f1))" | tee -a "$LOG"
else echo "[$(date '+%H:%M:%S')] ❌ falhou $ID" | tee -a "$LOG"; fi
