#!/bin/bash
# captura frames a cada 4s por ~80s
mkdir -p /tmp/strip && rm -f /tmp/strip/*.png
for i in $(seq 1 20); do
  PID=$(ps -ef | grep "[c]hrome-linux/chrome" | grep -v "type=" | awk "{print \$2}" | head -1)
  if [ -n "$PID" ]; then
    nsenter -t "$PID" -m -u -i -n sh -lc "DISPLAY=:99 ffmpeg -y -v error -f x11grab -video_size 1366x768 -i :99 -frames:v 1 /tmp/f.png" 2>/dev/null \
      && cp /proc/$PID/root/tmp/f.png /tmp/strip/$(printf %02d $i).png 2>/dev/null
  fi
  sleep 4
done
echo "frames:"; ls /tmp/strip/*.png 2>/dev/null | wc -l
