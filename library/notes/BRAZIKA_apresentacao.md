# Brazika — Apresentação do Painel (Call Leo × Lucas)

**Data:** 12/06/2026 14:54 · **Quem apresenta:** Leo (Brazika Brasil) · **Para:** Lucas (Automatrix)
**Fontes:** Anotações do Gemini (PT) + Transcrição da call. *(O vídeo Recording ainda não estava no Drive — só as Anotações do Gemini PT/EN. Quando subir, o auto-pull cataloga o card de vídeo sozinho.)*

> **Resumo (Gemini):** A apresentação abordou integrações operacionais, automação de marketing, métricas de desempenho e novos protocolos de segurança comercial. O painel centraliza rastreamento de eventos, automação de redes sociais e métricas de campanhas, consolidando pagamentos e logística. Atendimento via WhatsApp com respostas automáticas; captura de e-mail com cupom; segmentação de leads por etiquetas. Funcionalidade de segurança monitora sites em tempo real contra clonagem. Desenvolvimento futuro foca em agentes de IA para gerenciamento centralizado.

---

## O que o Leo mostrou (na ordem, com timestamp)

| ⏱ | Módulo | O que foi demonstrado |
|----|--------|------------------------|
| 00:00 | **Site de vendas + link da bio** | Loja que sai do link da bio do Instagram, integrada direto ao painel; todo botão tem rastreamento embutido. |
| 00:55 | **Feed de eventos (tempo real)** | "Visualizou a página", tempo de permanência ("faz 20s que abri"), clique em produto — jornada do cliente visível no painel. Customizável conforme a cliente. |
| 02:09 | **Automação Instagram** | DM do Instagram ativa: responde o comentário no post e manda direct pra pessoa; captura o lead (cidade, intenção). (Bot do WhatsApp existia mas está desativado.) |
| 02:39 | **Postagem automática** | Instagram integrado à Meta: Reels + Stories automáticos 24/7, online, sem depender de máquina local. **25 conteúdos postados, 86 ainda agendados**, com legenda e hashtag. |
| 04:03 | **Painel da Meta (métricas)** | Resumo do dia (gasto ~R$7), origem do tráfego, eventos. Edição das campanhas é pelo cloud — no painel é **visualização**. A função tinha sido desabilitada por ele. |
| 05:27 | **Chatbot WhatsApp** | Atendimento semi-humanizado: menu de início, FAQ, rastreio de pedido (responde "meu pedido" com link/código). Integrável ao site. **Falta alimentar os scripts** (responde padrão demais). |
| 09:48 | **Captura de e-mail + cupom** | Pessoa pede cupom → preenche e-mail → sistema captura o e-mail e dispara o cupom automático. (Bug: foto do produto não puxando do storage.) |
| 10:43 | **Checkout (compra simulada)** | Integrado ao **Envio.com** (cotação real de frete + gera etiqueta automática após pagamento) e ao **Efi Bank** (Pix + cartão). Gerou Pix fake real que cai direto no banco. |
| 12:30 | **Atribuição no painel** | Notificação "checkout iniciado", capturou contato/pagamento e a **origem do tráfego desde o link da bio**. |
| 13:07 | **Pendência do bot** | Reconheceu que o script do bot é só base; tem que alimentar com mais informação. |
| 15:14–22:58 | **Reativar painel Meta** | Reativou o gerenciador de anúncios integrado; campanhas, criativos, funil. Ideia de **scraper de browser** dos concorrentes em cron pra clonar a plataforma de métricas deles. |
| 17:09–18:29 | **Agentes de IA (Open Cloud)** | Plano: trazer pro painel agentes (estilo OpenClaw/Llama no Fly) — um chat com agentes que gerencia Meta Ads e calendário sem depender do Cloud Code nem de outro painel. |
| 19:07 | **Qualificação de leads** | Etiquetas separam contatos por interação (ex.: quem respondeu mensagem no grupo). Limite técnico: não dá pra saber se a pessoa adicionou o número aos contatos. |
| 24:34–25:57 | **Métricas por criativo** | Métrica geral (total gasto, ações, checkouts iniciados) + funil (60K impressões, 5K cliques) + por criativo (impressões, alcance, CTR, CPC, ROAS) + **preview de como o anúncio aparece no feed do cliente**. Sem vendas no período → ROAS não calcula. |
| 26:35 | **Catálogo + Instagram Shopping** | Atualizar produto no site reflete automático no catálogo da Meta e no Instagram Shopping (marcação de produto nas fotos). |
| 27:04 | **Configurações / APIs** | Lista das integrações: Efi (pagamento, com doc e taxas), Envio (logística), Meta (ads/catálogo), Instagram (perfil/media/insights). |
| 27:34–30:13 | **Segurança anti-clonagem** | Em implantação: monitora sites em tempo real. Recentemente um clone copiou a loja inteira (checkout + nome de domínio); ele identificou e derrubou (brazikaoutlet → "Derrubado"). Proteção anti-hotlink ativa; lista todos os domínios conectados ao domínio principal e alerta se surgir um novo na indexação do Google. |

---

## Próximas etapas (as 3 que o Gemini destacou)

1. **[Brazika] Atualizar Bot** — melhorar a configuração do bot de atendimento, incluindo mais informações nos scripts de resposta.
2. **[Brazika] Reativar Painel** — habilitar o painel da Meta no sistema para acompanhar anúncios e métricas de desempenho.
3. **[Brazika] Integrar Agentes** — adicionar agentes inteligentes ao painel para gerenciar e editar campanhas direto na plataforma.

> Tasklist completo e marcável na aba **Checklist** do card (`clkey: brazika`).
