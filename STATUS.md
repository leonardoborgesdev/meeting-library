# STATUS — Meeting Library (Leonardo × Nicolli)

Refeito do zero em 2026-06-11, vasculhando o Drive (conta `lucas@automatrix-ia.com`) de novo.

## Os 2 repositórios do Morfeu333 (clonados exatamente como são)
- **`meeting-library`** (este repo) — galeria HTML filtrável. **Usado como base**: o `index.html`
  foi reescrito pra ler `data/calls.json` e filtrar por **pessoa / projeto / assunto** (antes era
  hard-coded só com as calls do Chris Lamm).
- **`video-walkthrough-skill`** (em `~/Desktop/video-walkthrough-skill`) — o SKILL.md com o pipeline
  do Lucas (comprime CRF18 → extrai áudio → transcreve → frames → walkthrough). **Usado como receita**:
  virou `scripts/process_calls.sh`, com **uma troca**: AssemblyAI → **whisper.cpp local** (`whisper-cli`
  + `ggml-medium`), porque a key da AssemblyAI não está acessível aqui e o whisper roda offline em pt-BR.

## Como as calls foram separadas
Por pessoa (manifesto `data/calls.json`, filtro no index):
- **Leonardo** (5): Aquisição de Leads #2, #3, Saulo SDR + Junior WhatsApp 1 e 2 (Junior posto no Leo por sua instrução).
- **Nicolli** (5): Treinamento Intro, Leads, Atendimento (02/04 e 07/04) e Lucas & Nikolli.

Cada call tem: quem, assunto(s), projeto, participantes, ID do vídeo no Drive, nota Gemini e (após o pipeline) transcrição.

## Pipeline (padrão pedido: comprimir → extrair áudio → transcrever)
`scripts/process_calls.sh` faz, por call: baixa do Drive por ID (rclone, **apaga e baixa de novo**) →
comprime CRF18 sem perda perceptível → extrai WAV 16k mono → transcreve pt-BR (whisper, `.txt`+`.srt`) →
apaga o RAW e o WAV (mantém o `.mp4` comprimido + transcrição) → atualiza o `calls.json`.

## ⛔ Único bloqueio (precisa de você, é interativo)
O token do rclone está vazio. Rode no **Terminal de verdade** (abre o navegador pra login Google):
```
rclone config reconnect gdrive:
```
Depois é só:
```
cd ~/Desktop/meeting-library && bash scripts/process_calls.sh
```
(ou uma call só: `bash scripts/process_calls.sh nicolli_02_treinamento-leads`)

## Notas
- **N2 e N3 (Nicolli)** não têm resumo do Gemini (ele transcreveu PT como inglês) → são prioridade pro whisper.
- **N4 (Nicolli, 07/04)** tem ~**7h33** e o Leonardo Borges participa → o script usa modelo `small` em calls longas; ainda assim demora, melhor rodar à noite.
- Ver a galeria: `cd ~/Desktop/meeting-library && python3 -m http.server 8009` → http://localhost:8009
