#!/usr/bin/env bash
# push.sh — roda NO MAC. Envia a app pro Xeon (sem os vídeos pesados), leva o token do
# rclone e dispara o setup. Use quando o Xeon estiver ligado (ssh xeon respondendo).
set -e
HOST="${1:-xeon}"
DEST="/home/automatrix/meeting-library"
cd "$(dirname "$0")/../.."
echo "== checando $HOST =="
ssh -o ConnectTimeout=8 "$HOST" "echo ok; mkdir -p $DEST" || { echo "Xeon offline — ligue e rode de novo"; exit 1; }

echo "== rsync da app (sem vídeos/áudios/frames pesados) =="
rsync -az --delete \
  --exclude 'library/videos/' --exclude 'library/audio/' --exclude 'library/walkthroughs/*/frames/' \
  --exclude '.git/' --exclude 'data/*.log' \
  ./ "$HOST:$DEST/"

echo "== levando token do rclone (Drive) =="
ssh "$HOST" "mkdir -p ~/.config/rclone"
rsync -az "$(rclone config file | tail -1)" "$HOST:~/.config/rclone/rclone.conf"

echo "== rodando setup no Xeon =="
ssh "$HOST" "bash $DEST/deploy/xeon/setup.sh"
echo "== deploy concluído =="
