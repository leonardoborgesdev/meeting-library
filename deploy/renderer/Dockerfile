FROM node:20-bookworm-slim

# deps: python, ffmpeg, git, curl/unzip + bibliotecas do Chromium headless (Remotion)
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 ffmpeg git curl unzip ca-certificates \
      libnss3 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libgbm1 libasound2 \
      libxrandr2 libxkbcommon0 libxfixes3 libxcomposite1 libxdamage1 libxext6 \
      libpango-1.0-0 libcairo2 libcups2 libexpat1 libglib2.0-0 fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# instala o template Remotion + baixa o Chrome headless
RUN cd presentation-template \
    && npm install --no-audit --no-fund \
    && npx remotion browser ensure

ENV REMOTION_CHROME_MODE=headless-shell
ENTRYPOINT ["python3", "scripts/render_worker.py"]
