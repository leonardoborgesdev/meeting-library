# Meeting Library ("Meet") — Automatrix

Painel que **entra automaticamente nas suas calls do Google Meet, transcreve, resume e organiza tudo** num só lugar.

**Live (produção):** https://meet.automatrixapps99x.win

## O que é
Um bot (Vexa) entra nas reuniões do Google Meet agendadas no seu Google Calendar, grava e transcreve (Groq Whisper), uma etapa de IA gera resumo/insights, e um painel web (Meeting Library) mostra tudo — vídeo, áudio, transcrição, resumo e até apresentação gerada.

## Arquitetura (resumo)
```
Google Calendar (a conta que RECEBE as calls)
      │  control.py (autojoin) acha os links meet.google.com
      ▼
   VEXA  (docker: vexa-lite + postgres + minio)  ──►  entra na call, grava, transcreve (Groq Whisper)
      │
      ├─►  brain_ctr.py  → resume/insights (Groq / Cerebras / Gemini)
      ▼
MEETING LIBRARY (scripts/server.py, :8011)  → painel web (login) com todas as calls
      └─ media/transcript em /library, sync opcional Supabase/Teldrive
```

## Componentes
| Parte | Onde | O que faz |
|---|---|---|
| **Vexa** | `vexa-lite/compose.yaml` | Bot que entra na call + transcreve. Imagem `vexaai/vexa-lite`. |
| **Autojoin** | `vexa-lite/control.py` + `autojoin.env` | Vigia o Google Calendar e manda o Vexa entrar. **← define QUAIS calls.** |
| **Brain** | `vexa-lite/brain_ctr.py` + `brain.env` | Resumo/insights por IA. |
| **Meeting Library** | `meeting-library/scripts/server.py` + `.env` | O painel web (:8011). |

## Duplicar / trocar as calls
Ver **[REPLICATION.md](REPLICATION.md)**. Resumo: sobe a mesma stack e troca **só** o `autojoin.env` (a conta Google cujo calendário será vigiado). Todo o resto é idêntico.

## ⚠️ Segredos
Nenhuma chave real está neste repo. Cada `*.env.example` lista o que preencher e onde pegar. Os `.env` reais ficam só no servidor (estão no `.gitignore`).
