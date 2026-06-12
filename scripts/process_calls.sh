#!/usr/bin/env bash
# =============================================================================
# process_calls.sh — pipeline das calls (Leonardo · Nicolli · Lucas)
# Ordem: baixa (rclone) -> extrai áudio -> TRANSCREVE -> comprime (hardware).
# Transcrição: AssemblyAI (pt-BR + quem-fala) se ASSEMBLYAI_API_KEY; senão whisper.
# Compressão: h264_videotoolbox (hardware do Mac, rápido).
# Pré-req (no Terminal real): rclone config reconnect gdrive:
#   ASSEMBLYAI_API_KEY=xxx bash scripts/process_calls.sh [call_id]
# =============================================================================
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
REMOTE="gdrive:"; AAI="${ASSEMBLYAI_API_KEY:-}"
MODEL="${WHISPER_MODEL:-$HOME/whisper-models/ggml-medium.bin}"
MODEL_SMALL="$HOME/whisper-models/ggml-small.bin"
WHISPER="$(command -v whisper-cli || echo /usr/local/bin/whisper-cli)"
VID="library/videos"; AUD="library/audio"; TR="library/transcripts"
mkdir -p "$VID" "$AUD" "$TR"; LOG="data/process.log"
log(){ echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }

rclone about "$REMOTE" >/dev/null 2>&1 || { echo "❌ rclone config reconnect gdrive:"; exit 1; }
log "rclone OK"; [ -n "$AAI" ] && log "transcrição = AssemblyAI" || log "transcrição = whisper local"

set_field(){ # $1=id $2=key $3=value  (atualiza manifesto)
  local tmp; tmp=$(mktemp)
  jq --arg id "$1" --arg k "$2" --arg v "$3" \
    '(.calls[]|select(.id==$id))[$k]=$v' data/calls.json > "$tmp" && mv "$tmp" data/calls.json
}

transcribe_aai(){ # $1=audio $2=prefix
  local up job resp status
  up=$(curl -s -X POST "https://api.assemblyai.com/v2/upload" -H "Authorization: $AAI" --data-binary @"$1" | jq -r '.upload_url // empty')
  [ -z "$up" ] && { log "    upload AAI falhou"; return 1; }
  job=$(curl -s -X POST "https://api.assemblyai.com/v2/transcript" -H "Authorization: $AAI" -H "Content-Type: application/json" \
        -d "{\"audio_url\":\"$up\",\"language_code\":\"pt\",\"speaker_labels\":true,\"format_text\":true}" | jq -r '.id // empty')
  [ -z "$job" ] && { log "    submit AAI falhou"; return 1; }
  while true; do
    sleep 12
    resp=$(curl -s "https://api.assemblyai.com/v2/transcript/$job" -H "Authorization: $AAI")
    status=$(echo "$resp" | jq -r '.status // "error"')
    [ "$status" = "completed" ] && break
    [ "$status" = "error" ] && { echo "$resp" | jq -r '.error' | tee -a "$LOG"; return 1; }
  done
  echo "$resp" | jq -r '.text' > "$2.txt"
  echo "$resp" | jq -r '.utterances[]? | "[\((.start/1000)|floor|tostring)s] Speaker \(.speaker): \(.text)"' > "$2.speakers.txt"
  echo "$resp" | jq '{text:.text, words:.words, utterances:.utterances}' > "$2.json"
  return 0
}

FILTER="${1:-}"
while IFS=$'\t' read -r ID FID DUR; do
  [ -z "$ID" ] && continue
  [ -n "$FILTER" ] && [ "$FILTER" != "$ID" ] && continue
  RAW="$VID/${ID}_raw.mp4"; CMP="$VID/${ID}.mp4"; MP3="$AUD/${ID}.mp3"; WAV="$AUD/${ID}.wav"
  WT="library/walkthroughs/${ID}/WALKTHROUGH.md"
  [ -s "$TR/$ID.txt" ] && [ -s "$CMP" ] && [ -s "$WT" ] && { log "✓ $ID já completo — pulando"; continue; }
  log "=== $ID (~$DUR) ==="

  # 1) RAW (reaproveita / baixa) — só precisa se faltar transcrição ou vídeo
  if [ ! -s "$RAW" ] && [ ! -s "$CMP" ]; then
    log "  ↓ baixando..."; rclone backend copyid "$REMOTE" "$FID" "$RAW" </dev/null 2>>"$LOG"
    [ -s "$RAW" ] || { log "  ❌ download falhou"; continue; }
    log "  baixado: $(du -h "$RAW"|cut -f1)"
  fi
  SRC="$RAW"; [ -s "$SRC" ] || SRC="$CMP"

  # 2+3) áudio + TRANSCREVE (só se ainda não tem transcrição)
  if [ ! -s "$TR/$ID.txt" ]; then
    log "  🎧 extraindo áudio..."
    ffmpeg -nostdin -loglevel error -y -i "$SRC" -vn -ac 1 -ar 16000 -b:a 64k "$MP3" </dev/null
    ok=1
    if [ -n "$AAI" ] && [ -s "$MP3" ]; then
      log "  🗣 AssemblyAI..."; transcribe_aai "$MP3" "$TR/$ID" && ok=0 && log "  ✓ $TR/$ID.txt (+speakers)" || log "  ⚠ AAI falhou → whisper"
    fi
    if [ "$ok" != 0 ]; then
      M="$MODEL"; case "$DUR" in 0[2-9]:*|1[0-9]:*) M="$MODEL_SMALL";; esac
      ffmpeg -nostdin -loglevel error -y -i "$SRC" -vn -ar 16000 -ac 1 -c:a pcm_s16le "$WAV" </dev/null
      log "  🗣 whisper $(basename "$M")..."
      "$WHISPER" -m "$M" -f "$WAV" -l pt -otxt -osrt -of "$TR/$ID" -t "$(sysctl -n hw.ncpu)" </dev/null >>"$LOG" 2>&1
    fi
    [ -s "$TR/$ID.txt" ] && set_field "$ID" transcript "$TR/$ID.txt" && set_field "$ID" status "transcribed"
  else
    log "  ✓ transcrição já existe"
  fi

  # 4) vídeo jogável JÁ (usa o original; compressão é passo separado, scripts/compress_pass.sh)
  if [ ! -s "$CMP" ] && [ -s "$RAW" ]; then mv "$RAW" "$CMP"; fi
  [ -s "$CMP" ] && set_field "$ID" video "$CMP" && set_field "$ID" status "done"

  # 5) WALKTHROUGH (frames + WALKTHROUGH.md no formato Morfeu)
  if [ -s "$TR/$ID.txt" ] && [ -s "$CMP" ] && [ ! -s "$WT" ]; then
    log "  🖼  gerando walkthrough (frames + WALKTHROUGH.md)..."
    python3 scripts/build_walkthrough.py "$ID" >>"$LOG" 2>&1
  fi

  # 6) Supabase sync (se creds) + opcional limpeza local (Xeon: NOLOCAL=1)
  if [ -f data/.supabase.env ] || [ -n "${SUPABASE_URL:-}" ]; then
    bash scripts/supabase_sync.sh "$ID" >>"$LOG" 2>&1 || true
  fi
  if [ "${NOLOCAL:-0}" = "1" ]; then
    rm -f "$CMP"; rm -rf "library/walkthroughs/$ID/frames"
    set_field "$ID" video ""
    log "  🧹 NOLOCAL: vídeo via Drive, frames/transcrição no Supabase"
  fi

  rm -f "$MP3" "$WAV"
  log "  done $ID"
done < <(jq -r '.calls[] | [.id, .driveVideoId, (.durationApprox//"")] | @tsv' data/calls.json)
log "Pipeline finalizado."
