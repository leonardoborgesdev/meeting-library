#!/usr/bin/env bash
# sync_pass.sh — sobe pro Supabase toda call que já tem WALKTHROUGH.md e ainda não foi sincronizada.
# Rode quando quiser (ou em loop). Idempotente (x-upsert).
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
for d in library/walkthroughs/*/; do
  id=$(basename "$d")
  [ -s "$d/WALKTHROUGH.md" ] || continue
  # já sincronizado? (existe no supabase.json) -> pula
  if [ -f data/supabase.json ] && jq -e --arg id "$id" 'has($id)' data/supabase.json >/dev/null 2>&1; then
    echo "✓ $id já no Supabase"; continue
  fi
  bash scripts/supabase_sync.sh "$id"
done
echo "sync_pass finalizado."
