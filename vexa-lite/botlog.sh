#!/bin/bash
# acha o container do bot e segue os logs por ~90s
for t in $(seq 1 15); do
  C=$(docker ps --format "{{.Names}}" | grep "^meeting-" | head -1)
  [ -n "$C" ] && break
  sleep 2
done
echo "container: $C"
timeout 90 docker logs -f "$C" 2>&1 | grep -iE "join|admit|name|button|click|wait|leave|left|alone|reason|error|timeout|removed|denied|lobby|element|selector" | tail -60
