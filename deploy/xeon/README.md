# Deploy no Xeon (24/7, nada local no Mac)

Quando o Xeon estiver ligado (`ssh xeon` responde), rode **no Mac**:

```bash
cd ~/Desktop/meeting-library
bash deploy/xeon/push.sh
```

Isso faz tudo:
1. `rsync` da app pro Xeon (`/home/automatrix/meeting-library`) — **sem** os vídeos pesados.
2. Leva o **token do rclone** (acesso ao Drive) do Mac pro Xeon.
3. Roda `setup.sh` no Xeon, que:
   - instala `rclone jq ffmpeg python3`;
   - sobe o **servidor** como serviço systemd (`meeting-library.service`, porta 8009, `HOST=0.0.0.0`);
   - instala o **cron de auto-pull** (`*/20 min`) que detecta calls novas no Drive e processa sozinho;
   - faz a **primeira varredura** do Drive.

## Como funciona o auto-pull
`scripts/poll_drive.py` lista a pasta *Meet Recordings* do Drive, acha gravações **novas**
(dedup por ID), adiciona no `calls.json` e processa cada uma:
**baixa → transcreve (AssemblyAI) → frames + WALKTHROUGH.md → sobe pro Supabase → apaga o vídeo local** (`NOLOCAL=1`).
Ou seja: nada de vídeo fica no disco; preview continua via Drive, frames/transcrição no Supabase.

## Acessar a app
`http://<IP-tailscale-do-xeon>:8009` (ou põe atrás do nginx que já existe no Xeon).

## Comandos úteis (no Xeon)
```bash
systemctl status meeting-library          # estado do servidor
journalctl -u meeting-library -f          # logs do servidor
tail -f ~/meeting-library/data/poll.log   # logs do auto-pull
crontab -l                                # confere o cron
bash deploy/xeon/poll_cron.sh             # rodar a varredura manualmente
bash scripts/walkthrough_pass.sh          # regenerar walkthroughs (formato Morfeu)
```

## Config
- `deploy/xeon/meeting-library.env` — `ASSEMBLYAI_API_KEY`, `HOST`, `PORT`, `NOLOCAL=1`.
- `data/.supabase.env` — creds do Supabase (vai junto no rsync).
