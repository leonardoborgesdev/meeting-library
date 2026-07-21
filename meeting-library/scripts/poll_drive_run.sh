#!/bin/bash
cd /opt/meeting-library || exit 1
export HOME=/root
set -a; . ./.env 2>/dev/null; set +a
export POLL_SINCE="${POLL_SINCE:-2026-06-20}"
export POLL_MAX_PER_RUN="${POLL_MAX_PER_RUN:-6}"
export POLL_DAILY_MAX="${POLL_DAILY_MAX:-300}"
export NOLOCAL="${NOLOCAL:-1}"
exec /usr/bin/python3 scripts/poll_drive.py
