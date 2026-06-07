# 📹 Meeting Library — Chris Lamm × Automatrix IA

Video library for meeting recordings with built-in HTML5 player, filters, and Google Drive links.

## Features
- HTML5 video player with streaming (range requests)
- Filter by: Playable / Screen Demo / Transcribed / Chris Present
- Direct Google Drive links per meeting
- Stats: total, playable, screen demos, transcribed

## Setup (Nginx)

```nginx
server {
    listen 3009;
    server_name your-domain.com;
    root /var/www/chris-calls;
    index index.html;
    disable_symlinks off;

    location / {
        try_files $uri $uri/ =404;
        add_header Cache-Control "no-cache";
        add_header Access-Control-Allow-Origin "*";
    }

    location ~* ^/videos/.+\.(mp4|mov|mkv)$ {
        root /var/www/chris-calls;
        disable_symlinks off;
        add_header Accept-Ranges bytes;
        add_header Access-Control-Allow-Origin "*";
        add_header Cache-Control "public, max-age=3600";
    }
}
```

## Videos Folder

Place video files (or symlinks) in `/var/www/chris-calls/videos/`.

## Access

- Local: `http://localhost:3009/`
- Tailscale: `http://automatrix-x99.tail870dd6.ts.net:3009/`

## Stack

Pure HTML/CSS/JS — zero dependencies.
