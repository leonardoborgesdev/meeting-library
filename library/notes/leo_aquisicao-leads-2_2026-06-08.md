# Reunião Automatrix — Interna — Agentes de Aquisição de Leads 2

- **Data:** 2026-06-08
- **Pessoa (lib):** Leonardo
- **Participantes:** Lucas F. N. Alves, Brazika Brasil (Leo), henrike Augusto
- **Projeto:** Automatrix Lead System (scraper FB + SDR)
- **Vídeo (Drive):** https://drive.google.com/file/d/1y4zsvDdQ-ZafOJfI5f-wrzRLg4nygFlF/view (429 MB)
- **Notas Gemini (PT):** doc 1C2XokSMi4Wc0Ff7WDd26C6gWOEoIw8ystsZUr04djGg

## Resumo
Revisão da automação de leads e integração de modelos com centralização dos repositórios de código.

- **Status da geração de leads:** validada a geração de 47 leads via automação; problemas no driver do Chrome (CDP) durante interações. Modelos usados: GPT-4.1 Mini e Claude 3.5/4.6 Sonnet.
- **Centralização de arquivos:** todos os arquivos de config e repositórios GitHub devem ficar num local centralizado para reprodutibilidade.
- **Padronização do ambiente:** scraper estável usando Chrome + repositório ORIGINAL (evitar Opera, que quebrava). Funções distribuídas para organizar o banco de dados e as apresentações de vídeo.

## Próximas etapas
- [Leo] Enviar relatório CSV diário dos leads capturados.
- [Leo] Documentar projetos: salvar repos GitHub e arquivos no Notion.
- [Grupo] Criar banco de dados para o SDR com todas as aplicações e apresentações.
- [Henrique] Produzir vídeos de apresentação das aplicações.
- [Grupo] Mapear grupos do Facebook em tabela para ranking e análise de qualidade.
- [Lucas] Ajustar Codex para melhorar criação de apresentações e atualizar app de quiz.
- [Leo] Ampliar sistema de captura de leads e documentar o processo.

## Detalhes-chave
- 47 leads capturados, 6 DMs enviadas; execuções confirmadas rodando via OpenCloud no Xeon (cloud), não local.
- Discussão sobre lastro/rastreabilidade por lead (quem/de onde/qual prompt/qual modelo).
- Gargalo confirmado = a LLM (token vencendo derruba tudo), não o código.
- Scraper estável só com Chrome + repo original; Opera causou falhas.
