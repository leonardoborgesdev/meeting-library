# Meeting Library (`meet.*`)

Painel de reunioes: lista/organiza calls, transcreve (AssemblyAI), gera resumo/apresentacao (Gemini/OpenAI), sincroniza (Notion). Serve `meet.<dominio>`.

- **Stack:** Python (`scripts/server.py`, sem framework pesado) + HTML (`index.html`/`login.html`) + `sync_live.py`.
- **Roda via systemd** (`meeting-library.service`, EnvironmentFile=.env) na porta `PORT` (8011).

## Deploy numa VPS
```bash
git clone https://github.com/brazika/meeting-library /opt/meeting-library
cd /opt/meeting-library
cp .env.example .env    # preencher com as chaves do cliente (ver abaixo)
python3 -m pip install -r requirements.txt   # se houver; senao deps do server.py
# instalar o systemd unit (ver deploy/) e habilitar:
systemctl enable --now meeting-library
# apontar meet.<dominio> -> localhost:8011 (Cloudflare Named Tunnel)
```

## APIs/tokens que o CLIENTE precisa
| O que | Pra que | Obrigatorio |
|---|---|---|
| **AssemblyAI** API key | transcricao das calls | sim (se transcrever) |
| **Notion** token | sincronizar reunioes no Notion | opcional |
| **Gemini** e/ou **OpenAI** key | resumo + apresentacao automatica | opcional |
| **Teldrive** (`TD_TOKEN`) | storage das midias (Telegram) | opcional |
| **Supabase** URL | dados | opcional |

`data/` e `library/` (as gravacoes/midias, ~GBs) NAO vao no git — sao geradas em uso.
