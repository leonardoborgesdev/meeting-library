#!/usr/bin/env bash
# supabase_sync.sh <call_id> — sobe frames + transcrições + WALKTHROUGH.md de UMA call
# pro bucket 'meeting-library' do seu projeto Supabase (free tier: 50MB/arquivo → só small).
# Lê creds de SUPABASE_URL / SUPABASE_KEY (ou de /tmp/.ml_sburl /tmp/.ml_sbkey).
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
[ -f data/.supabase.env ] && . data/.supabase.env
URL="${SUPABASE_URL:-$(cat /tmp/.ml_sburl 2>/dev/null)}"
KEY="${SUPABASE_KEY:-$(cat /tmp/.ml_sbkey 2>/dev/null)}"
BUCKET="meeting-library"; LOG="data/supabase.log"
[ -z "$URL" ] || [ -z "$KEY" ] && { echo "sem creds Supabase"; exit 1; }
ID="$1"
up(){ # localfile destpath contenttype
  [ -s "$1" ] || return 0
  curl -s -X POST "$URL/storage/v1/object/$BUCKET/$2" -H "Authorization: Bearer $KEY" -H "apikey: $KEY" \
    -H "x-upsert: true" -H "Content-Type: $3" --data-binary @"$1" >/dev/null
}
echo "[$(date '+%H:%M:%S')] ↑ supabase $ID" | tee -a "$LOG"
up "library/transcripts/$ID.txt"          "$ID/transcript.txt"   "text/plain"
up "library/transcripts/$ID.speakers.txt" "$ID/speakers.txt"     "text/plain"
up "library/walkthroughs/$ID/WALKTHROUGH.md" "$ID/WALKTHROUGH.md" "text/markdown"
n=0
for f in library/walkthroughs/$ID/frames/*.jpg; do
  [ -e "$f" ] || continue
  up "$f" "$ID/frames/$(basename "$f")" "image/jpeg"; n=$((n+1))
done
# grava mapa em data/supabase.json
pub="$URL/storage/v1/object/public/$BUCKET/$ID"
tmp=$(mktemp); [ -f data/supabase.json ] || echo '{}' > data/supabase.json
jq --arg id "$ID" --arg b "$pub" \
  '.[$id]={frames:($b+"/frames"), walkthrough:($b+"/WALKTHROUGH.md"), speakers:($b+"/speakers.txt"), transcript:($b+"/transcript.txt")}' \
  data/supabase.json > "$tmp" && mv "$tmp" data/supabase.json
echo "[$(date '+%H:%M:%S')] ✓ $ID: $n frames + transcrições no Supabase" | tee -a "$LOG"
