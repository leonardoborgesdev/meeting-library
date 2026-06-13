# Meeting Library — Documentação Completa

> Catálogo inteligente das calls da Automatrix. Puxa as gravações do Google Drive do Lucas,
> transcreve, gera walkthrough com frames, ingere reuniões do Notion, e serve tudo numa
> interface estilo Notion — **100% online, sem depender de nenhuma máquina local**.

**Produção:** https://meet.brazika.online (login `automatrix` / `958462`)
**Fallback:** https://automatrix-meeting-library.fly.dev

---

## 1. O que é / para que serve

A Automatrix grava dezenas de reuniões (Meet → Drive do Lucas) e também áudios/reuniões
direto no Notion. Esse acervo estava espalhado e sem busca. A **Meeting Library** centraliza
tudo num catálogo navegável:

- **Calls de vídeo** (Drive): preview direto, transcrição (AssemblyAI pt-BR com speakers),
  walkthrough no formato Morfeu333 (frames 1-a-cada-N-segundos sincronizados com a fala).
- **Áudios** e **checklists/docs** (cards especiais).
- **Reuniões do Notion** (Agency OS): ingeridas como cards com o conteúdo + link direto.
- **Views estilo Notion:** Galeria, Tabela (ordenável), Board (agrupável), Calendário, Volume.
- **Chat de busca geral**, **monitor de saúde**, **login/registro**, **métricas**.

Tudo se alimenta sozinho: cron interno no Fly puxa o Drive e o Notion, transcreve, gera
frames, sobe pro Supabase e se auto-corrige — sem intervenção.

---

## 2. Infraestrutura completa

```
                      ┌────────────────────────── Fly.io (gru / São Paulo) ──────────────────────────┐
  Google Drive        │  app: automatrix-meeting-library   (shared-cpu-1x · 1GB · sempre ligado)      │
  (Meet Recordings)   │                                                                               │
  conta lucas@        │   entrypoint.sh (3 loops paralelos):                                          │
  automatrix-ia.com   │     ├─ poll_drive.py     (a cada 1h) ── baixa → transcreve → frames → Supabase│
        │  rclone     │     ├─ healthcheck.py    (a cada 15m) ── escreve health.json (status/auto-cura)│
        └────────────►│     └─ notion_poll.py    (a cada 30m) ── ingere reuniões do Notion como cards  │
                      │                                                                               │
  Notion (Agency OS)  │   server.py (porta 8009) ── serve o site + API (auth por cookie)              │
  bot clawdy ─────────►│                                                                               │
                      │   Volume "ml_data" (12GB) montado em /data ── calls.json, transcrições,        │
                      │     walkthroughs(.md), notes, users.json, sessions.json, *.log, health.json    │
                      └───────────────┬──────────────────────────────────┬────────────────────────────┘
                                      │ frames + transcrição + md         │ HTTPS
                                      ▼                                   ▼
                          Supabase Storage (brazika)            Cloudflare DNS (brazika.online)
                          bucket público "meeting-library"      meet.brazika.online → Fly (cert LE)
```

### Componentes e por que cada um

| Camada | Tecnologia | Papel | Por quê |
|--------|-----------|-------|---------|
| **Host** | Fly.io (`automatrix-meeting-library`, região `gru`) | Roda o servidor + os 3 crons 24/7 | Grátis-ish, sempre ligado, sem depender do Mac/Xeon. App **dedicado** (regra: 1 app por projeto). |
| **Compute** | shared-cpu-1x, 1GB RAM, `min_machines_running=1`, `auto_stop=false` | Não pode dormir (senão o cron para) | Equilíbrio custo × precisar processar vídeo de até 2,6GB. |
| **Disco** | Fly Volume `ml_data` (12GB) em `/data` | Persiste estado entre deploys/restarts | Vídeo é transitório (baixa→processa→apaga); só metadados/transcrições ficam. |
| **Origem dos vídeos** | Google Drive (rclone, conta `lucas@automatrix-ia.com`) | Pasta "Meet Recordings" (`1TDBW8…`) com 112+ gravações | É onde o Meet salva automaticamente. Token do rclone vai como secret. |
| **Transcrição** | AssemblyAI (`universal-2`, pt-BR, `speaker_labels`) | Áudio → texto com quem-fala + timestamps por palavra | Qualidade pt-BR muito superior ao Gemini (que confundia PT com EN). |
| **Frames/vídeo** | ffmpeg (`fps=1/N`, `scale=640`) | Extrai ~55 frames/call + áudio 16kHz mono | `interval=ceil(dur/55)` capa em 55 frames mesmo num vídeo de 7h → cabe no Supabase. |
| **Storage de frames/transcrição** | Supabase Storage (projeto brazika, bucket público `meeting-library`) | Serve frames + .txt + WALKTHROUGH.md publicamente | Free tier 1GB → 55 frames/call × 112 ≈ 280MB. Vídeo NÃO cabe (50MB/arquivo). |
| **Notion** | API v3 (bot `clawdy`, workspace "Espaço de trabalho de Herberth Morfeu Herzich") | Ingere reuniões do Agency OS como cards | Lá tem briefings, kickoffs, análises por reunião e os áudios gravados no Notion. |
| **DNS/TLS** | Cloudflare (zona `brazika.online`) + cert Let's Encrypt do Fly | `meet.brazika.online` (registros DNS-only → Fly emite o cert) | Subdomínio bonito com HTTPS. |
| **Auth** | Cookie de sessão (server.py) | Login/registro, conta padrão `automatrix`/`958462` | Protege o acervo (calls do Lucas) na URL pública. |

### Secrets (Fly) — nada commitado
- `ASSEMBLYAI_API_KEY` — transcrição.
- `SUPABASE_URL` / `SUPABASE_KEY` — upload de frames/transcrição.
- `RCLONE_CONF_B64` — base64 do `rclone.conf` (acesso ao Drive); restaurado em `/data/rclone.conf` no boot.
- `NOTION_TOKEN` — integração do Notion (bot clawdy).
- `GEMINI_API_KEY` / `GEMINI_MODEL` — IA do chat (Gemini 2.5-flash). ⚠️ `gemini-2.0-flash` foi descontinuado (404).
- `AUTH_SALT` / `INVITE_CODE` — auth (defaults embutidos).

### ⚙️ Independência do Mac (importante)
**Em runtime, nada depende do Mac.** O app roda inteiro no Fly: `server.py` + 3 loops
(Drive / healthcheck / Notion) dentro do container, com TODOS os segredos como secrets do Fly
e o estado num volume. O token do rclone vive em `/data/rclone.conf` (auto-refresh), não no Mac.
O Mac só é usado para **deploy** (`flyctl deploy` envia uma nova versão do código) — isso é
desenvolvimento, não operação. Desligue o Mac e a Meeting Library continua puxando Drive+Notion,
transcrevendo, monitorando e respondendo no chat normalmente.

### Variáveis (fly.toml)
`HOST=0.0.0.0` · `PORT=8009` · `NOLOCAL=1` (apaga vídeo após processar) ·
`POLL_SINCE=2025-01-01` (backfill histórico) · `POLL_MAX_PER_RUN=2` · `POLL_DAILY_MAX=6`
(cota diária — poucas por dia) · `POLL_INTERVAL=3600` · `HEALTH_INTERVAL=900` · `NOTION_INTERVAL=1800`.

---

## 3. Pipeline de dados (como uma call vira card)

```
1. poll_drive.py lista a pasta do Drive (rclone lsjson)
2. Cataloga gravações novas em calls.json (status "catalog") — fallback de data por ModTime
3. Dreno (cota diária POLL_DAILY_MAX): pega as N mais novas pendentes
4. process_calls.sh por call:
     rclone backend copyid → baixa o vídeo (transitório, /data/library/videos)
     ffmpeg → extrai áudio (16kHz mono)
     AssemblyAI → .txt + .speakers.txt + .json (words)
     build_walkthrough.py → 55 frames + WALKTHROUGH.md (formato Morfeu)
     supabase_sync.sh → sobe frames + transcrição + md pro bucket
     NOLOCAL=1 → apaga o vídeo e os frames locais (preview fica via Drive, frames via Supabase)
5. healthcheck.py confere se ficou completo; se não, o dreno reprocessa (auto-cura)
```

**Auto-cura:** `poll_drive.needs_work()` reprocessa calls transcritas mas sem frames no
Supabase (ex.: interrompidas por deploy). **Sem whisper no container** → se a AssemblyAI
estourar cota, a call fica pendente e re-tenta depois.

---

## 4. Banco de dados / modelo de dados

Não há SQL — o "banco" é **arquivo no volume** + **Supabase Storage**. Simples, versionável, sem servidor de DB.

### `data/calls.json` — manifesto (fonte da verdade dos cards)
```jsonc
{
  "calls": [{
    "id": "auto_2026-06-10_junior-mauricio-telemedicina",
    "pessoa": "Mauricio",
    "title": "Junior / Mauricio — Telemedicina",
    "date": "2026-06-10",
    "projeto": "Telemedicina (UBS)",
    "assunto": ["telemedicina", "UBS"],     // tópicos
    "participantes": ["Lucas F. N. Alves", "Mauricio", "Junior"],
    "type": "video",                          // video | audio | checklist | notion
    "driveVideoId": "1789nxj4…",              // id no Drive (preview/print)
    "sizeMB": 1584,
    "durationApprox": "138:15",
    "transcript": "library/transcripts/<id>.txt",
    "walkthrough": "library/walkthroughs/<id>/WALKTHROUGH.md",
    "notes": "library/notes/<id>.md",         // conteúdo (notion/checklist)
    "clkey": "brazika",                       // checklist: aponta pro data/checklist_*.json
    "notion": "https://notion.so/…",          // (em meta.json)
    "github": "https://github.com/brazika/…", // (em meta.json)
    "status": "done"                          // catalog | transcribed | done | plan
  }]
}
```

### Outros arquivos de estado (em `/data`)
| Arquivo | Conteúdo |
|---------|----------|
| `data/meta.json` | `{id: {notion, github}}` — links editáveis por card |
| `data/supabase.json` | `{id: {frames:[urls], walkthrough, transcript}}` — mapa público |
| `data/checklist*.json` | checklists (projetos / kinbox / brazika) com grupos+tarefas marcáveis |
| `data/users.json` | `{user: sha256(user:pw:salt)}` — login |
| `data/sessions.json` | `{token: user}` — sessões ativas |
| `data/health.json` | último status do monitor (lido por /api/health) |
| `data/.backfill_day` | `{date, count}` — cota diária do backfill |
| `library/transcripts/<id>.txt / .speakers.txt / .json` | transcrição (texto / com speaker / words) |
| `library/walkthroughs/<id>/WALKTHROUGH.md` | walkthrough Morfeu (frames + falas sincronizadas) |
| `library/notes/<id>.md` | conteúdo de cards notion/checklist |

### Classificações (campos para filtrar/agrupar)
data · pessoa · projeto · tópicos(assunto) · **ferramentas** (auto-derivadas por regex sobre
título+projeto+tópicos) · tarefas (progresso de checklist) · tipo · status · duração · tamanho.

---

## 5. Plataforma / análise geral da aplicação

### Backend — `scripts/server.py` (Python stdlib, zero dependências)
`http.server` + `socketserver`. Serve arquivos estáticos e a API. Auth por cookie gateia tudo.

| Rota | Método | O quê |
|------|--------|-------|
| `/login` | GET | página de login (`login.html`) |
| `/api/login` `/api/register` `/api/logout` `/api/me` | POST/GET | autenticação |
| `/api/status` | GET | calls + running + meta + supabase + checklists |
| `/api/health` | GET | status do monitor |
| `/api/transcribe?id=` `/api/download?id=` | POST | dispara processamento sob demanda |
| `/api/meta?id=` | POST | salva link Notion/GitHub do card |
| `/api/check?item=&cl=` | POST | marca tarefa de checklist |
| `/api/ingest` | POST | injeta um card (usado pela ingestão do Notion) |
| `/api/chat` | POST | **assistente IA**: manda o catálogo + pergunta pro Gemini, devolve `{answer, ids}` |

### Frontend — `index.html` (single-file, sem build, design Studio OS)
Sistema de design **Studio OS** (OKLCH navy/cobalt/gold, Inter, glass topbar, cards hairline,
pills de stage, scrim+blur). Réplica fiel do `youtube-os-studioos`. Componentes:
- **5 views** (Galeria/Tabela/Board/Calendário/Volume) com agrupar-por e ordenar.
- **Filtros**: pessoa, projeto, **período (de/até)**, busca, chips de tipo/status, temas.
- **Popup de detalhe**: preview (Drive iframe / player / áudio), transcrição com frames
  sincronizados (walkthrough), notas, checklist, índice lateral, campos Drive/Notion/GitHub.
- **Chat assistente IA** (canto inferior direito): pergunta em linguagem natural → `/api/chat`
  manda o catálogo pro **Gemini 2.5-flash** (server-side, chave nunca exposta) → resposta + os
  cards relevantes com links. Cai pra busca local (stopwords + "hoje/ontem/recentes") se sem IA.
- **Filtro de período (De/Até)** — vale inclusive no Calendário.
- **Botões Métricas / Status** (popups) + **Sair**.

### Scripts (`scripts/`)
`server.py` · `process_calls.sh` (pipeline) · `build_walkthrough.py` (frames+md) ·
`supabase_sync.sh` · `poll_drive.py` (catálogo+dreno Drive) · `notion_poll.py` (ingestão Notion) ·
`healthcheck.py` (monitor) · `auto_summary.py` (resumo via Ollama, opcional) · `compress_pass.sh` ·
`walkthrough_pass.sh` · `download_one.sh`.

### Deploy (`deploy/fly/`)
`Dockerfile` (python3.12 + ffmpeg + rclone + jq) · `fly.toml` · `entrypoint.sh` (loops) ·
`deploy.sh` (cria app+volume+secrets+deploy+cert). `deploy/xeon/` = plano B (servidor próprio).

---

## 6. Skills / técnicas usadas (Claude Code)

- **chris-lamm-design / Studio OS** — sistema de design replicado pixel-a-pixel do YouTube OS.
- **playwright-site-audit** — screenshots headless de validação a cada deploy.
- **cloudflare / wrangler** — DNS do subdomínio.
- **vercel/fly** — orquestração de deploy.
- **graphify / deep-research** — análise do Notion (Agency OS) e do acervo.
- **AssemblyAI universal-2** — transcrição pt-BR com diarização.
- **Notion API v3** (bot clawdy) — leitura do Agency OS (Meetings DB, Projects, páginas).
- **rclone** (Drive), **ffmpeg** (frames/áudio), **Supabase Storage** (CDN público).
- Padrão **Morfeu333 video-walkthrough** — frames 1/N seg sincronizados com a transcrição.

---

## 7. Histórico (a jornada, do começo)

1. **Catálogo local** — `index.html` lia `calls.json`, filtros por pessoa/projeto, popup com
   walkthrough. Pipeline `process_calls.sh` (rclone→ffmpeg→AssemblyAI→frames).
2. **Cards especiais** — áudios, checklists (projetos/kinbox/brazika) com tarefas marcáveis.
3. **Redesign Studio OS** — tema light navy/cobalt/gold + **views Notion** (Galeria/Tabela/Board/
   Calendário/Volume), ferramentas auto-derivadas.
4. **Online no Fly** — modo `NOLOCAL`, volume, secrets, auto-pull do Drive, `meet.brazika.online`.
5. **Backfill histórico** — catálogo das 112 gravações (dez/25→jun/26), dreno com **cota diária**.
6. **Monitor + auto-cura** — healthcheck, `/api/health`, botão Status, reprocesso de incompletas.
7. **Login/registro** — proteção por cookie, conta `automatrix`.
8. **Links Notion/GitHub** — por projeto (repos brazika) + ingestão das reuniões do Notion como cards.
9. **Métricas, filtro de período** — usabilidade.
10. **Notion 100% automático** — `notion_poll.py` ingere reuniões antigas e futuras sozinho.
11. **Chat assistente com IA (Gemini 2.5-flash)** — busca em linguagem natural com links.
12. **Este repositório** — código + docs, privado, compartilhado com Morfeu333.

---

## 8. Operação

```bash
# Deploy completo (Mac)
bash deploy/fly/deploy.sh

# Logs / estado (precisa flyctl)
flyctl logs --app automatrix-meeting-library
flyctl ssh console --app automatrix-meeting-library -C "tail -20 /data/poll.cron.log"
flyctl ssh console --app automatrix-meeting-library -C "tail -20 /data/notion_poll.log"
flyctl ssh console --app automatrix-meeting-library -C "cat /data/health.json"

# Tunables (sem código): flyctl secrets / fly.toml [env]
POLL_DAILY_MAX   # quantas calls do Drive por dia (default 6)
NOTION_INTERVAL  # frequência da ingestão do Notion (default 1800s)
```

**Pegadinhas conhecidas** (ver memória do projeto): nomes do Meet usam solidus fullwidth `／`
na data; `read` com `IFS=$'\t'` colapsa tabs vazios; `[build].dockerfile` no fly.toml duplica
caminho (usar flag `--dockerfile`); Supabase free 50MB/arquivo (vídeo não cabe); sem whisper
no container (AssemblyAI é obrigatório).
