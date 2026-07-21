#!/bin/bash
# Backup Fly-free das gravações (áudio) + transcrições do Vexa -> disco da VPS (cópia separada do volume docker)
DST=/opt/vexa-lite/backups; mkdir -p "$DST/recordings"
SRC=/var/lib/docker/volumes/vexa-lite_vexa-recordings/_data
if command -v rsync >/dev/null; then rsync -a "$SRC/" "$DST/recordings/" 2>/dev/null; else cp -ru "$SRC/." "$DST/recordings/" 2>/dev/null; fi
docker exec vexa-postgres pg_dump -U vexa -d vexa -t transcriptions > "$DST/transcriptions.sql" 2>/dev/null
# backup das gravações das calls no BRAZIKA DRIVE (Teldrive, incremental, sem Fly)
if [ -f /opt/vexa-lite/.td_token ]; then
  UP=/opt/vexa-lite/.td_uploaded; touch "$UP"
  find "$SRC" -name master.webm 2>/dev/null | while read f; do
    sess=$(basename "$(dirname "$(dirname "$f")")")
    grep -q "$sess" "$UP" 2>/dev/null && continue
    [ "$(wc -c < "$f")" -lt 10000 ] && continue
    cp "$f" "/tmp/Call_${sess}.webm"
    /opt/vexa-lite/td_upload.sh "/tmp/Call_${sess}.webm" / >/dev/null 2>&1 && echo "$sess" >> "$UP" && echo "[backup] Call $sess -> Brazika Drive"
    [ -f /opt/vexa-lite/.supabase_key ] && /opt/vexa-lite/sb_upload.sh "/tmp/Call_${sess}.webm" "calls/${sess}.webm" >/dev/null 2>&1 && echo "[backup] Call $sess -> Supabase VPS2"
    rm -f "/tmp/Call_${sess}.webm"
  done
fi
echo "[backup] $(date -u): audio=$(du -sh $DST/recordings 2>/dev/null|cut -f1) transcript=$(du -sh $DST/transcriptions.sql 2>/dev/null|cut -f1) drive=$(wc -l < /opt/vexa-lite/.td_uploaded 2>/dev/null||echo 0) calls"
