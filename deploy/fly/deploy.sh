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
set -a
[ -f deploy/xeon/meeting-library.env ] && . deploy/xeon/meeting-library.env
[ -f deploy/xeon/meeting-library.local.env ] && . deploy/xeon/meeting-library.local.env
[ -f data/.supabase.env ] && . data/.supabase.env
[ -f data/.supabase.local.env ] && . data/.supabase.local.env
set +a
if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_KEY:-}" ]; then
  echo "SUPABASE_URL/SUPABASE_KEY precisam vir de env local ou arquivo .local" >&2
  exit 1
fi
RCLONE_B64="$(base64 < "$HOME/.config/rclone/rclone.conf" | tr -d '\n')"
flyctl secrets set --app "$APP" --stage \
  ASSEMBLYAI_API_KEY="$ASSEMBLYAI_API_KEY" \
  SUPABASE_URL="$SUPABASE_URL" \
  SUPABASE_KEY="$SUPABASE_KEY" \
  RCLONE_CONF_B64="$RCLONE_B64" \
  ${TD_TOKEN:+TD_TOKEN="$TD_TOKEN"}

echo "== deploy =="
flyctl deploy . --app "$APP" --config deploy/fly/fly.toml --dockerfile deploy/fly/Dockerfile --ha=false

echo "== domínio meet.automatrix-ai.com =="
flyctl certs add meet.automatrix-ai.com --app "$APP" 2>/dev/null || true
flyctl certs show meet.automatrix-ai.com --app "$APP" 2>/dev/null || true

echo
echo "✓ pronto. URL temporária: https://$APP.fly.dev"
echo "  Depois do DNS na Cloudflare: https://meet.automatrix-ai.com"
