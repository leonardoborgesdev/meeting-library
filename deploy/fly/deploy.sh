#!/usr/bin/env bash
# deploy.sh — roda NO MAC. Cria o app Fly dedicado, o volume, injeta os secrets
# (token do Drive + AssemblyAI + Supabase) e faz o deploy. Idempotente.
#   bash deploy/fly/deploy.sh
set -e
cd "$(dirname "$0")/../.."
APP="automatrix-meeting-library"
REGION="gru"

echo "== app =="
flyctl apps create "$APP" 2>/dev/null && echo "criado" || echo "já existe"

echo "== volume (3GB, $REGION) =="
flyctl volumes list --app "$APP" 2>/dev/null | grep -q ml_data \
  && echo "já existe" \
  || flyctl volumes create ml_data --app "$APP" --region "$REGION" --size 3 --yes

echo "== secrets =="
set -a; . deploy/xeon/meeting-library.env; . data/.supabase.env; set +a
RCLONE_B64="$(base64 < "$HOME/.config/rclone/rclone.conf" | tr -d '\n')"
flyctl secrets set --app "$APP" --stage \
  ASSEMBLYAI_API_KEY="$ASSEMBLYAI_API_KEY" \
  SUPABASE_URL="$SUPABASE_URL" \
  SUPABASE_KEY="$SUPABASE_KEY" \
  RCLONE_CONF_B64="$RCLONE_B64"

echo "== deploy =="
flyctl deploy . --app "$APP" --config deploy/fly/fly.toml --dockerfile deploy/fly/Dockerfile --ha=false

echo "== domínio meet.brazika.online =="
flyctl certs add meet.brazika.online --app "$APP" 2>/dev/null || true
flyctl certs show meet.brazika.online --app "$APP" 2>/dev/null || true

echo
echo "✓ pronto. URL temporária: https://$APP.fly.dev"
echo "  Depois do DNS na Cloudflare: https://meet.brazika.online"
