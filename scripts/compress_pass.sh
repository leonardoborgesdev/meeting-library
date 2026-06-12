#!/usr/bin/env bash
# compress_pass.sh — comprime os vídeos já baixados (passo separado, não bloqueia transcrição).
# Re-encoda cada library/videos/<id>.mp4 com h264_videotoolbox (hardware) e substitui no lugar.
# Marcador: library/videos/<id>.cmpdone  (pula os já comprimidos).
# Uso:  bash scripts/compress_pass.sh   (rode quando quiser, ex.: à noite)
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
VID="library/videos"; LOG="data/compress.log"
log(){ echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }
for f in "$VID"/*.mp4; do
  [ -e "$f" ] || continue
  case "$f" in *_raw.mp4) continue;; esac
  base="${f%.mp4}"
  [ -f "$base.cmpdone" ] && { log "✓ $(basename "$f") já comprimido"; continue; }
  before=$(du -h "$f"|cut -f1)
  log "⚙ comprimindo $(basename "$f") ($before)..."
  tmp="$base.cmp.mp4"
  if ffmpeg -nostdin -loglevel error -y -i "$f" \
       -c:v h264_videotoolbox -b:v 1500k -maxrate 2500k -bufsize 4000k \
       -c:a aac -b:a 96k "$tmp" </dev/null && [ -s "$tmp" ]; then
    mv "$tmp" "$f"; touch "$base.cmpdone"
    log "  ✓ $(basename "$f"): $before → $(du -h "$f"|cut -f1)"
  else
    rm -f "$tmp"; log "  ⚠ falhou $(basename "$f")"
  fi
done
log "Compressão finalizada."
