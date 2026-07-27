#!/bin/bash
# meet.automatrix-ai.com agora roda NA VPS. Backup = tarball data+library -> Brazika Drive (semanal)
cd /opt/meeting-library || exit 1
if [ "$(date +%u)" = "7" ] || [ ! -f .last_drive_bk ]; then
  TS=$(date +%Y%m%d); tar czf /tmp/panel_${TS}.tar.gz data library 2>/dev/null
  /opt/vexa-lite/td_upload.sh /tmp/panel_${TS}.tar.gz / >/dev/null 2>&1 && date > .last_drive_bk && echo "[panel-backup] tarball $TS -> Brazika Drive"
  rm -f /tmp/panel_${TS}.tar.gz
fi
echo "[panel-backup] $(date -u): painel VIVO na VPS (data $(du -sh data 2>/dev/null|cut -f1) + library $(du -sh library 2>/dev/null|cut -f1))"
