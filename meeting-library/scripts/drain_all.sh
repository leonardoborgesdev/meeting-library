#!/bin/bash
cd /opt/meeting-library || exit 1
export HOME=/root
set -a; . ./.env 2>/dev/null; set +a
export POLL_SINCE=2026-06-20 POLL_MAX_PER_RUN=6 POLL_DAILY_MAX=999 NOLOCAL=1
echo "$(date -Is) === DRAIN ALL start ===" >> data/drain_all.log
for i in $(seq 1 40); do
  python3 scripts/poll_drive.py >> data/drain_all.log 2>&1
  pend=$(python3 -c "import json;d=json.load(open(\"data/calls.json\"));c=d[\"calls\"] if isinstance(d,dict) else d;print(len([x for x in c if str(x.get(\"id\",\"\")).startswith(\"auto_\") and not (x.get(\"transcript\") or x.get(\"transcribed\")) and x.get(\"type\")!=\"audio\"]))" 2>/dev/null)
  echo "$(date -Is) iter=$i pendentes=$pend" >> data/drain_all.log
  [ "${pend:-1}" -le 0 ] && break
  sleep 3
done
echo "$(date -Is) === DRAIN ALL end ===" >> data/drain_all.log
