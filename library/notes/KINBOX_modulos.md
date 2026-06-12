# Kinbox — documentação detalhada por módulos (com proveniência)

**Projeto:** AW Júnior / **Jav Interneg** (análise de crédito imobiliário).
**Pessoas:** Lucas (consultor), Júnior = José A. Verga (dono), **Camila JAV (Garrido)**, Luis Henrique Genda, Marcelo (analista).
**Legenda de fonte:** 📍 `Call · data · momento · [aplicação/ferramenta]`.
Calls: **WA1** = Junior Treinamento WhatsApp 1 (08/jun) · **WA2** = Treinamento WhatsApp 2 (09/jun) · **WA3** = Reunião Junior WhatsApp 3 (08/jun) · **REU05** = Reunião Junior WhatsApp 2 (05/jun) · **ÁUDIO** = Avenida Beira Mar 6 (12/jun).

---

## MÓDULO 0 — O que é o Kinbox (a aplicação por baixo)
- O Kinbox é a aplicação que eles usam pro WhatsApp; "tipo um CRMzinho de WhatsApp". 📍ÁUDIO·12/jun·[Kinbox]
- Por baixo é **Evolution API** (API **não-oficial** do WhatsApp) + **N8N** + interface, empacotados e **hospedados num servidor**. "O Kingbox nada mais é do que Evolution API… um programador criou uma API não oficial do WhatsApp… pegou Evolution + N8N, botou interface e hospeda num servidor." 📍WA3·08/jun·~[Evolution API/N8N]
- É modelo **SaaS pago** (ex.: Evolution ~R$399/mês, N8N ~R$125+/mês) → motivo pra depois **clonar pra VPS própria**. 📍WA3·08/jun·13:45–16:48 · 📍REU05·05/jun·[N8N/Evolution]
- **Webhook de entrada** do Kinbox (doc `atx-share`, criado pelo Júnior): `https://webhook.kinbox.com.br/v3/inbound/BrrcwTfTa`. 📍Drive `atx-share`·[Kinbox webhook]

## MÓDULO 1 — Fonte dos dados (Salesforce)
- Agente lê o Salesforce por **browser (Playwright)** e por **CLI**; a CLI não estava consistente pra puxar → usa o browser. 📍ÁUDIO·12/jun · 📍WA1·08/jun·21:38·[Salesforce/Playwright]
- Salesforce tem **2 aplicativos**: **Repasse** e **Crédito Comercial** (telas/Kanban diferentes; separados pelo campo "tipo de venda"). **Foco = Repasse**; instruir o agente a buscar só repasse e desconsiderar crédito. 📍WA1·08/jun·35:04→49:32·[Salesforce]
- Campos por cliente em **Repasse**: nome do comprador, **CPF**, celular, telefone, e-mail, nome síntese, dias na síntese, estado de aprovação. Fases: triagem, cessão de direitos, repasse, conferência, registro, desembolso, retenção, unidade vendida. 📍WA1·08/jun·49:32·[Salesforce]
- **Estágio gatilho:** decidiram disparar no estágio **"venda nova"** (antes cogitaram "agendar entrevista") pra antecipar o contato. 📍REU05·05/jun·13:51·[Salesforce]

## MÓDULO 2 — O CENÁRIO (workflow dentro do Kinbox) — núcleo
> Lucas: *"Qual que é o esboço do cenário inicial que eu criei?"* 📍**WA2·09/jun·13:13**·[Kinbox/N8N]
1. **Cron job** de X em X min (configurado **20/20 min** na WA2; no ÁUDIO fala 10/10): olha os leads no Salesforce → manda pro **webhook**. 📍WA2·13:13 · 📍ÁUDIO·12/jun
2. **Webhook divisor:** chega um payload com vários leads (15/18/20) → **divide um por um** → envia um a um. 📍WA2·13:13 · 📍ÁUDIO
3. Por lead: **busca o contato** → se NÃO existe, **cria contato + cria conversa**; se existe, busca a conversa; se não há conversa, cria conversa + atualiza contato. 📍WA2·13:13·[Kinbox]
4. **Automação por canal:** ao **criar conversa nesse canal novo**, dispara o **bot**. 📍WA2·13:13·[Kinbox]
5. **Bot:** manda mensagem pro cliente pedindo pra ele **mandar mensagem pro número "repasse"** (número do inbox, API não-oficial) e **adicionar como contato**. 📍WA2·13:13·[Kinbox/WhatsApp]
6. **Padrão de nome** ao salvar contato: **nome + empreendimento + bloco + unidade** (do Salesforce). 📍WA2·09/jun·15:46·[Kinbox/Salesforce]

## MÓDULO 3 — Anti-ban / aquecimento de número (WhatsApp)
- **Por que dá ban:** mandar msg pra quem não te adicionou / não te mandou nas últimas 24h = Meta lê como marketing não-solicitado (ela vende esse serviço). 📍REU05·05/jun·09:34 · 📍ÁUDIO·12/jun·[WhatsApp/Meta]
- **Solução:** a **1ª mensagem sai pelo número da API OFICIAL**; o cliente **adiciona o número não-oficial (do inbox) e manda msg** → abre **janela de 24h** → números autorizados a responder. 📍REU05·05/jun·~05–09min ("vamos criar API oficial… os números vão adicionar o pessoal… quando mandarem msg e adicionarem como contato, aí vão estar autorizados") · 📍ÁUDIO·[WhatsApp]
- Já têm **números pós-pagos "aquecidos"** disponíveis. 📍REU05·05/jun·03:20·[WhatsApp]
- Qual número o cliente adiciona: "tanto faz, quem estiver disponível". 📍REU05·05/jun·[Kinbox]

## MÓDULO 4 — API oficial do WhatsApp / validação do canal (PENDÊNCIA)
- Cadastrou a **API oficial** no Kinbox (botão no site → **logou Facebook → certificou → "deu ok"**) — **mas NÃO está funcionando**. 📍ÁUDIO·12/jun·[Kinbox/Meta]
- Pra o canal **validar**, o Kinbox exige **autorização + cobrança extra (~R$100/canal)** — o **Júnior já autorizou**. 📍ÁUDIO·12/jun·[Kinbox]
- Disparos ainda não rodam "por causa da API oficial / vou verificar se validou o novo canal". 📍WA2·09/jun·17:52·[Kinbox]
- Pelo **MCP não identifica a conexão** com a API oficial cadastrada. 📍ÁUDIO·12/jun·[MCP/Kinbox]

## MÓDULO 5 — MCP / API do Kinbox (limitações)
- Criou o **MCP do Kinbox** a partir da API. 📍ÁUDIO·12/jun·[MCP]
- Só funcionam **endpoints básicos**: mandar mensagem, checar mensagens. **NÃO funcionam:** editar cenários, criar bots. 📍ÁUDIO·12/jun·[Kinbox API]
- Parece existir **API v2/v3** com mais endpoints → investigar. 📍ÁUDIO·12/jun·[Kinbox API]
- Houve uma **call deles com o pessoal do Kinbox** que o Lucas não participou → **pedir essa call pra Camila**; pode falar direto com o **dev do Kinbox**. 📍ÁUDIO·12/jun

## MÓDULO 6 — Contingência (mandar por fora do Kinbox)
- Criar **APIs oficiais do WhatsApp na conta Meta do Lucas**. 📍ÁUDIO·12/jun·[Meta]
- Fluxo: **N8N** → passa pelo filtro do Kinbox → **endpoint envia direto pela API oficial** (ou volta pro N8N e manda). 📍ÁUDIO·12/jun·[N8N/WhatsApp]
- Ter **2 números de API oficial** pra **não depender** do canal do inbox deles. 📍ÁUDIO·12/jun

## MÓDULO 7 — Inbox, usuários e permissões (sistema MOLA)
- O sistema onde a Camila administra = **MOLA** (ela é **master**, cria usuários). 📍WA1·08/jun·62:26→62:38 · 📍WA2·09/jun·17:52·[MOLA]
- Precisa criar um **usuário "analista"** pro agente, senão as mensagens ficam **atribuídas à Camila** no Mola. 📍WA1·08/jun·61:50·[MOLA]
- O usuário criado no Kinbox tem **permissão limitada** (só envio de msg; não cria acessos/automações) → ajustes avançados só pela conta master. 📍WA2·09/jun·10:33→12:26·[Kinbox]
- **Tags e regras** ficam no **inbox** — ex.: **após enviar, transferir a conversa pro Marcelo** (ele acompanha). 📍WA1·08/jun·62:56·[Kinbox inbox]
- **Login principal** a recuperar com a Camila (trocou de PC). A senha **ela enviou pelas mensagens** ("mandei a senha nas mensagens"), **não falou em call** — em REU05 ela diz "deixa eu olhar a senha que eu não lembro". 📍REU05·05/jun·15:59→19:13 · 📍WA1·08/jun·73:02–73:23

## MÓDULO 8 — Checks / follow-up / tags
- NÃO mandar **mensagem repetida** pra quem já recebeu/respondeu. 📍ÁUDIO·12/jun·[N8N/Kinbox]
- Rastrear: o cliente que pedimos pra mandar msg **respondeu?** Se não, **novo disparo no dia seguinte** ("João, adicione o número…"). 📍ÁUDIO·12/jun
- Continua sem responder → **tag "não respondendo"** → tentar outro canal. 📍ÁUDIO·12/jun·[Kinbox inbox]
- **Follow-up de documentação:** automação relembrando o cliente de enviar a documentação. 📍ÁUDIO·12/jun

## MÓDULO 9 — Pós-Kinbox: documentação / gov.br
- Cliente com documentação → **marca call com a equipe** pra ajudar a subir no **gov.br**. 📍ÁUDIO·12/jun·[gov.br]
- Opções pro cliente: **vídeo** ensinando / **call** / **agente** (futuro). 📍ÁUDIO·12/jun
- **Agente futuro:** Playwright sobe os dados no gov.br, espera o **SMS**, insere o **código**, sobe a documentação. Exige **IA LOCAL** (Ollama local, não Cloud) por **compliance/CPF**. 📍ÁUDIO·12/jun·[Playwright/Ollama/gov.br]

## MÓDULO 10 — Roadmap / decisão estratégica
- Objetivo: automatizar a empresa do Júnior **~100%** (análise de crédito, contato mínimo). 📍ÁUDIO·12/jun · 📍REU05·05/jun
- **DECISÃO em aberto:** avançar etapas do Notion **OU** **clonar o Kinbox pra interno** ("Kinbox do Júnior") → não pagar Kinbox; só precisa **API Meta oficial + Evolution**. 📍ÁUDIO·12/jun · 📍REU05·05/jun·09:34 ("planeja clonar a aplicação futuramente")·[Evolution/Meta]
- Estudar a plataforma (agente em paralelo analisando estética/técnica pra clonar). 📍ÁUDIO·12/jun
- Infra: hoje no **PC do Júnior** → migrar pra **VPS 24/7** (N8N + Evolution + API oficial WhatsApp + Chatbot). 📍ÁUDIO·12/jun · 📍REU05·05/jun·[VPS]
- Treinamento da IA do Mola agendado (Camila) e Lucas vai **ensinar a IA a usar o Kingbox** (criar grupo, enviar msg, gerenciar). 📍REU05·05/jun·50:55→56:31·[MOLA/Kinbox]
- Incentivo dito no áudio: trazer o Kinbox pra interno = "garante salário de **R$8 mil/mês**". 📍ÁUDIO·12/jun

---

### Aplicações/ferramentas citadas
**Salesforce** (CRM fonte) · **Playwright** (raspagem browser) · **Salesforce CLI** · **N8N** (automação) · **Kinbox** (= Evolution API + N8N, WhatsApp) · **MOLA** (sistema/inbox da Camila) · **Meta / WhatsApp API oficial (Cloud)** · **MCP do Kinbox** · **Chatwoot** (CRM mensageria, modelo) · **gov.br** · **Ollama local** (compliance) · **VPS**.

### Pendências imediatas (ordem)
1. Recuperar login principal do Kinbox com a Camila (grupo).
2. Validar o canal da API oficial (dev Kinbox + a call) — Júnior já pagou.
3. Investigar API v2/v3 (editar cenários / criar bots).
4. Contingência: 2 números API oficial por fora do Kinbox.
5. Checks/tags + follow-up de documentação.
6. Decidir clonar Kinbox pra interno × avançar etapas do Notion.
