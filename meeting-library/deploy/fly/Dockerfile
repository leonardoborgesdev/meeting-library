# Meeting Library — Fly.io (24/7, sem Mac). Puxa o Drive sozinho, frames/transcrição
# no Supabase, vídeo NUNCA fica no disco (NOLOCAL=1). Estado persiste em volume /data.
FROM python:3.12-slim

# deps de runtime: ffmpeg (frames/áudio), rclone (Drive), jq + curl (sync/transcrição)
RUN apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg rclone jq curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# semente do estado (data/ + library leve) — restaurada no 1º boot se o volume estiver vazio
RUN mkdir -p /seed \
    && cp -r /app/data /seed/data \
    && cp -r /app/library /seed/library \
    && chmod +x deploy/fly/entrypoint.sh

ENTRYPOINT ["/app/deploy/fly/entrypoint.sh"]
