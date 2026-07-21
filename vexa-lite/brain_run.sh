#!/bin/bash
NATIVE="$1"
source /opt/vexa-lite/runtime-secrets.env
GK=$(grep "^TRANSCRIPTION_SERVICE_TOKEN=" /opt/vexa-lite/.env | cut -d= -f2-)
docker exec vexa-lite sh -lc "pactl set-sink-mute tts_sink 0; pactl set-source-mute virtual_mic 0" 2>/dev/null
for i in $(seq 1 30); do
  NID=$(curl -s -H "X-API-Key: $API_KEY" http://localhost:8056/bots/status | python3 -c "import sys,json
[print(b.get('meeting_id_from_name')) for b in json.load(sys.stdin).get('running_bots',[]) if b.get('native_meeting_id')=='$NATIVE']" | head -1)
  [ -n "$NID" ] && break; sleep 2
done
echo "brain_run: native=$NATIVE numid=$NID"
docker exec vexa-lite pkill -9 -f brain_ctr.py 2>/dev/null; sleep 1
exec docker exec -e NID="$NID" -e NATIVE="$NATIVE" -e GROQ_API_KEY="$GK" -e VEXA_API_KEY="$API_KEY" -e CEREBRAS_API_KEY="$CEREBRAS_API_KEY" -e GEMINI_API_KEY="$GEMINI_API_KEY" vexa-lite python3 /opt/brain_ctr.py
