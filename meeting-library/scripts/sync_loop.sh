#!/usr/bin/env bash
cd "$(dirname "$0")/.."
for i in $(seq 1 40); do
  bash scripts/sync_pass.sh >/dev/null 2>&1
  n=$(jq 'keys|length' data/supabase.json 2>/dev/null || echo 0)
  pgrep -f process_calls.sh >/dev/null || running=0 && running=1
  echo "[loop $i] supabase=$n/19 lote=$(pgrep -f process_calls.sh >/dev/null && echo on || echo off)" >> data/sync_loop.log
  [ "$n" -ge 19 ] && break
  sleep 150
done
