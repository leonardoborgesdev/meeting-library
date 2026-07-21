# Guia de Replicação — duplicar o "Meet" (Meeting Library)

Objetivo: subir um painel **idêntico**, mudando **só as calls que entram** (ou seja, qual conta Google/calendário é vigiado). Tempo estimado: ~1h.

---

## 0. Pré-requisitos
- 1 VPS Linux (Ubuntu 22.04+), Docker + Docker Compose, Python 3.10+.
- Um subdomínio apontado pra VPS (ex: `meet2.seudominio` via Cloudflare Tunnel ou Nginx).
- As contas/chaves de API da seção **1**.

---

## 1. TODAS as chaves/APIs necessárias (e onde pegar)

| Token / API | Pra quê | Onde obter |
|---|---|---|
| **Google OAuth** (Client ID, Secret, **Refresh Token**) | **Define QUAIS calls o bot entra** — o calendário desta conta | https://console.cloud.google.com → ativar *Google Calendar API* → OAuth client (Desktop) → gerar refresh token (scope `calendar.readonly`) |
| **Groq API key** (`gsk_...`) | Transcrição (Whisper) + brain | https://console.groq.com/keys |
| **Cerebras API key** (`csk-...`) | Brain (resumo) | https://cloud.cerebras.ai |
| **Gemini API key** (`AIza...`) | Brain (resumo) | https://aistudio.google.com/apikey |
| **AssemblyAI key** | Transcrição/diarização de reforço no painel (opcional) | https://www.assemblyai.com |
| **Teldrive token** | Storage de mídia via Telegram (opcional) | Teldrive self-host |
| **Supabase URL** | Sync do painel (opcional) | https://supabase.com |
| Gerados por você | `ADMIN_API_TOKEN`, `POSTGRES_PASSWORD`, `MINIO_ACCESS_KEY/SECRET`, `VEXA_API_KEY`, `AUTH_SALT`, `INVITE_CODE`, `CTRL_TOKEN` | `openssl rand -hex 24` |

> O **mínimo pra funcionar** = Google OAuth + Groq (transcrição) + os segredos gerados. Cerebras/Gemini/AssemblyAI/Teldrive/Supabase são reforços/opcionais.

---

## 2. Subir a Vexa (o bot que entra e transcreve)
```bash
mkdir -p /opt/vexa-lite && cd /opt/vexa-lite
# copie compose.yaml, control.py, brain_ctr.py, brain_run.sh, backup.sh deste repo
cp vexa-lite/.env.example .env            # preencha (Groq, postgres, minio)
docker compose up -d
# cria a API key do Vexa (usada em autojoin.env e brain.env):
curl -s -X POST http://localhost:8056/admin/tokens \
  -H "Authorization: Bearer $ADMIN_API_TOKEN" | tee vexa_key.txt
```

## 3. Configurar QUAIS calls entrar (o passo que muda)
```bash
cd /opt/vexa-lite
cp autojoin.env.example autojoin.env      # <<< preencha o GOOGLE_* da conta que recebe as calls
# roda o autojoin (vigia o calendário e manda o Vexa entrar):
python3 control.py                         # ou via systemd/cron (ver control.py)
```
> **É AQUI que se troca a instância:** o `autojoin.env` aponta pra UMA conta Google.
> Painel novo = calendário de outra conta = outras calls. O resto é idêntico.

## 4. Brain (resumos por IA) — opcional mas recomendado
```bash
cd /opt/vexa-lite
cp brain.env.example brain.env             # Groq/Cerebras/Gemini + PANEL_URL do painel novo
./brain_run.sh                             # processa os transcripts
```

## 5. Subir o painel (Meeting Library)
```bash
mkdir -p /opt/meeting-library && cd /opt/meeting-library
# copie scripts/, index.html, login.html, sync_live.py deste repo
cp meeting-library/.env.example .env       # AUTH_SALT, INVITE_CODE, ASSEMBLYAI, etc.
python3 scripts/server.py                  # sobe em :8011
```

## 6. Expor o domínio
- Aponte `meet2.seudominio` → `127.0.0.1:8011` (Nginx `proxy_pass` ou Cloudflare Tunnel).
- Ajuste `PANEL_URL`/`PANEL_HOST` no `brain.env` pro domínio novo.

---

## 7. Checklist "está funcionando?"
```bash
docker ps | grep vexa                      # vexa-lite/postgres/minio Up
curl -s localhost:8056/health              # Vexa viva
curl -s -o /dev/null -w "%{http_code}\n" localhost:8011   # painel (302/200)
# entre numa call de teste agendada na conta Google → deve aparecer no painel em minutos
```

## 8. O que é IGUAL vs o que MUDA entre instâncias
| | Igual em toda cópia | Muda por instância |
|---|---|---|
| Código (compose, control.py, brain, server.py) | ✅ | |
| Chaves de infra (Groq, Cerebras, Gemini) | pode reusar | ou usar novas |
| **`autojoin.env` (conta Google / calendário)** | | ✅ **← as calls** |
| Domínio / `PANEL_URL` | | ✅ |
| Segredos gerados (tokens/senhas) | | ✅ (gere novos) |

---

## Estrutura do repo
```
vexa-lite/          # a Vexa (bot + transcrição)
  compose.yaml
  control.py        # autojoin (vigia calendário)  ← QUAIS calls
  brain_ctr.py      # resumo IA
  *.env.example
meeting-library/    # o painel
  scripts/server.py # servidor web :8011
  index.html / login.html
  .env.example
```
