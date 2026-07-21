#!/usr/bin/env bash
# walkthrough_pass.sh — regenera o WALKTHROUGH.md (formato Morfeu atualizado) de todas as
# calls que tenham transcrição + vídeo local. Use p/ "refazer" os walkthroughs.
set -uo pipefail
cd "$(dirname "$0")/.."
jq -r '.calls[]|select(.transcript!=null and (.video//"")!="")|.id' data/calls.json | while read -r id; do
  [ -z "$id" ] && continue
  rm -f "library/walkthroughs/$id/WALKTHROUGH.md"
  python3 scripts/build_walkthrough.py "$id"
done
echo "walkthroughs regenerados."
