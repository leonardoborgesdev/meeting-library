# 📹 Meeting Library — Inteligência de Reuniões da Automatrix

Painel que cataloga **todas as calls da Automatrix** num só lugar. Puxa as gravações do **Google Drive** (Meet Recordings do lucas@), recebe as calls **ao vivo do bot Vexa** e as **pré-calls do Cap**, **transcreve** (AssemblyAI), gera **walkthrough com frames** sincronizados às falas, e serve tudo numa **interface estilo Notion** (Galeria · Tabela · Board · Calendário · Volume) com busca por IA.

> **Atualizado em:** 2026-07-07 · **Produção:** https://meet.automatrixapps99x.win (login `automatrix` / `958462`) · **Infra:** 1 VPS Hostinger + Cloudflare Tunnel · **100% online, não depende de nenhuma máquina local.**

Esta é a arquitetura **atual (pós-migração)**. O painel saiu do **Fly** (`automatrix-meeting-library.fly.dev`, mantido parado como rollback) e hoje roda **na VPS** `187.77.24.132` em `/opt/meeting-library`. O domínio antigo `meet.automatrix-ai.com` **morreu** (o domínio `automatrix-ai.com` foi suspenso no registrar) → tudo migrou para **`meet.automatrixapps99x.win`** via Cloudflare Tunnel.

## O que faz

```
   3 FONTES DE CALL                                    O PAINEL
┌─────────────────────────┐
│ 📁 Google Drive          │  poll_drive (rclone gdrive: lucas@)
│   "Meet Recordings"      │ ──── baixa gravação nova ────┐
│   (auto, timer 30min)    │                              │
├─────────────────────────┤                              ▼
│ 🤖 Vexa (bot ao vivo)    │  brain → /api/ingest   ┌───────────────────────────────┐
│   entra na call, grava,  │ ─────────────────────▶ │  server.py (Python stdlib :8011)│
│   transcreve, analisa    │                        │   • baixa → AssemblyAI → frames │
├─────────────────────────┤                        │   • data/calls.json = "banco"   │
│ 🎥 Cap (pré-call)        │  cap_bridge → /api/ingest │   • backup Brazika Drive        │
│   cliente grava a tela   │ ─────────────────────▶ │   • serve index.html + /api/*   │
│   ANTES da call          │                        └───────────────┬───────────────┘
└─────────────────────────┘                                         │
   + ⬆ Upload manual (/api/upload)                                  ▼
                                          UI estilo Notion: Galeria·Tabela·Board·Calendário·Volume
                                          filtros (pessoa/projeto/ferramenta/tipo) + chat IA (Gemini)
```

Cada call vira um **card** com: vídeo/áudio (preview), **transcrição** (falas por locutor), **walkthrough** (≈55 frames sincronizados às falas), notas/análise, e links (Drive / Cap / Notion / GitHub). Ferramentas usadas são **auto-derivadas** do conteúdo.

**Escala atual (2026-07-07):** **144 cards** — `video` 136 · `audio` 5 (Cap pré-call) · `checklist` 3 · **131 transcritos**. Fontes: `auto_` (Drive) 109 · `precall` (Cap) 7 · treinamentos/históricos.

---

## Onde está hospedado (VPS Hostinger + Cloudflare)

| Recurso | Tipo | Host | Caminho / porta |
|---|---|---|---|
| **Painel Meeting Library** (front + back) | App | VPS `187.77.24.132` | `/opt/meeting-library` · `server.py` **:8011** |
| **Frontend** | SPA single-file | (servido pelo server.py) | `index.html` + `login.html` (design **Studio OS**, OKLCH) |
| **Backend** | HTTP puro (sem framework) | idem | `scripts/server.py` (Python **stdlib** `http.server`) |
| **"Banco de dados"** | Arquivo JSON | idem | `data/calls.json` (+ `meta.json`, `supabase.json`) |
| **Pipeline Drive** | Timer systemd | idem | `meeting-library-drive.timer` (30min) → `scripts/poll_drive.py` |
| **Serviço web** | systemd | idem | `meeting-library.service` (enabled) |
| **Reverse proxy** | nginx | idem | catch-all `_` → `127.0.0.1:8011` |
| **Túnel HTTPS** | Cloudflare Tunnel | idem (container docker) | `gsa-cloudflared` → painel |
| **Mídia (vídeos/áudio)** | Disco | idem | `library/videos` (3.6G) · `library/audio` (398M) · `library/transcripts` (237M) |
| **Rollback** | Fly (parado) | fly.io org suportebrazika | `automatrix-meeting-library.fly.dev` (NÃO deletar) |

### Domínios (Cloudflare)
| Domínio | Aponta para | Status |
|---|---|---|
| **`meet.automatrixapps99x.win`** | painel (:8011 via Tunnel `gsa-cloudflared`) | ✅ **NO AR** |
| `meet.automatrix-ai.com` | (era o painel) | ❌ morto — `automatrix-ai.com` suspenso no registrar |

> A VPS `187.77.24.132` hospeda também o **Vexa** (`/opt/vexa-lite`) e o **Cap** (`/opt/cap`) — os 3 sistemas conversam entre si localmente. Ver repo [`brazika/vexa-notetaker`](https://github.com/brazika/vexa-notetaker) para o bot Vexa e o Cap.

---

## De onde vêm as calls (3 pipelines + upload)

| Fonte | Como chega no painel | Componente |
|---|---|---|
| **📁 Google Drive** | `poll_drive.py` lista a pasta *Meet Recordings* (folder `1TDBW8…`) via `rclone gdrive:` (login lucas@, `drive.readonly`), baixa gravações novas, `process_calls.sh` transcreve + gera walkthrough, cria card `auto_*`. Timer a cada 30min, mais novas primeiro. | `scripts/poll_drive.py` + `poll_drive_run.sh` |
| **🤖 Vexa (ao vivo)** | O bot entra na call (auto-join pelo Google Calendar), transcreve por voz (Groq), e no fim o **cérebro** publica análise+transcrição via `POST /api/ingest`. | repo `vexa-notetaker` (`/opt/vexa-lite`) |
| **🎥 Cap (pré-call)** | Cliente grava a tela antes da call; `cap_bridge.py` transcreve (Groq) + lê a tela (Groq Vision) e cria card `precall_*` via `POST /api/ingest`. | `/opt/cap/cap_bridge.py` |
| **⬆ Upload manual** | Botão "Enviar gravação" no topbar → `POST /api/upload` (streama em disco) → mesmo pipeline (AssemblyAI + autofill Gemini). | `server.py` + `scripts/autofill.py` |

---

## Estrutura deste repositório

```
index.html               Frontend — SPA single-file (design Studio OS, views Notion, chat IA)
login.html               Tela de login (cookie de sessão)
scripts/
  server.py              Backend — HTTP stdlib :8011. Endpoints /api/* + serve o site + preview Drive
  poll_drive.py          Pipeline Drive: cataloga + drena gravações do Meet (rclone) → cards auto_*
  poll_drive_run.sh      Wrapper do timer (carrega .env + POLL_SINCE/MAX/DAILY, HOME=/root)
  process_calls.sh       Baixa → extrai áudio → AssemblyAI → walkthrough → backup → (NOLOCAL apaga vídeo)
  build_walkthrough.py   Gera os ~55 frames + WALKTHROUGH.md sincronizados às falas (formato Morfeu)
  autofill.py            Gemini preenche campos em branco (pessoa/projeto/tópicos) pós-transcrição
  td_push.py             Backup "infinito" no Brazika Drive (Teldrive, chunk 1.8GB)
  healthcheck.py         Monitor de saúde (done/fila/erros) → /api/health
  auto_summary.py        Card de resumo/checklist via LLM local (gated)
data/
  calls.json             O "banco": todos os cards (call, transcrição, walkthrough, links, tipo)
  meta.json              Links Notion/GitHub editáveis por card
  supabase.json          Mapa id→URLs públicas de frames (quando Supabase ativo)
library/
  transcripts/           .txt (fala) + .speakers.txt (por locutor) + .json (words AAI)
  walkthroughs/<id>/     frames/ + WALKTHROUGH.md
  videos/ audio/         mídia local (gitignored; NOLOCAL apaga vídeo de card do Drive)
  notes/                 notas/análises (.md) — Cap/Vexa/ingestão
deploy/
  fly/                   Dockerfile+fly.toml (rollback histórico)
  systemd/               units da VPS (web + timer do Drive)
  xeon/                  plano B (VPS antiga) + meeting-library.env (gitignored, tem segredos)
```

---

## Endpoints (server.py, `:8011`)

`/api/login` · `/api/logout` · `/api/me` · `/api/register` (convite `958462`) — **auth por cookie**
`/api/status` (catálogo+saúde, cache-buster) · `/api/health` · `/api/meta` (Notion/GitHub)
`/api/ingest` (Vexa/Cap criam card) · `/api/upload` (gravação manual) · `/api/transcribe` (sob demanda)
`/api/chat` (busca com **Gemini** sobre o catálogo) · `/api/download` · `/api/check` (checklist) · `/api/presentations`

> Máquinas (Vexa/Cap) publicam autenticando por header `X-Worker-Token` **ou** login `automatrix`/`958462`, indo pelo gateway docker interno `172.22.0.1:8088` (evita o hairpin do Cloudflare).

---

## Tokens e APIs necessários

| Token | Para que serve | Onde fica | Obrigatório |
|---|---|---|---|
| **AssemblyAI** | Transcrição das gravações do Drive/upload (pt-BR + diarização) | `.env` `ASSEMBLYAI_API_KEY` | ✅ Sim |
| **rclone (Google Drive OAuth)** | Puxar as gravações do Meet do lucas@ | VPS `/root/.config/rclone/rclone.conf` (remote `gdrive:`) | ✅ Sim (poll_drive) |
| **Gemini** | Chat de busca + autofill de campos | env `GEMINI_API_KEY` | ⚠️ Recomendado |
| **Teldrive (Brazika Drive)** | Backup "infinito" da mídia | `.env` `TD_TOKEN` (JWT 1 ano) | ⚠️ Recomendado |
| **Supabase** | Hospedar frames públicos (hoje **desligado**: `SUPABASE_URL` vazio) | `.env` `SUPABASE_URL`/`SUPABASE_KEY` | 🔵 Opcional |
| **Cloudflare Tunnel** | Expor o painel com HTTPS (`gsa-cloudflared`) | dashboard Cloudflare (token) | ✅ Sim (acesso externo) |
| **INVITE_CODE / AUTH_SALT** | Registro e hash de senha | `.env` | ✅ Sim |

> Todos os valores reais ficam em `.env` na VPS e em `deploy/xeon/meeting-library.env` — **ambos gitignored**, nunca neste repositório. `users.json`/`sessions.json` também são ignorados.

---

## Operação

```bash
# rodar o painel (VPS)
systemctl status meeting-library             # web :8011
systemctl status meeting-library-drive.timer # puxa Drive a cada 30min
journalctl -u meeting-library-drive.service -f  # ver o pipeline do Drive rodando

# puxar do Drive na mão
cd /opt/meeting-library && ./scripts/poll_drive_run.sh
```

**Login:** `automatrix` / `958462` (registro exige convite `958462`). Tema claro/escuro no ⚙ Configurações.
**Backup:** 3 cópias de toda mídia processada — VPS local + Brazika Drive (Teldrive) + Supabase VPS2 (quando ativo).
