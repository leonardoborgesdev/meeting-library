#!/usr/bin/env bash
# wrapper do cron: carrega env (AAI + Supabase + NOLOCAL) e roda o poller
cd "$(dirname "$0")/../.."
set -a
. deploy/xeon/meeting-library.env
[ -f data/.supabase.env ] && . data/.supabase.env
set +a
python3 scripts/poll_drive.py
