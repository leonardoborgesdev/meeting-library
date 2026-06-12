# ð Observações  

 jun. 10, 2026

## Reuniao Automatrix - Interna - Agentes de Aquisicao de Leads 3

convidado <leooborges20@gmail.com> [Lucas F. N. Alves](mailto:lucas@automatrix-ia.com) <suportebrazika@gmail.com>

Anexos [Reuniao Automatrix - Interna - Agentes de Aquisicao de Leads 3](https://calendar.google.com/calendar/event?eid=NHI3YmIzam5tc3RzMW5raGxva3M2OG5hZ2QgbHVjYXNAYXV0b21hdHJpeC1pYS5jb20)

Registros da reunião [Transcrição](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?usp=drive_web&tab=t.x2zt52m31pqv) [Gravação](https://drive.google.com/file/d/1wz3MY2j8VYtITE2eYLQB4TGqtJHZPUer/view?usp=drive_web) [Anotações do Gemini (Inglês)](https://docs.google.com/document/d/1DV_U4mqayUqQ1jbiOtfk0bOlDgvdC0oqrloPcUBttXg/edit?usp=meet_tnfm_email) 

  
  

### Resumo

Reunião de alinhamento técnico foca na migração para nuvem, otimização de agentes inteligentes e estruturação de dados.  
  
**Infraestrutura e Migração Cloud**  
A equipe centralizou a operação dos agentes na VPS para garantir estabilidade e performance. A decisão estratégica foi migrar para o Ollama Cloud visando maior eficiência operacional.  
  
**Refinamento de Agentes IA**  
O foco ajustou-se para classificar corretamente leads e evitar interações repetitivas de spam. Implementaram o uso de histórico de chamadas via RAG para padronizar respostas dos agentes.  
  
**Estruturação do Projeto Automatrix**  
O projeto Automatrix organizará fluxos de trabalho no Notion utilizando transcrições de reuniões anteriores. A análise de dados será aprimorada com ferramentas de indexação avançada para suporte às decisões.

  
  

### Próximas etapas

  - \[Brazika Brasil\] Compartilhar Credenciais VPS: Enviar os dados de acesso da infraestrutura VPS para possibilitar a auditoria e análise do sistema.
  - \[Lucas F. N. Alves\] Enviar Link Notion: Compartilhar o link do documento do Notion utilizado para permitir a correção do fluxo de captura de leads.
  - \[Brazika Brasil\] Enviar HTML: Encaminhar o código HTML da interface atualizada por e-mail para o colaborador.
  - \[Lucas F. N. Alves\] Configurar Conta Ollama: Realizar a assinatura da conta no Ollama Cloud e fornecer as credenciais para acesso compartilhado.
  - \[Lucas F. N. Alves\] Enviar Documento Modelo: Enviar o documento modelo para que a estrutura de pipeline de leads possa ser replicada corretamente.
  - \[O grupo\] Criar RAG SDR: Desenvolver a base de conhecimento RAG para o agente de SDR com o intuito de qualificar as respostas e automações.
  - \[Lucas F. N. Alves\] Gravar Instruções SDR: Registrar instruções detalhadas e exemplos de uso na tela para facilitar a criação do RAG pelo colaborador.
  - \[Lucas F. N. Alves\] Otimizar Leads: Adicionar detalhes dos leads extraídos na interface para permitir a filtragem por data de captura.
  - \[Lucas F. N. Alves\] Ajustar Agente: Configurar o agente de automação para evitar comentários duplicados em posts e enviar links de vídeo em vez de arquivos brutos.
  - \[Lucas F. N. Alves\] Refazer Recruta Sis: Redesenhar a aplicação de recrutamento para servir como base de dados centralizada de vagas e candidatos.
  - \[Brazika Brasil\] Criar Plataforma: Desenvolver a estrutura de gestão de vagas e criar uma aba dedicada para classificar novas oportunidades de contratação.
  - \[Brazika Brasil\] Desenvolver Scrapers: Implementar scrapers para capturar o design do sistema e integrar automaticamente os novos dados de contratação.
  - \[O grupo\] Registrar Projeto: Organizar todos os projetos e transcrições de videochamadas no Notion para consolidar o ecossistema de aquisição e atendimento de leads.
  - \[Brazika Brasil\] Analisar Chamadas: Explorar o conteúdo das videochamadas, realizar transcrições detalhadas com a ferramenta Assembly e criar prompts otimizados para os agentes.
  - \[Lucas F. N. Alves\] Enviar Dados: Compartilhar as configurações e automações do WhatsApp do cliente após a conclusão da estruturação do banco de dados.

  
  

### Detalhes

*Did the screenshots in this section make your notes* [*better*](https://goo.gle/44IH7J9) *or* [*worse*](https://goo.gle/4b5ZWtJ)*?*

  - **Autenticação e Acesso ao Sistema**: Lucas F. N. Alves e Brazika Brasil realizaram a configuração de acesso à Open Cloud, validando o uso de tokens do Google e credenciais da VPS para garantir a autenticação correta do sistema ([00:00:00](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.e6uq5ppd34b6)). O foco inicial foi garantir que os agentes pudessem operar na VPS, transferindo a carga de trabalho que antes estava sendo processada localmente em um computador Mac ([00:02:21](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.ikr4qej52eql)) ([00:05:47](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.ojfaurhmimsf)).
  - **Status da Operação dos Agentes**: O sistema está atualmente centralizado na VPS, utilizando diversas ferramentas como CamoFox, Playwright, Chrome CDP e Ollama, sendo que o modelo de IA foi alternado entre Gemini e Codex devido a limites de uso semanal do Ollama ([00:05:47](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.ojfaurhmimsf)). Brazika Brasil confirmou que o fluxo de captura de leads do Facebook está operacional, com ajustes para priorizar posts mais recentes em vez de publicações antigas ([00:06:53](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.weulmi5i2pqy)).
  - **Monitoramento de Leads no Notion**: A equipe discutiu o funcionamento da integração com o Notion, onde os leads são registrados após a extração ([00:06:53](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.weulmi5i2pqy)) ([00:11:53](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.g7dbodhmq4ta)). Lucas F. N. Alves solicitou revisões na captura, pois notou inconsistências no registro de comentários postados e de mensagens enviadas (DMs), embora o sistema esteja conseguindo interagir com os perfis identificados como relevantes ([00:08:19](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.7zmh0oejy6q5)) ([00:11:53](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.g7dbodhmq4ta)).
  - **Desenvolvimento da Interface de Usuário**: Brazika Brasil apresentou uma interface (HTML mockup) integrada ao sistema, permitindo visualizar em tempo real o chat, ações realizadas (comentários, DMs) e rascunhos de e-mails ou WhatsApp ([00:16:42](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.qbsn8qqe4e8d)). Lucas F. N. Alves validou o layout e discutiu a necessidade de exibir o conteúdo gerado de forma clara para melhorar o gerenciamento do SDR ([00:17:51](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.s44tlyh0q808)).
  - **Avaliação do Ollama Cloud**: Após analisarem as limitações dos modelos atuais, ambos concordaram em migrar para o Ollama Cloud, que oferece acesso a múltiplos modelos open source na nuvem, eliminando a necessidade de processamento pesado localmente ([00:21:51](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.f1988rxo8osw)). Essa mudança visa aumentar a eficiência e contornar restrições de limite de uso de outras plataformas ([00:23:07](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.kar894i6mq5j)) ([00:45:36](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.9j80etcn6cdw)).

  - **Agendamento da Reunião de Telemedicina**: Lucas F. N. Alves organizou a agenda para uma reunião às 15:00 com Maurício, focada em telemedicina ([00:25:18](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.32ucv6478c0l)). Foi definido que o foco técnico deve ser mantido, evitando discussões sobre valores, e que Leonard será convidado para tratar da segurança e gestão de equipe, garantindo que o tema da licitação permaneça separado da discussão técnica ([00:26:18](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.c3d0ypsvpw32)).
  - **Seleção de Modelos de IA e Hardware**: Houve uma discussão técnica sobre os modelos de IA, com menções ao Qwen 3 VL e Mini CPM ([00:28:40](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.rf1pd5z32o5g)). Eles avaliaram a viabilidade de rodar modelos locais versus cloud, concluindo que, para o projeto atual, a nuvem é mais eficiente, embora planejem investir em hardware robusto para futuras implementações locais ([00:30:37](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.al7v7lsuxbw3)).
  - **Definição de Estratégia para Leads (Pipeline)**: Lucas F. N. Alves detalhou a classificação dos tipos de oportunidades em "Partnership" (parceria), "Hiring" (contratação de pessoal) e "Project" (projetos sob demanda) ([00:34:47](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.owclti35m0vn)). Eles concordaram que a estratégia de abordagem deve variar conforme a categoria: "Partnership" será tratado como uma oportunidade de baixo foco, enquanto "Project" é o tipo de demanda prioritária para o negócio ([00:36:01](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.x8f90m7fueq2)) ([00:39:11](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.958jaeswa5as)).
  - **Qualificação de Leads e Refinamento do Sistema**: A equipe revisou exemplos reais de posts para treinar a lógica de classificação dos agentes, diferenciando claramente o que é uma oportunidade de projeto de uma vaga de emprego ([00:37:45](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.1rrcot1kpda9)). Foi decidido que é necessário ajustar o agente para identificar corretamente esses perfis, evitando que o sistema envie propostas inadequadas ([00:39:11](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.958jaeswa5as)) ([00:51:12](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.gf4gfivub7o6)).
  - **Otimização da Automação de Conteúdo**: Foi discutido o problema de spam, onde o agente comentou repetidamente no mesmo post ([00:47:22](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.6uttlpcvc39o)). Lucas F. N. Alves propôs que o sistema envie links de vídeos de demonstração em vez de comentários extensos, garantindo uma abordagem mais profissional e evitando comportamentos repetitivos dos agentes de automação ([00:48:10](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.luq884j5p8re)).
  - **Utilização de Dados Históricos para Treinamento (RAG)**: Para melhorar a precisão das respostas dos agentes, Brazika Brasil iniciou a extração de históricos de chamadas anteriores, especificamente das reuniões com Nicole, utilizando as transcrições e anotações como base de conhecimento. Essa estratégia visa alimentar um sistema de RAG (Retrieval-Augmented Generation) para que o agente saiba responder de forma alinhada ao padrão da empresa ([00:52:20](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.k85ovwpp033z)) ([00:54:08](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.n08fdjvki4e8)).
  - **Localização de Gravações de Chamadas**: Lucas F. N. Alves e Brazika Brasil discutiram a ausência de registros de certas reuniões, resultando na identificação de sete chamadas específicas ocorridas entre 26/03 e 30/04. Brazika Brasil confirmou a localização e o envio dos links dos documentos e transcrições correspondentes via WhatsApp e Google para que a análise fosse viabilizada ([00:58:34](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.cuarhl4q3t4)).
  - **Objetivo da Análise de Chamadas**: O objetivo central da análise é capacitar Brazika Brasil a compreender profundamente as interações com clientes para aprimorar as respostas, tanto em comentários públicos quanto no gerenciamento administrativo. Lucas F. N. Alves orientou a utilização do NotebookLM, que já contém materiais de treinamento, para auxiliar na criação de \*prompts\* e no refinamento da comunicação dos agentes ([01:01:20](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.czu3wyushnvn)).
  - **Integração Técnica e Acesso aos Dados**: Lucas F. N. Alves e Brazika Brasil estabeleceram a necessidade de integração de fontes, incluindo o uso do NotebookLM e possíveis conexões via API ou MCP ([01:02:55](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.xqkibru6r6t4)). Foi confirmado que Brazika Brasil obteve acesso aos arquivos e pastas do projeto, incluindo materiais relacionados ao projeto de "face" e ao ecossistema de aquisição e atendimento de \*leads\* ([01:05:10](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.rxp6pyb8vws5)).
  - **Estruturação do Projeto Automatrix**: Lucas F. N. Alves destacou que o "projeto Automatrix" envolverá a organização de todos os fluxos de trabalho e arquivos de vídeo no Notion ([01:06:37](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.cdrmdc4atkni)). A meta é criar apresentações estruturadas para cada iniciativa, como a de aquisição de \*leads\*, utilizando a base de dados formada pelas chamadas para alimentar e configurar os agentes de inteligência artificial de forma consistente ([01:09:23](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.72t9ksy696h2)).
  - **Tarefas Imediatas de Processamento de Chamadas**: Para o curto prazo, Brazika Brasil deve explorar as chamadas, criar \*prompts\* e desenvolver instruções aprimoradas para os agentes, evitando, contudo, alterações nas configurações atuais desses sistemas neste momento ([01:09:23](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.72t9ksy696h2)) ([01:11:38](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.rf4wot138jgz)). Lucas F. N. Alves se comprometeu a enviar a gravação da chamada atual para que o processo de organização e estruturação de uma base de dados métrica seja formalmente iniciado ([01:10:43](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.go6nb9vzan13)).
  - **Ferramentas de Transcrição e Indexação**: Foram discutidas estratégias para a gestão das gravações, incluindo uma aplicação de indexação desenvolvida por Lucas F. N. Alves, que salvará os \*frames\* na memória, e uma organização no GitHub iniciada por Iara ([01:10:43](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.go6nb9vzan13)). Brazika Brasil utilizará a \*skill\* "video walkthrough" para gerar transcrições via Assembly, garantindo a captura precisa de \*timestamps\* e \*frames\* para uma análise superior à oferecida pelas transcrições padrão do Google ([01:11:38](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.rf4wot138jgz)).
  - **Feedback de Desempenho e Próximos Passos**: Brazika Brasil solicitou um \*feedback\* sobre o trabalho realizado, e Lucas F. N. Alves indicou que o desempenho está adequado, reforçando apenas a necessidade de maior organização na gestão do projeto a longo prazo. O planejamento futuro envolve a transição para projetos focados em telemedicina e automação via WhatsApp, os quais serão abordados assim que a estruturação da base de dados atual estiver concluída e funcional ([01:14:36](https://docs.google.com/document/d/1zxyOWCTJueAMDQ4fuarxEFKM7so44PtDxX3AxM9Dmxo/edit?ouid=101907048426152034943#heading=h.o17qon9s4fxn)).

  
  

*Revise as anotações do Gemini para checar se estão corretas.* [*Confira dicas e saiba como o Gemini faz anotações*](https://support.google.com/meet/answer/14754931)

*Como está a qualidade de* ***destas observações?*** [*Responda a uma breve pesquisa*](https://google.qualtrics.com/jfe/form/SV_9vK3UZEaIQKKE7A?confid=emlaqaOHkNF-A4TR71npDxISOAIIigIgABgFCA&detailid=standard&screenshot=true) *para nos dar seu feedback, incluindo o quanto as observações foram úteis para o que você precisa.**  
*

# ð Transcrição*  
*

 jun. 10, 2026

## Reuniao Automatrix - Interna - Agentes de Aquisicao de Leads 3 - Transcrição

### 00:00:00

  

**Lucas F. N. Alves:** para Ó, tem um carregador e a nome

**Brazika Brasil:** Deix o carregador aqui em casa,

**Lucas F. N. Alves:** da Ah,

**Brazika Brasil:** mano. Eu vi lá na cama lá onde você tava

**Lucas F. N. Alves:** pode ser.

**Brazika Brasil:** dormindo.

**Lucas F. N. Alves:** Carregar. Você quer mostrar aí o negócio seu ou você quer que eu vejo aqui?

**Brazika Brasil:** Vou compartilhar aqui.

**Lucas F. N. Alves:** Você matou lá? Matei. Vou fazer

**Brazika Brasil:** Tá aparecendo a tela

**Lucas F. N. Alves:** outro.

**Brazika Brasil:** aí? Aí,

**Lucas F. N. Alves:** Uhum.

**Brazika Brasil:** qual que é a senha?

**Lucas F. N. Alves:** Qual que é a senha para logar no que que você tá

**Brazika Brasil:** é no seu

**Lucas F. N. Alves:** falando?

**Brazika Brasil:** Gmail minúsculo.

**Lucas F. N. Alves:** Ah, tá. Eh, lu pera, deixa eu te mandar aí no zap.

**Brazika Brasil:** Kinh M.

**Lucas F. N. Alves:** Так.

**Brazika Brasil:** Só confirmar aí agora.

**Lucas F. N. Alves:** Ver se eu consigo te dar acesso a Open Cloud.

**Brazika Brasil:** Eu vou p lá do chão.

**Lucas F. N. Alves:** Achei um também.

  
  

### 00:02:21

  

**Brazika Brasil:** Eu tenho. Tem. É,

**Lucas F. N. Alves:** Você tem,

**Brazika Brasil:** é por ele que eu peguei a base tudo desde do começo lá. Quando eu compartilho,

**Lucas F. N. Alves:** mas você consegue, pera, você consegue logar nesse aqui?

**Brazika Brasil:** é o que tá os agentes do Face.

**Lucas F. N. Alves:** Falar interface.

**Brazika Brasil:** Ah, pera aí, deixa eu ver. É, chegou alguma coisa do Google?

**Lucas F. N. Alves:** Chegou. Deixa eu confirmar aqui também.

**Brazika Brasil:** O pentual abriu o teu pactado

**Lucas F. N. Alves:** Abriu aí. Ah, então você tá Ah,

**Brazika Brasil:** pel É só que deu autenticação requerida. Pedi um token aqui do get,

**Lucas F. N. Alves:** beleza. Eu te mando o token aí. Pera aí.

**Brazika Brasil:** mas é porque eu tô na no teu esquerdo da VPS, então qualquer coisa aí local da VPS eu acesso aqui.

**Lucas F. N. Alves:** Entendi. Eu achei que você não tava no que talvez você não tava no coisa ainda. Quer ver? Eh, esse token aí, ó.

  
  

### 00:03:57

  

**Lucas F. N. Alves:** Bom,

**Brazika Brasil:** Boa.

**Lucas F. N. Alves:** open c Da hora, mano.

**Brazika Brasil:** Ah, o Google foi. Depois eu vou extrair os mits aqui.

**Lucas F. N. Alves:** Santo

**Brazika Brasil:** Abrir aqui no mission control. Um minuto.

**Lucas F. N. Alves:** Pera aí que eu vou te mostrar aqui que você direitinho. Hum. Ó, baixando aqui, Léo. Deixa eu mostrar minha tela. Você quer mostrar os seus agentes funcionando aí também antes?

**Brazika Brasil:** para mostrar o quê? O seu nome, como é que é?

**Lucas F. N. Alves:** Eu vou te mostrar. Me mostra aí os seus funcionando que eu te mostro depois o que você tem que fazer.

**Brazika Brasil:** Tá, eu vou dar uma outra aqui.

**Lucas F. N. Alves:** Acho que nem precisa rodar outra run não. Só se me explicar mesmo os trem. Se você quiser ver mesmo, posso ir vendo aqui no noion. Mas isso aí no caso então tá rodando no seu PC, é a sua versão do negócio do convex,

**Brazika Brasil:** É, então per tá rodando na naquela VPS.

**Lucas F. N. Alves:** né?

  
  

### 00:05:47

  

**Brazika Brasil:** Você lembra que a gente pegou uma VPS que você tinha pedido para instalar o Pencloud Suprobase?

**Lucas F. N. Alves:** Eu

**Brazika Brasil:** Eh, já tá com a VPS parado aí, não sei se você lembra.

**Lucas F. N. Alves:** lembro a

**Brazika Brasil:** Então, aí tá tudo rodando nela agora. Tipo, não tem nada rodando no meu no meu Mac, tá? O sistema tá rodando lá inteirinho lá. É aqui, ó, onde roda, roda no Mac. Tava rodando no Mac, agora tá usando usando a VPS ali no sei lá que é aquela tava parada. Aí, o cérebro é o Codex, o lama e tá o Gemini. Só que hoje, hoje o olama deu o limite lá tem limite semanal, mesmo sendo grátis tem limite semanal.

**Lucas F. N. Alves:** M.

**Brazika Brasil:** E o meu codex volta amanhã porque também deu o limite. Aí ele fez pelo pelo Gemini hoje. Essa análise aqui, ó. Dois L capturado, um comentário, duas RS, duas DM. Cadê? Captura Camofox igual original. Facebook, ele puxou aqui do meu Mac e jogou lá. Eu criei o bagulho da senha lá do Messenger também.

  
  

### 00:06:53

  

**Lucas F. N. Alves:** Hm.

**Brazika Brasil:** Aí tem uns três agentes aí. Está Camo Fox, Playwite, o Chrome CDP, o Pencloud, o Olama, só que hoje ele tá fora, ele vai volotar só semana que vem. Essa aqui é a base normal. Evolute também já tá conectado com o seu número aqui. Eu só não coloquei para ele mandar mensagem porque vai que sei lá ban seu número aí. Aí não tem como você recuperar ele depois. Como funciona? Captura de leadsfox rola os feeds lá. Aí eu ajustei ele para pegar os feeds mais eh uns post mais recente. Ele tava pegando posto bem antigão. Aí o post que ele respondeu hoje que é esse daqui, ó. Ele é de foi hoje o posto de hoje aqui, ó. 7 horas atrás. Aí ele respondeu há uma hora atrás.

**Lucas F. N. Alves:** E ele tá salvando isso aí no Não.

**Brazika Brasil:** O noel. Deixa eu abrir aqui o

**Lucas F. N. Alves:** M.

**Brazika Brasil:** no. Espera aí carregar. Vou botar aqui. Ele extrai os posts dos compradores. Tipo, ele tá seguindo a base do celular que você programou.

  
  

### 00:08:19

  

**Lucas F. N. Alves:** Deixa eu ver aqui como que tá

**Brazika Brasil:** Dá uma ideia. Tá. A tentar abrir no

**Lucas F. N. Alves:** Ш.

**Brazika Brasil:** filme.

**Lucas F. N. Alves:** Como é que é o nome dessa cliente aí?

**Brazika Brasil:** Esse é que comentou. Foi esse daqui, ó.

**Lucas F. N. Alves:** Deixa eu ver lá naquele Facebook de novo. Princess Vincent Go High Level Funnels.

**Brazika Brasil:** Princess

**Lucas F. N. Alves:** Deixa eu ver se acho.

**Brazika Brasil:** Princess Vince, deixa eu ver no Achou.

**Lucas F. N. Alves:** Achou. Achou.

**Brazika Brasil:** Tá completinho aí ou faltou alguma coisa? Cadê? Deixa eu ver.

**Lucas F. N. Alves:** Comentário postado. Ele comentou alguma coisa para comentário postado.

**Brazika Brasil:** Aumentou aqui, ó.

**Lucas F. N. Alves:** Não, DM enviada também

**Brazika Brasil:** Ah, ele não enviou só, ele só comentou nesse aí.

**Lucas F. N. Alves:** não.

**Brazika Brasil:** DM, ele ele só envia para quem acha que é interessante, né, que tá configurado. Então ele não mandou DM.

**Lucas F. N. Alves:** Mas ele comentou.

  
  

### 00:09:39

  

**Brazika Brasil:** Comentou aí na tela aí, ó. Leonardo Borges, comentário de uma hora atrás.

**Lucas F. N. Alves:** Hum, ele não registrou aqui no no comentário, mas beleza,

**Brazika Brasil:** Tá,

**Lucas F. N. Alves:** tá ótimo.

**Brazika Brasil:** então vou ajustar isso. E agora tem a parte do Messenger.

**Lucas F. N. Alves:** Pera aí, deixa eu ver aqui o restante link do grupo.

**Brazika Brasil:** Ixe, o cara falou que rodei a reunião de

**Lucas F. N. Alves:** Grupo certinho?

**Brazika Brasil:** novo.

**Lucas F. N. Alves:** hashtagsoportunidade

**Brazika Brasil:** Se o cara não quer fazer reunião, como é que vai ser o bagulho? Se o cara não quer fazer uma reunião,

**Lucas F. N. Alves:** hã pera aí que não eu vou ver isso

**Brazika Brasil:** como é que vai fazer o negócio com ele?

**Lucas F. N. Alves:** aí deixa eu ver aqui o link do post também não,

**Brazika Brasil:** Puxou não tá faltando.

**Lucas F. N. Alves:** não. Ele mandou o link do grupo no link do

**Brazika Brasil:** Manda,

**Lucas F. N. Alves:** post que ele salvou o profile link também.

**Brazika Brasil:** manda esse link aí desse no para mim para mim corrigir aqui.

**Lucas F. N. Alves:** Ele salvou o o nome do do grupo.

  
  

### 00:10:33

  

**Lucas F. N. Alves:** Deixa eu te mostrar como que

**Brazika Brasil:** Ai o Notion certinho ainda. É,

**Lucas F. N. Alves:** aí

**Brazika Brasil:** me manda o link do no aí des de desse desse que tá aberto agora aí.

**Lucas F. N. Alves:** deixa eu mandar um WhatsApp aqui você salvar.

**Brazika Brasil:** Eu já vou vou arrumar.

**Lucas F. N. Alves:** Deixa eu te mostrar aqui na minha tela. Aliás, abre aí na sua tela mesmo, porque aí eu te mostro como você faz. O no é pesado para c\*\*\*\*\*\*, velho. f\*\*\* no é isso. Mas aí você pode apertar control F ou command F ou então naquela lupinha ali na direita, ó. Mano, dá para fazer coisa demais com esse trem aí. p\*\*\* que pariu.

**Brazika Brasil:** live

**Lucas F. N. Alves:** Aí você naquela naquela lupinha ali da direita,

**Brazika Brasil:** aí.

**Lucas F. N. Alves:** você clica ali, ó, na Então você aperta conttrl F e escreve o nome dela para você ver. Princess Vincent. Rola paraa esquerda que você vai ver.

**Brazika Brasil:** Ah,

  
  

### 00:11:53

  

**Lucas F. N. Alves:** Ó lá.

**Brazika Brasil:** tá faltando tudo

**Lucas F. N. Alves:** Ela alguma dessa teve a vez que ele pegou ela certa.

**Brazika Brasil:** praticamenteando

**Lucas F. N. Alves:** Tá vendo aí? Tá faltando algumas coisas aí, mas tá ruim não.

**Brazika Brasil:** tudo aqui.

**Lucas F. N. Alves:** Quase tudo.

**Brazika Brasil:** Um

**Lucas F. N. Alves:** Ó, o comentário ele colocou como não,

**Brazika Brasil:** dele.

**Lucas F. N. Alves:** ó. comentário. Ele escreveu lá,

**Brazika Brasil:** É,

**Lucas F. N. Alves:** não,

**Brazika Brasil:** então era para tá marcando aqui.

**Lucas F. N. Alves:** eh,

**Brazika Brasil:** Como tu é

**Lucas F. N. Alves:** o comentário postado, porque o comentário postado é o principal que a gente vai revisar, avaliar, mas tá de boa.

**Brazika Brasil:** só não foi aqui,

**Lucas F. N. Alves:** Se ele tiver registrar no Notion,

**Brazika Brasil:** mas tipo aqui no cadê oxe,

**Lucas F. N. Alves:** é o mais fácil, o mais difícil é ele fazer. se ele tá conseguindo fazer o comentário.

**Brazika Brasil:** capturou outro lead aqui agora. É mais um. Só não sei se ele comentou.

  
  

### 00:12:32

  

**Brazika Brasil:** Será que ele comentou? Entendeu? Então aí no eu já vou arrumar aqui já. Eh, voltar aqui. Então, cadê? É o fluxo normal. Daí ele comenta se ele achar o post interessante, relevante, ele manda DM se ele achar relevante. Se a pessoa pedir, daí ele responde a DM quando tá tendo conversa, que nem esse cliente aqui, ó, que já vamos ver ele aqui, ó.

**Lucas F. N. Alves:** Угу.

**Brazika Brasil:** Lá visualizou sozinho com a mensagem, nem fui eu. Tá vendo a tela aí? É aquela última mensagem que eu te mandei.

**Lucas F. N. Alves:** Eu vou dar uma depois essas mensagens dá para visualizar elas aonde? Além desse lugar aí

**Brazika Brasil:** Você visualizava elas na onde antes ou não tinha nenhum

**Lucas F. N. Alves:** visualizava ela só e você aquele trem,

**Brazika Brasil:** lugar?

**Lucas F. N. Alves:** aquela interface que você criou lá. Cadê?

**Brazika Brasil:** Eh, abrir aqui, mas era só moto ainda, não tava normal. Mas eu vou fazer aqui para você poder ver.

**Lucas F. N. Alves:** Só para eu poder ver mesmo, para eu poder pensar aqui, poder entender que eu vou vou passar um negócio louco aqui para você agora.

  
  

### 00:13:59

  

**Lucas F. N. Alves:** Eu acho que tem um tem um chat útil aqui na VPS,

**Brazika Brasil:** Mas eh você acha que tá certo então? Tá original igual você fazia essa

**Lucas F. N. Alves:** mano. Se ele tiver conseguindo,

**Brazika Brasil:** conosco?

**Lucas F. N. Alves:** se o seu bote tiver comentando e respondendo mensagem da VPS, tá bom demais. Agora a gente tem só que monitorar eles.

**Brazika Brasil:** Aham.

**Lucas F. N. Alves:** Depois me falta os acessos lá da VPS.

**Brazika Brasil:** Aí aqui, ó, ele fez, vamos ver que ele fez, ele fez um comentário, será? Vamos ver. E um draft no Not.

**Lucas F. N. Alves:** Como

**Brazika Brasil:** Deve ser draft de e-mail. Vamos ver aqui. Vamos ver se ele pegou. É, comentou agora.

**Lucas F. N. Alves:** Deixa eu ver.

**Brazika Brasil:** Vixe, mas falta agora comentou bugado. Não comentou inteiro.

**Lucas F. N. Alves:** Mas comentou, tá? OK.

**Brazika Brasil:** Aqui é o SDR. Aqui, ó. Esse aqui já é a conversa da mulher mesmo aqui já, ó. Só que ele não puxou a última mensagem que ela mandou.

  
  

### 00:15:27

  

**Lucas F. N. Alves:** Entendi. Isso aí tá rodando tudo da a esse HTML aí. Não, mas o coisa tá rodando tudo da

**Brazika Brasil:** É o sistema inteirinho na VPS.

**Lucas F. N. Alves:** VPS.

**Brazika Brasil:** Só essa, isso aqui, essa interface que é é mocap, só esse daqui que tá integrado com meu messeng real,

**Lucas F. N. Alves:** Eu

**Brazika Brasil:** tipo o chat, o chat aqui, mas não consigo fazer nada aqui.

**Lucas F. N. Alves:** pensar aqui se a gente coisa o seu primeiro ou meu, mas eu acho que vai ser

**Brazika Brasil:** Aqui era tipo, mas esse aqui não é o certo, ele abriu

**Lucas F. N. Alves:** o

**Brazika Brasil:** errado.

**Lucas F. N. Alves:** me arruma aí as credenciais dessa VPS para eu ver o que que tem lá. Mas acho que eu vou te mostrar os próximos passos aqui do do Sheon e replicar no

**Brazika Brasil:** Aqui, ó.

**Lucas F. N. Alves:** seu.

**Brazika Brasil:** Eu coloquei até print aqui no no para você poder ver ele comentando bonitinho. Provas, prints reais.

**Lucas F. N. Alves:** Nossa.

**Brazika Brasil:** Cadê? Tá. Esperar ele abrir o normal ou que eu queria.

  
  

### 00:16:42

  

**Brazika Brasil:** É, se cortou o chat, a mensagem ali, acho que foi o geminho, mas com o Codex aí ele fica mais perfeitinho ainda igual tava, só que acabou meu limite aqui. Lá gerou uma quebra de

**Lucas F. N. Alves:** me manda aquele link lá do Rust Desk para eu tentar conectar aí.

**Brazika Brasil:** linha

**Lucas F. N. Alves:** Não. Ou então como

**Brazika Brasil:** aí, ó. Dá uma olhada aí, ó. É esse painel aqui que eu tinha feito, certo? Aqui é onde ficaria aqueles vídeos lá que que é o que a gente tá fazendo aí que vocês estão fazendo ou tipo GitHub, vídeo. Aqui é ranking de grupo e aqui é o bagulho de lead que você tinha falado de qualificar lead.

**Lucas F. N. Alves:** M.

**Brazika Brasil:** Aí aqui, por exemplo, no chat você clica nele, aí você consegue tipo mandar apresentação, aquela outa lá, né? Tipo, ah, tem vídeo de tals, ele já sugere, ele vai puxar no nosso banco de dados e sugere baseado no que ele ele puxou, né? Aqui tem que melhorar bastante, mas tipo, ele puxa aqui o link do post, ações já feitas, tipo, comentou, mandoum, tem um draft do WhatsApp, o draft do e-mail, demo GHL, acho que é tipo o videozinho que já mandou aí,

  
  

### 00:17:51

  

**Lucas F. N. Alves:** Isso aí ficou bom.

**Brazika Brasil:** tipo, enviar demo local ou abrir a conversa.

**Lucas F. N. Alves:** Isso aí ficou bom para c\*\*\*\*\*\*. Esse esse HTML

**Brazika Brasil:** Aí,

**Lucas F. N. Alves:** aí.

**Brazika Brasil:** tipo, aqui é o chat, né? Aparece o chat em tempo real, é, é mo então não tô conseguindo mexer direito aqui, mas tipo, tá integrada no no seu painel mesmo,

**Lucas F. N. Alves:** Uhum.

**Brazika Brasil:** lá no no SDR aqui, ó. Ou o seu original é esse aqui, né? Tem nada no original. Aí ele entra essa parte aqui, ó. E você, aí, tipo, você que é basicão,

**Lucas F. N. Alves:** Угу.

**Brazika Brasil:** mas eu fiz só no baseado que você falou lá. Aí quando eu tiver todos os conteúdos, vai ficar o conteúdo aqui. Ele fez um vídeo de de vistoria para mim, um bagulho que você pediu ontem. Será que é isso? Eu para ver. Ah, não. Esse aqui é o primeiro que eu te mandei. Te mandei esse vídeo? Acho que não, né?

**Lucas F. N. Alves:** Acho que não.

  
  

### 00:18:50

  

**Brazika Brasil:** Ah, esse aqui foi o primeiro que eu fiz lá com aquela skill que você mandou.

**Lucas F. N. Alves:** M.

**Brazika Brasil:** Ficou bem basicão. Ol, cadê? Tem outro aqui. Acho que é esse aqui. Toda fraude veicular começa com uma imagem que mente o confere acaba com isso. Vistoria 100% por vídeo com antifraud cinco camadas.

**Lucas F. N. Alves:** Vou te passar certa,

**Brazika Brasil:** Um saque de chutas.

**Lucas F. N. Alves:** mas os vídeos por enquanto não precisa preocupar tanto.

**Brazika Brasil:** É, mas tipo isso eu fiz só de teste para poder tipo colocar aqui para ver como é que ficaria integrado aqui,

**Lucas F. N. Alves:** Угу.

**Brazika Brasil:** sabe? Esse vídeo ele já ele aqui ele já ia gerar esse vídeo automático. Só que daí no caso eu esperasse você mandar o seu lá, como é que você fez o seu certinho? Daí eu coloco aqui para ele já gerar automático. Ele vai gerar automático baseado no KitHub lá. Você tem projeto seu, se não tiver, ele vai gerar baseado na na conversa aqui e no que o cara pediu, tipo, igual esse aqui mandou, cadê? Igual esse aqui, tipo, já mandou esse textão aí, já faria um conteúdo baseado nisso aqui, né?

  
  

### 00:20:01

  

**Brazika Brasil:** No caso, já daria para fazer, né?

**Lucas F. N. Alves:** Não, no caso, no caso,

**Brazika Brasil:** O que você tá

**Lucas F. N. Alves:** esses vídeos,

**Brazika Brasil:** fazendo?

**Lucas F. N. Alves:** eu acho que a gente vai gerar só depois da call, mas dá para fazer um e-mail e tals. Eu eu vou eu vou te mostrar certinho aqui. Eu tô procurando um histórico aqui das calinho o que que a gente vai fazer para ele responder tudo perfeito. Deixa eu te mostrar minha tela aqui. Ficou bom isso aí, velho? Não ficou ruim não.

**Brazika Brasil:** Ficou basicão, mas o que eu fiz com dois prontos?

**Lucas F. N. Alves:** Isso aí. Isso aí que eu tá mostrando é a tela do confere ou é ele que

**Brazika Brasil:** Eu pedi para ele acessar a tela do Confere Real Mm.

**Lucas F. N. Alves:** recriou?

**Brazika Brasil:** Tipo, aqui ele não pegou a certa, mas aqui no painel ele pegou a tela certa, ó.

**Lucas F. N. Alves:** Mas isso aí é um print da tela ou ele recriou? É um print.

**Brazika Brasil:** Ele acessou pro play e fez.

  
  

### 00:20:58

  

**Brazika Brasil:** Ele navegou,

**Lucas F. N. Alves:** Entendi.

**Brazika Brasil:** tirou print e é a tela real mesmo da

**Lucas F. N. Alves:** Entendi.

**Brazika Brasil:** plataforma.

**Lucas F. N. Alves:** Porque dá para ele recriar a tela, mas ficou bom. Eu vou dar uma olhada se

**Brazika Brasil:** É, foi basicão. Esse aqui no tipo não era, pô. Eu tô agora mexendo.

**Lucas F. N. Alves:** mais.

**Brazika Brasil:** É, é aqui mesmo. Marco dele fiz com dois pronto daquela skill que você mandou. Era só para ver como é que ficaria. Ele gerou aquele bagulho básico ali,

**Lucas F. N. Alves:** Uhum.

**Brazika Brasil:** mas dá para melhorar. Aqui ó, resposta sugerida. E também dá até a resposta sugerida na hora. Ó,

**Lucas F. N. Alves:** Deixa eu tear, deixa eu te mostrar aqui o review da, aliás, me manda esse HTML aí para mim por e-mail

**Brazika Brasil:** esse

**Lucas F. N. Alves:** e deixa eu te mostrar aqui um a minha tela. Mas ficou bom, viu, mano? Vou ver esse negócio do lama cloud aí também

**Brazika Brasil:** tem, acho que tem um, ó, vou mostrar o valor.

  
  

### 00:21:51

  

**Brazika Brasil:** Recompensa bem mais que que acho que o open o o cloud, o codex que obra ele que é o o lama. Você os valores aqui ele é bem mais completo e tem todas, né? Tipo esse ele usou cinco só para fazer análise de texto. Ele tem de áudio, ele tem de vídeo, tem de tudo aqui, ó. Aí tem tipo o plano Max, que é o mais carinho deles. Aqui, ó, o cloud usage, que é o que nós usa que é na nuvem, 50% mais aqui é cinco vezes mais, eu acho que deve ser não deve ser

**Lucas F. N. Alves:** Pode dar ali nesse pro aí. Vai. Aliás, deixa eu assinar uma conta minha aqui do

**Brazika Brasil:** não,

**Lucas F. N. Alves:** Pro.

**Brazika Brasil:** mas dá uma dá uma estudada nele para ver se realmente é não consigo ver se o limite aqui se dá para fazer, se ele vai ficar rodando limitado. Vamos ver Get Pro. Ah, ele vai direto para Stripe já.

**Lucas F. N. Alves:** 50 vezes mais Cloud usa de tá doido, é muito cabuloso.

**Brazika Brasil:** E o e o e o Maps é cinco vezes mais, mas o Pro 20, mas tem tudo, ó, os modelos você tem tem infinitos modelos aqui, ó, na nuvem, né?

  
  

### 00:23:07

  

**Brazika Brasil:** Tem um cloud. Esses daqui é para rodar local, se o PC aguentar. Esse aqui é top, ó. Que víde liberou, tipo, essa semana, semana passada,

**Lucas F. N. Alves:** Cloud.

**Brazika Brasil:** na verdade.

**Lucas F. N. Alves:** Esses aí tudo tem cloud.

**Brazika Brasil:** Cadê? Tem que bate de frente com a com a do Cláudio. É aqui, ó. Kim de psique também é boa. Essas daqui é tudo na nuvem. É, tem pouco, só tem isso aqui, mas acho que já é suficiente,

**Lucas F. N. Alves:** Vou assinar aqui na minha conta.

**Brazika Brasil:** velho.

**Lucas F. N. Alves:** Pode entrar aí na minha conta ou lama. E depois você conecta nela aí para ver.

**Brazika Brasil:** que daí tipo não dá para dá esse olama aqui dá dependendo dos créditos dá pra gente usar para fazer as outras coisas aí, não só aqui, né? Que ela tem modelo para

**Lucas F. N. Alves:** É,

**Brazika Brasil:** tudo.

**Lucas F. N. Alves:** isso aí dá para usar para c\*\*\*\*\*\* até para um negócio que eu tô vendo aqui de

**Brazika Brasil:** Tentar ver se ela substitui o Cláudio. Se substituir aí compensa,

  
  

### 00:23:59

  

**Lucas F. N. Alves:** licitação.

**Brazika Brasil:** né, galera? E eu vou criar um API já já criei API.

**Lucas F. N. Alves:** Você conseguiu entrar no meu aí?

**Brazika Brasil:** Vou deixar salvo aqui. Eh, qual que é seu e-mail mesmo? O e-mail para mim te mandar o

**Lucas F. N. Alves:** Hum.

**Brazika Brasil:** HTML.

**Lucas F. N. Alves:** Ué, é isso que você tá logado aí, Lucas @automatrix.

**Brazika Brasil:** Vamos ver.

**Lucas F. N. Alves:** Traciar com isso.

**Brazika Brasil:** Aí você me fala que eu ativo aqui.

**Lucas F. N. Alves:** Que que é esse toquen aí?

**Brazika Brasil:** É o seu lama já.

**Lucas F. N. Alves:** Ah, hum. Isso aí. Eu recebi ontem um pedido para poder fazer eh para poder adicionar num edital de uma licitação coisas que dificultassem pros concorrentes, tipo coisa bem específica. Aí quanto esse trem da Oama Cloud, por exemplo, eu vou,

**Brazika Brasil:** Boa. Tá surgindo trampin aí assim, tipo igual do Facebook ou não?

**Lucas F. N. Alves:** eu não tô muito de olho não, que eu tô muito focado no negócio do Júnior lá que tá enchendo de trem.

  
  

### 00:25:18

  

**Brazika Brasil:** É, dele também é um negócio que já entrou também,

**Lucas F. N. Alves:** Escrepe de muita oportunidade aqui.

**Brazika Brasil:** né?

**Lucas F. N. Alves:** Eu que não tô olhando, mas eu tô batendo olho assim, não tô vendo várias coisas. Esses trem de gor leva aí mesmo. Nossa.

**Brazika Brasil:** Pois nós ver o bagulho das cal para ele poder responder certinho. Daí eu tento fazer aqui também ele da sua lado. Você me explica como é que é certinho. Só não vou conseguir fazer cal. Aí é com você

**Lucas F. N. Alves:** Não, os negó da cal tá tranquilo, mas falar não ligando que Fala Júnior.

**Brazika Brasil:** mesmo.

**Lucas F. N. Alves:** Beleza. Beleza. Só para confirmar, 15 horas dá para falar com Maurício. 15 horas dá. fechado. Era só para isso que ele vai agendar lá com o menino. Vai ser telemedicina só? Não. Eh, telemedicina a gente vai falar com o menino, não fala de valor nem nada. Vamos falar da segurança, sei lá, dúvida que a gente eh possa ter lá.

  
  

### 00:26:18

  

**Lucas F. N. Alves:** Ponto. E aí depois a gente fala depois que o menino sair que o menino não tem nada a ver com a com a questão da da outra estação multit. É isso. Entendi. Tá bom. Mas essa das três vai ser sobre telemedicina. É. E não, depois a gente o menino saindo. O menino saindo. A gente pode falar da seguradora. Acho que dá tempo. Posso chamar o Leon? Pode chamar o Leonard vai em qual? Nessa nesse projeto da telemedicina aí. Ele ele ele tá querendo marcar comigo as três. Aí de repente eu boto ele na cal também, tá? Ele é da segurança, ele que vai fazer a segurança, ele é que vai gerir tudo. Ele que vai vai arrumar a equipe toda para inclusive a segurança para poder fazer, tá? Mas aí você não vai, é o seguinte, vamos lá. Não fala nada que vai arranjar a equipe nem nada, é seu parceiro, tá beleza?

  
  

### 00:27:21

  

**Lucas F. N. Alves:** Tá. E assim, valores eh com o menino a gente não tem nada para falar, tá? Fechou? Então, tipo, quando o menino tiver na cal, né? Isso. Na largada parte técnica. Ok. Ok. Tá ótimo. Tá. Falou. Falou.

**Brazika Brasil:** Boa fecha os dois ligado.

**Lucas F. N. Alves:** Acho que foi aqui o lama cloud.

**Brazika Brasil:** Aí aí

**Lucas F. N. Alves:** Mostrar a tela na cal aqui para poder mostando

**Brazika Brasil:** já vou dar o enter aqui.

**Lucas F. N. Alves:** aí.

**Brazika Brasil:** Vixe, agora vai ficar rodando infinito. É, literalmente teve curso, né?

**Lucas F. N. Alves:** Manda os acessos dessa VPS aí depois para eu poder ver como é que tá lá nela,

**Brazika Brasil:** Agora

**Lucas F. N. Alves:** que eu tenho que mostrar pro Salo também. Deixa eu ver esse trem.

**Brazika Brasil:** tem umas top aí para analisar a imagem

**Lucas F. N. Alves:** Vision Mini Max M3 milhão de context Window, né? Tem muita, tem muita.

  
  

### 00:28:40

  

**Lucas F. N. Alves:** Ah, tem a mini CPM aqui, ó. Mini CPM. É essa que dá para rodar no iPhone

**Brazika Brasil:** Dá para rodar local também, mas você tem que ver as cloud aqui, ó. As cloud é que roda na nuvem. Essas outras acho que vai ter essas outras aí é tudo

**Lucas F. N. Alves:** que eu menina ali.

**Brazika Brasil:** localmente.

**Lucas F. N. Alves:** Eh, o Caio quer quer uma iar para ele rodar local.

**Brazika Brasil:** Ô, dá para pega, tipo, eu testei aqui uma que deu bom no meu notebook foi essa aqui, ó.

**Lucas F. N. Alves:** Essas mini CPM roda no iPhone, mano. Bota fé no iPhone.

**Brazika Brasil:** Meu iPhone.

**Lucas F. N. Alves:** E é boa para c\*\*\*\*\*\*.

**Brazika Brasil:** Eu usei essa daqui,

**Lucas F. N. Alves:** Já testei.

**Brazika Brasil:** ó, no meu PC, tipo, ela é na nuvem, né? Só que ela não consegue acessar local os computador,

**Lucas F. N. Alves:** Eu tô usando essa daqui,

**Brazika Brasil:** mas eu tô usando essa

**Lucas F. N. Alves:** ó. Quen 3 VL. Qual que você tá usando?

  
  

### 00:29:28

  

**Brazika Brasil:** Nemotron.

**Lucas F. N. Alves:** Ela é quanto de limite de contexto?

**Brazika Brasil:** Aí eu fiz bastante pergunta ali, acho que é 1 milhão. Quer ver?

**Lucas F. N. Alves:** 256 550 bilhões de parâmetros.

**Brazika Brasil:** Ó.

**Lucas F. N. Alves:** Volta lá. Volta lá nas modelos,

**Brazika Brasil:** Na onde? Em cima.

**Lucas F. N. Alves:** na lista. Desce aí. É trê quen 3 VL. Pode descer. Cran 3 coder next. Ah, sobe lá, sobe lá. Clica em vision.

**Brazika Brasil:** Esse aqui é top. Então, tipo, é que bate de frente com com a do

**Lucas F. N. Alves:** Tô usando aquela ali, ó. Coin 3 VL ou é Coin 2 VL.

**Brazika Brasil:** Cláudio.

**Lucas F. N. Alves:** Clica lá para você ver. 3. Ele clica ali embaixo. Isso aí. Essa, essa IA aí, ó, tá rodando no meu Mac e tá fazendo a indexação dos vídeos lá.

  
  

### 00:30:37

  

**Brazika Brasil:** Boa.

**Lucas F. N. Alves:** Conseguir botar o lama nela aqui, vai ser muito

**Brazika Brasil:** O meu rodou só esse aqui.

**Lucas F. N. Alves:** sucesso.

**Brazika Brasil:** Tentei rodar também. Eu consegui rodar essa aqui, mas bem travando. Travou tudo o computador e para responder um oi. Demorou. Eu ten que arrumar um,

**Lucas F. N. Alves:** Deixa eu ver aqui qual que ele rodou.

**Brazika Brasil:** tem que fazer um setup top, é um PC super top para deixar rodando, ficar mais top. Essas tudo assim, ó, local

**Lucas F. N. Alves:** Nós vamos fazer por causa do projeto, vai precisar dear local, mas esse lama Cláudio aí quebra um galho,

**Brazika Brasil:** no AliExpress. Aí nós dá fazer um PCzão top,

**Lucas F. N. Alves:** viu?

**Brazika Brasil:** velho. Ou vários, né? Um integrado num só. Esses modelos aqui na nuvem aqui dá para fazer qualquer coisa agora. Deixa eu ver se integra aqui aqui,

**Lucas F. N. Alves:** Mano, eh,

**Brazika Brasil:** ó. VS te

**Lucas F. N. Alves:** eu vou ter que olhar uns treinos da telemedicina para antes do da cal com o Júnior às 3

  
  

### 00:31:24

  

**Brazika Brasil:** mandar.

**Lucas F. N. Alves:** horas. Então, eu vou te passar aqui esse negócio aqui da pipeline e vou olhar os negócios da telemedicina lá.

**Brazika Brasil:** Fechou.

**Lucas F. N. Alves:** Deixa eu ver aqui qual o modelo que ele usou. Deixa eu ver. Foi esse co 3 VL aí, 2 bilhões de parâmetro. Deixa eu te mostrar aqui no meu na minha tela. Ó, aqui no sidan é inf, não é? É, é infel pipeline de leads. Depois a gente tem que vai atualizar esse documento aqui. Eu vou te mandar esse documento modelo aqui, você criar um tipo esse aqui, ó. Mas aqui já vai plano de leitades. Então, descoberta no Face, parece que o senhor tá fazendo comentários e tal, vai ter que aprimorar esse negócio aí, ver agora como é que ele vai rodar com esse lama ilimitado. E aí a captura.

**Brazika Brasil:** É, tem que ver como é que é que nem a parte do notion aí que ele já não fez certinho. Tem que ver nesse convex aí.

  
  

### 00:32:53

  

**Lucas F. N. Alves:** Uhum.

**Brazika Brasil:** Esse convex é o quê? É tipo um Ah,

**Lucas F. N. Alves:** conve é tipo um super base mesmo, só

**Brazika Brasil:** fica só armazenar os arquivos.

**Lucas F. N. Alves:** OK.

**Brazika Brasil:** Mas acho que deve tá indo nos arquivos lá então, porque senão não ia aparecer lá no no seu Michocra.

**Lucas F. N. Alves:** É o aquele mão controlar, o database dele tá sendo convex em vez de ser o super base.

**Brazika Brasil:** Ah, então então tá

**Lucas F. N. Alves:** Só que no tipo o notion é uma maneira de salvar os dados de um

**Brazika Brasil:** funcionando.

**Lucas F. N. Alves:** jeito que fique visível para todos, entendeu? Um dado só.

**Brazika Brasil:** Aham.

**Lucas F. N. Alves:** Aí o convex como ele tem limitações, aí tipo você tem esse convex aí com o seu com a sua aplicaçãozinha, eu tenho com a minha.

**Brazika Brasil:** Então eu tô usando o seu.

**Lucas F. N. Alves:** e usar,

**Brazika Brasil:** O combo que você tá usando é o seu

**Lucas F. N. Alves:** entendeu?

**Brazika Brasil:** mesmo

**Lucas F. N. Alves:** Só que tipo o que você faz scraping aí você tem que identificar que o scraping foi seu do seu perfil e tals. Isso é uma coisa que falta de deado lá no Notion.

  
  

### 00:33:41

  

**Brazika Brasil:** no painel,

**Lucas F. N. Alves:** É, mas aqui a captura a gente tá quase tá quase OK,

**Brazika Brasil:** tá?

**Lucas F. N. Alves:** é quase 100%. Eu acho que com esse negócio aí deve resolver. Aí a gente precisa de quê? Melhorar talvez a qualidade da captura. Mas ele tá capturando, OK? Mas vou te dar mais dados, mais exemplos para melhorar dados de captura. Eu vou te dar exemplos aqui. Aí, beleza? Eh, essa parte do SDR que eu quero te mostrar mais aqui,

**Brazika Brasil:** Aumentei aí.

**Lucas F. N. Alves:** o SDR, o seguinte, ele precisa, a gente precisa de fazer um rag para ele e fazer o prompt mais específico com as informações certas e direcionar ele para poder ele eh, como que eu posso dizer, para poder ele saber buscar os exemplos certos, as automações certas, etc. e tal. Eu acho que eu vou até te gravar aqui com detalhes e te dar exemplos aqui na tela.

**Brazika Brasil:** esse

**Lucas F. N. Alves:** Quer ver? Ó, primeira coisa aqui do essa essa parte aqui entra um pouco no scraping

  
  

### 00:34:47

  

**Brazika Brasil:** pipeline.

**Lucas F. N. Alves:** também, mas é um dado importante de se saber. Por exemplo, aqui, ó. Isso aqui. Depois aqui, quando eu terminar a explicação, eu vou te mostrar onde você vai achar todas as caus que eu fiz, explicando isso com mais detalhes para você poder extrair e criar esse rag, a me ajudar a criar esse rag aqui. Eh, vem aqui, ó,

**Brazika Brasil:** Eu

**Lucas F. N. Alves:** tipo de oportunidade, hiding, project e partnership. Vamos ver o post dessa mulher aqui, se foi o se conteúdo do post dela é esse mesmo. Quer ver?

**Brazika Brasil:** vi o conteúdo.

**Lucas F. N. Alves:** Post.

**Brazika Brasil:** aqui era mais zoado.

**Lucas F. N. Alves:** Estou estou me mudando paraa China em alguns meses e pretendo abrir uma agência de automação go High Level. Estou procurando por alguém para ficarem cargo de conseguir os meus de conseguir clientes e dividir porcentagem. Alguém interessado? Esse tipo de post aqui, mano, é o tipo de pessoa, tipo assim, que a gente só vai, tipo, dar um oi, tá ligado?

  
  

### 00:36:01

  

**Lucas F. N. Alves:** A gente não vai dar muito foco para esse tipo de cliente, porque esse tipo de cliente é o cliente que tá querendo juntar com outras com outra pessoa de graça para montar um negócio, isso nunca funciona.

**Brazika Brasil:** Угуm.

**Lucas F. N. Alves:** Partnership, esse termo parceria é um termo que não existe, não funciona. Você vai achar muita gente aí tipo: "Ah, busca o partnership". É tipo assim, eu virar para você e falar: "Ô, Léo, vamos embora junto aqui comigo e tal, vamos fazer uma agência." Só que aí você vai comer como pagar seu aluguel,

**Brazika Brasil:** Угу.

**Lucas F. N. Alves:** esses trem, entendeu? Então, partnership, a gente vai mandar uma mensagem ali e tipo deixar o lead só no na nossa base ali para caso ele venha a apresentar intenção de comprar alguma coisa, a gente fala com ele. E aí o SDR pode conversar com esse lead, que ele é tipo partnership, no sentido de oferecer para ele mentoria, talvez, ou eh explicar para ele algum dos nossos serviços. Por isso que é importante a gente explicar os nossos serviços e que eu vou te explicar depois e vou te mostrar os vídeos aí. Eh, aí a gente tem hiding.

  
  

### 00:37:00

  

**Lucas F. N. Alves:** Hiring, mano. Vamos ver se a gente acha um hiding aqui.

**Brazika Brasil:** Eh,

**Lucas F. N. Alves:** Vamos.

**Brazika Brasil:** o que que é? É bom. Traduz aí para mim esses três aí.

**Lucas F. N. Alves:** Hã,

**Brazika Brasil:** parceria, partnership

**Lucas F. N. Alves:** é a pessoa quer contratar alguém, tipo assim,

**Brazika Brasil:** lá.

**Lucas F. N. Alves:** quer contratar, entendeu? Tipo assim, ele não quer eh igual Crislan, por exemplo, foi um projeto Hiding não, Heiding, ele quer contratar, tipo, é um é uma vaga de emprego, tá ligado?

**Brazika Brasil:** Entendi,

**Lucas F. N. Alves:** Uma pessoa dele e tals.

**Brazika Brasil:** entendi. A parceria,

**Lucas F. N. Alves:** Deixa eu ver como é que

**Brazika Brasil:** vaga de emprego e projeto do zero.

**Lucas F. N. Alves:** é.

**Brazika Brasil:** Qual os carguin que tem? É parceria para fazer parceria. Aí tem esse aí que é vaga de emprego e o outro aí pro que é para projeto novo para fazer o projeto do zero.

**Lucas F. N. Alves:** É, o outro é tipo projeto sobre demanda, igual o do Cris, é tipo tantos meses, tal coisa tem que fazer.

  
  

### 00:37:45

  

**Brazika Brasil:** Uhum.

**Lucas F. N. Alves:** Esses aí é os que a gente mais quer fazer. Mas eu vou te explicar esse negócio do H. Ai, ai, ai. Meu Google tá fando. O Google atualizou agora, mano. Ficou muito legal. Precisa-se de especialista em comportamento de a atacado imobiliário, ou seja, o nicho high real estate. Eh, por favor, lê atentamente antes de candidatar. Eu não estou procurando especialista geral em go high level. A maioria dos candidatos sabe como construir fundo de trabalho. Não é isso que eu preciso. Tô procurando um verdadeiro especialista em comportamento de A que entenda D. Engenharia de pronto, design de conversação, comportamento de resposta de a lógica de fluxo, psicologia de interação com vendedor e a de conversação do guay level, nutrição de líos imobiliários. O ideal é que você já tenha trabalhado com empresa ou agência que use ativamente a IA para geração de leaders. Experiência com atado imobiliário, rolo,

**Brazika Brasil:** M.

  
  

### 00:39:11

  

**Lucas F. N. Alves:** cedo, esporte m preferencial. Situação atual. Meu sistema G já foi construído e auditado. Não estou à procura de reconstrução completa. Problemas que precisam ser diagnosticados. A IA está ocasionalmente enviando mensagens confusas ou sem sentido para os vendedores. Isso é um trabalho para nós, entendeu? Revisão adicional necessária. Que eu quero de você. Qual essa experiência? Trabalhou com IA do Burai Level ou funcionários de IA? Ela trabalhou com empresa de imobiliário real estate roll saying

**Brazika Brasil:** É,

**Lucas F. N. Alves:** world.

**Brazika Brasil:** é todo o sistema que a gente já tem os clientes, o Cris já tem cliente.

**Lucas F. N. Alves:** Isso aqui foi qualificado como um como um hiring, Leo, mas não é um hiding isso aqui. Isso aqui é um project. Deixa eu achar um hiding aqui para eu te mostrar só a diferença e a gente entrar nesse detalhe aí desse projeto.

**Brazika Brasil:** ali embaixo mais

**Lucas F. N. Alves:** Isso aqui é de hoje.

  
  

### 00:40:03

  

**Lucas F. N. Alves:** Isso aqui é de hoje,

**Brazika Brasil:** de ontem.

**Lucas F. N. Alves:** c\*\*\*\*\*\*, mano. Será que tem esse post aqui? Isso aqui é oportunidade boa. Grupo link. Post link ser o meu,

**Brazika Brasil:** É, foi do meu bicho. Acho que foi do

**Lucas F. N. Alves:** mano.

**Brazika Brasil:** seu

**Lucas F. N. Alves:** Esse aí a minha eu vou te falar, velho. Nós precisamos de gravar vídeo e mostrar a minha não.

**Brazika Brasil:** tá rodando com Codx, eu acho.

**Lucas F. N. Alves:** Acho que a minha tá rodando com cloud.

**Brazika Brasil:** O Cláudi quer que eu

**Lucas F. N. Alves:** Ela tá com codex, mas ela tá caindo no fall.

**Brazika Brasil:** boto o lama lá.

**Lucas F. N. Alves:** Ô Lama, não precisa não. Pode deixar essa minha. Eu vou deixar ela regaceira, mano. Vou mandar o vídeo pro cara aqui, ó.

**Brazika Brasil:** É, não comentou não.

**Lucas F. N. Alves:** Ó, tá vendo a minha tela?

**Brazika Brasil:** Sim.

**Lucas F. N. Alves:** Vou até cortar esse prompt aqui.

  
  

### 00:40:57

  

**Lucas F. N. Alves:** Eh, deixa eu mandar esse prompt aqui para você. Calma que eu vou cavar esse prompt aí. Eh, busque pergunta Não, nós temos que traquear esse esse negócio, mas vai ser fácil traquear. Não vou nem digitar isso aqui. Acho que vai ser só isso. Vou mandar para ele para ver as respostas que os agentes dariam para isso. Ah, já salve. Na verdade, vou mudar isso. E aí eu quero olhar aqui para ver se esse lead a anônimus participante. Ó, deve ser um desses aqui. Deixa eu ver. O SD tá rodando. Não, aqui seria legal clicar e ver os detalhes dos leades que foram extraídos. Eu vou adicionar isso aqui depois para ficar tranquilo que esse meu aqui eu vou personalizando. É legal você ir personalizando o seu. Vou personalizando o meu. Depois a gente bate para ver.

**Brazika Brasil:** Ja.

**Lucas F. N. Alves:** Aqui, por exemplo, ó, eu tenho que clicar e ver qual os leads que foram cincados pro Notion.

  
  

### 00:44:21

  

**Brazika Brasil:** Угу.

**Lucas F. N. Alves:** Isso aqui falta eu otimizar. Open cloud offline. Como assim? Ah, ficou offline por causa de alguma coisa. Uma mensagem que eu mandei aqui ou algum botão que eu apertei, ficou off. Vai reiniciar. Beleza.

**Brazika Brasil:** B

**Lucas F. N. Alves:** Que que você i falar? Ah, de bom. Ah, v outras ferramentas que tem no flow lá. Tem umas ferramentas, tem umas ferramentas interessante lá. Você tem coisa para c\*\*\*\*\*\*. Tem da hora. Nós assinamos um trem aqui, ó, que chama o lama cloud. Aí, esses modelos é tipo aqueles modelos que eu tava rodando localmente lá, não tem que pagar nada. E aí esse Olama Cloud, ele nos dá servers na nuvem. Cloud para cloud que eu tô falando é cloud de nuvem agora, viu? Cloud assim, ó. Cloud. Uhum.

  
  

### 00:45:36

  

**Lucas F. N. Alves:** E aí a gente consegue rodar armazenamento nuvem, você fala não é armazenamento, a gente consegue rodar as IAS nessa nesse cloud nuvem,

**Lucas F. N. Alves's Presentation:** Er

**Lucas F. N. Alves:** é, em vez de rodar no nosso PC. Então, por exemplo, essa Ia aqui, ó, que tava rodando no meu, é, exato. E essa aqui roda no iPhone, ó. Essa mini CPM, nesses iPhone nosso, 14, 15, ela roda e ela é f\*\*\*, mano. f\*\*\* essa mini CP. É, mas essas paradas aí é o quê? Todos esses três é o que vai rodar. São modelos Minimx, gema. A gente pode escolher o modelo e rodar. Em vez de pagar pela assinatura do GPT ou do cloud, do Clode. A gente assina uma nuvem e a gente pode rodar vários modelos open source lá. Ah, bem melhor que a gente poderia rodar no nosso computador. Bem melhor já. Aí eu assinei um aqui lá tá configurando os negócios lá.

  
  

### 00:46:25

  

**Lucas F. N. Alves:** Essa brincadeira $ Downs que dá mesmo assinatura do dia R$ 100. Então compensa. Nós vamos testar que isso compensa por todos. Nós vamos testar que isso compensa. Ô Léo, parece que o meu open call ficou off por algum motivo, velho. Vou verificar aqui ele. Ah, voltou. Eu mandei a mensagem ali, ele tinha dado um pirutico, mas aqui eu vou colocar ele para ver se ele fez o scraping dele, tipo para ver qual os leads que ele fez o scraping por aqui também para eu é para

**Brazika Brasil:** Tem que identificar, né, o perfil. Ah,

**Lucas F. N. Alves:** eu poder bater aqui.

**Brazika Brasil:** como cada um vai ser o teu seu painel, tem que identificar lá no último, né, no

**Lucas F. N. Alves:** Eu acho que dá para ver, ó.

**Brazika Brasil:** caso.

**Lucas F. N. Alves:** Tabela. Ah, aqui dá para ver captura. Só eu tenho que adicionar aqui depois para poder filtrar por data. Isso aí é um site que você fez. Uhum. 10/06 10/06.

  
  

### 00:47:22

  

**Lucas F. N. Alves:** Aqui, ó.

**Brazika Brasil:** É tudo novo,

**Lucas F. N. Alves:** Ah,

**Brazika Brasil:** c\*\*\*\*\*\*.

**Lucas F. N. Alves:** dá para ver por aqui, ó.

**Brazika Brasil:** Ah, aquele dali foi o meu. Tem um teste B.

**Lucas F. N. Alves:** Foi, foi por aqui, ó.

**Brazika Brasil:** Testando.

**Lucas F. N. Alves:** Foi por aqui, ó. Tá vendo? Agora não sei porque que ele não comentou,

**Brazika Brasil:** Hum.

**Lucas F. N. Alves:** velho. Se foi por aqui, não sei porque que ele não comentou. Ah, tá. Comentário postado. Ele postou aqui. Parece comentário postado. Deixa eu ver.

**Brazika Brasil:** Pronto.

**Lucas F. N. Alves:** ver post no Facebook.

**Brazika Brasil:** Bota lá em cima lá o filtro. Volta lá. Ah, a gente comentou três

**Lucas F. N. Alves:** Hum.

**Brazika Brasil:** vezes.

**Lucas F. N. Alves:** Ele tá, ele tá spamando. Ah, isso aqui foi ontem. Ele pegou repetido.

  
  

### 00:48:10

  

**Lucas F. N. Alves:** Entendi. Vou dar a instrução para

**Brazika Brasil:** O meu tá com a instrução, tipo, ele não comenta nos posts que ele já comentou.

**Lucas F. N. Alves:** ele.

**Brazika Brasil:** E ele fez esse teste. Se eu acho que deve ter perdido essa

**Lucas F. N. Alves:** Preciso dar esse esse tchan

**Brazika Brasil:** configuração.

**Lucas F. N. Alves:** aqui. Deixa eu ver se eu consigo mandar o vídeo.

**Brazika Brasil:** Os cara é doido. Tudo ele vai ficar

**Lucas F. N. Alves:** Comentários.

**Lucas F. N. Alves's Presentation:** In real estate andage speed is everything the broker who responds first wins

**Brazika Brasil:** doido.

**Lucas F. N. Alves:** M.

**Lucas F. N. Alves's Presentation:** de quietes what if lead was captured automatically every drafted in seconds in your voice with your

**Lucas F. N. Alves:** Угу.

**Lucas F. N. Alves's Presentation:** CRM every piece of contentuced without you ever sitting in front of a camera that's not a

**Brazika Brasil:** Tem que fazer uma para ficar postando esses comentários o vídeo. Acho que não é uma boa não.

**Lucas F. N. Alves's Presentation:** future pitch that's what we built for a mortgage broker in Reding California aentic

**Brazika Brasil:** o nos poste referente a isso.

  
  

### 00:49:17

  

**Brazika Brasil:** comentar já

**Lucas F. N. Alves's Presentation:** system handling lead capture client communication and content production running 24 hours a

**Brazika Brasil:** convos

**Lucas F. N. Alves's Presentation:** day 7 days a Mac mini M4 Pro the platform

**Lucas F. N. Alves:** É o vídeo aqui.

**Lucas F. N. Alves's Presentation:** power 11

**Lucas F. N. Alves:** Eu falei para ele para poder checar esse projeto que eu fiz para um cliente de real estate na Califórnia, que ele tá procurando também pro real estate.

**Lucas F. N. Alves's Presentation:** special

**Lucas F. N. Alves:** Mas, mano, o meu boneco tá spamando o comentário aqui. Eu vou falar com ele depois para adicionar isso para não fazer comentário repetido e para mandar o vídeo no comentário. Agora o vídeo acho que eu vou botar ele para mandar o link que se ele mandar o vídeo assim vai ser f\*\*\*, eu acho. Cara pegar não que eu falo assim fodo para ir a automatizar

**Brazika Brasil:** Oi,

**Lucas F. N. Alves:** esse envio aqui eu acho. Talvez dá um link só pode.

**Brazika Brasil:** Eixe,

**Lucas F. N. Alves:** Eu acho que mandar um link vai ser mais. Mas mano, a galera tá ó, você comentou no mesmo post que eu, ó.

  
  

### 00:50:13

  

**Brazika Brasil:** o meu comentou aí.

**Lucas F. N. Alves:** Uhum.

**Brazika Brasil:** Cadê?

**Lucas F. N. Alves:** Ixe, que que é isso aqui? Será que o meu WhatsApp já tá sacando o pau lá? Botar um dinheiro. Ah, não, não tem dinheiro aqui ainda.

**Brazika Brasil:** Ah, eu não configurei seu zap não. Só quando

**Lucas F. N. Alves:** Nãurei isso aqui. Isso aqui fui eu que configurei.

**Brazika Brasil:** vou

**Lucas F. N. Alves:** Isso aqui é pro pro Júnior aqui, ó. Léo, isso aqui é um um exemplo de hiding. Isso aqui é um hiding, tá vendo? Isso aqui ele tá querendo uma pessoa para trabalhar para ele,

**Brazika Brasil:** ter

**Lucas F. N. Alves:** pra empresa dele, tá procurando virtual assistant. Essas vagas de hiding a gente vai, tipo, mandar uma mensagem diferente para ele e vai redirecionar tipo para alguém, entendeu? Tipo, a gente vai refazer o aplicativo recrutais, eu vou refazer ele, te dar o ele assim no protótipo e aí essas vagas de Haring vai bater com as as pessoas que a gente tem lá no Recruta Sis e vai recomendar essas pessoas para cá.

  
  

### 00:51:12

  

**Lucas F. N. Alves:** Aí isso vai ser meio que a base ali da da plataforma. Se você quiser, você já pode ir criando essa plataforma.

**Brazika Brasil:** Scraping word

**Lucas F. N. Alves:** É tipo,

**Brazika Brasil:** packers.

**Lucas F. N. Alves:** não precisa nem você fazer o, acho que é bom fazer o scrapers para já pegar ali o o system design e aí você já adiciona lá uma aba para poder esses essas vagas que vem pro como hiring.

**Brazika Brasil:** No se alimentado lá.

**Lucas F. N. Alves:** Aí lá e aí a gente tem que ajustar o agente que classificou isso aqui como hiring, porque isso aqui não é hing. Vou dar uma lapidada nele aqui. Mas esse EV Specialist aqui é é project. Ainda mais que ele deixou claro que ele não precisa do negócio completo, que ele quer lapidar o negócio ali e tals. É hiding. Mas beleza. Aqui não tem profile link porque era anônimo esse cara. Agora, eh, eu vou te mostrar uma parada aqui de como que a IA vai saber a coisa certa. Então eu tenho aqui, ó, fechar esse isolando aqui para eu baixar depois.

  
  

### 00:52:20

  

**Lucas F. N. Alves:** Eh, tem aqui, ó, as o meu calendar que você acho que você vai conseguir acessar ele agora que você logou com o Google. E aí tem um histórico de umas cals, mano. Dessas CS, quer ver se eu achar achar? Tem várias calus, por exemplo, ó. Tem essa que eu tive que ser no N8N e tals, mas as que você acha que a gente precisa focar em reunir primeiro são as que eu fiz com Nicole. Quer ver? Tipo essas aqui,

**Brazika Brasil:** Eu

**Lucas F. N. Alves:** ó. Várias causas assim que eu fiz com Nicole e fica vários arquivos salvos aqui, tá vendo? Fica vários arquivos salvos. Fica alguma transcrição, alguma anotação

**Brazika Brasil:** consigo puxar pela PI aqui os seu sua agenda aí e essas transcrição inteira agora que eu

**Lucas F. N. Alves:** lá conectado aqui no open você consegue,

**Brazika Brasil:** tenho

**Lucas F. N. Alves:** mas acho que o open call vou ter que dar um jeito nele. Você vai ter

**Brazika Brasil:** não consigo pelo o CLI da Google mesmo.

**Lucas F. N. Alves:** que

  
  

### 00:53:11

  

**Brazika Brasil:** Aí ele consegue extrair tudo esses essas transcrição em vídeo e organizar para mim.

**Lucas F. N. Alves:** então se você quiser usar o CLI do Google, eu vou abrir uma sessão aqui. Eu uso vai, quer ver?

**Brazika Brasil:** Não, agora que eu tenho seu face aqui, eu consigo gerar API aqui e mexer aqui. gerar uma sessão.

**Lucas F. N. Alves:** Nãoar não. Já tem gerado aqui. Quer ver? É só abrir no meu codex. Ó, qual conta do Pior que qual conta do codex que será que eu tô?

**Brazika Brasil:** Não,

**Lucas F. N. Alves:** Pera aí. Ô, Cláudia. Provavelmente a gente deve estar em conta diferente do Cloud,

**Brazika Brasil:** Mas a que eu tô aqui é tipo,

**Lucas F. N. Alves:** velho.

**Brazika Brasil:** é só conectar direto do cloud também, né, pelo CLI. Como eu já tô logado aqui na sua conta, ele vai jogar direto pro Google pelo

**Lucas F. N. Alves:** Mas vaiar aqui.

**Brazika Brasil:** pelo tá,

**Lucas F. N. Alves:** É, mas você pode tentar fazer isso aí. Vai, tenta aí.

  
  

### 00:54:08

  

**Lucas F. N. Alves:** Deixa eu ver.

**Brazika Brasil:** pera aí. Mas se desconectar aí a f\*\*\*.

**Lucas F. N. Alves:** Tudo bem,

**Brazika Brasil:** Deixa eu dar aqui. Pera aí. MCP. Pera aí. É, agora o meu aqui já tá automático aqui agora com lama. Vai ficar rodando o dia inteiro.

**Lucas F. N. Alves:** Угу.

**Brazika Brasil:** É no terminal. Não chegando no navegador. Essas gravação tá no Google Drive, tá? Google Drive autenticar. É, abre o navegador. Vouar com a sua conta pro Lucas. É, não vai se conectar não. Tá falando que você já tem tipo quatro serviços cloud

**Lucas F. N. Alves:** É,

**Brazika Brasil:** aqui.

**Lucas F. N. Alves:** então

**Brazika Brasil:** Foi. Vê se saiu aí. É conectado. Deixa eu ver que eu consigo fazer

**Lucas F. N. Alves's Presentation:** Jo.

**Brazika Brasil:** Nic, né, Lucas? Nic.

**Lucas F. N. Alves:** Essa primeira cal que já ensina bastante. Essa cal que já começa lá, você já pode ver ela.

**Brazika Brasil:** Tem que ver para pro agente poder entender e saber responder.

  
  

### 00:57:08

  

**Brazika Brasil:** De acordo com essas causas

**Lucas F. N. Alves:** É, na verdade, você vai fazer uma extração, né, até a gente encontrar ali o Nossa,

**Brazika Brasil:** aí.

**Lucas F. N. Alves:** tem muitas calas aí. vai fazer a extração até a gente encontrar ali o encontrar

**Lucas F. N. Alves's Presentation:** Eu

**Lucas F. N. Alves:** ali o promp ideal,

**Lucas F. N. Alves's Presentation:** M.

**Lucas F. N. Alves:** né, para cá, para calente.

**Brazika Brasil:** Achou bastante puxar aqui a cal da Nicole.

**Lucas F. N. Alves:** Pois é. Ó, essa daqui, ó, começa aqui. Quer ver essa

**Brazika Brasil:** Mandei que é qualquer

**Lucas F. N. Alves:** aqui?

**Brazika Brasil:** data

**Lucas F. N. Alves:** Mas tem um onde eu mostro de fato a tela do negócio.

**Brazika Brasil:** Nicol é só essas aí só que tem.

**Lucas F. N. Alves:** Hum. Talvez vai ter mais. vai ter espalhada, pode ter

**Brazika Brasil:** Ele achou.

**Lucas F. N. Alves:** no

**Brazika Brasil:** Vamos ver uma porqu uma.

**Lucas F. N. Alves:** Deixa eu ver se eu acho aqui, ó, que He.

**Brazika Brasil:** Ele achou Nicole com C também.

  
  

### 00:58:34

  

**Lucas F. N. Alves:** Aqui essa dois. Ixe, essa daqui não ficou gravada. ata da reunião. Isso aqui não deve ter acontecido.

**Brazika Brasil:** curtiu o comentário lá.

**Lucas F. N. Alves's Presentation:** E aí,

**Lucas F. N. Alves:** Aqui eu passei. Isso aqui foi bo do crisão, mano. Só teve essas cal deve ter sido para mim que tem bem mais cal aqui. Será que caiar essas calças? Encaixar essas calc.

**Brazika Brasil:** Ele puxou aqui sete cal. A primeira dia 26/03, a última dia 30/04.

**Lucas F. N. Alves:** me manda os link delas aí no no Google, no WhatsApp.

**Brazika Brasil:** Já tá pegando aqui o resumo e as transcrição. Já entresan Nicole. Esse que você mandou é o quinto vídeo. Ele já tá liberando o bicho aqui. Peraí. Primeiro vídeo me de treinamento. Intro aí. Vou te mandar aí. Confirma se é isso aí mesmo.

  
  

### 01:01:20

  

**Brazika Brasil:** Угу.

**Lucas F. N. Alves:** Mandou pelo Whats. Boa, mano. Aí agora você conseguiu, você conseguiu os links dos docs. Agora vê se você consegue os links das cal, dos vídeos relacionados a esses docs.

**Brazika Brasil:** Como é que é?

**Lucas F. N. Alves:** Você conseguiu os links dos docs, mas vê se você consegue os links de todas as caus relacionadas aos docs. Nossa, mas achou aqui já bem já.

**Brazika Brasil:** já te mandou.

**Lucas F. N. Alves:** Eu vou pegar essa de atendimento aqui,

**Brazika Brasil:** Então você quer que eu analiseo,

**Lucas F. N. Alves:** ó.

**Brazika Brasil:** que ele analise todas essas essas aulas aí para poder entender como é que vai responder o cliente lá,

**Lucas F. N. Alves:** Uhum.

**Brazika Brasil:** melhorar o jeito que ele tá lá, tipo, ele já tá respondendo, tipo, o jeito que ele responde por inteiro no comentário ou só no ADM.

**Lucas F. N. Alves:** tudo. Quer ver? Eu vou pegar aqui, eu vou adicionar no vou adicionar no notebook al te ajudar a fazer um prompt

**Brazika Brasil:** Faz um promptí para mim.

**Lucas F. N. Alves:** aqui.

**Brazika Brasil:** É, ele pegou o Zink aqui a última

  
  

### 01:02:55

  

**Lucas F. N. Alves:** Tem, ah, tem um notebook LM aqui já com vários desses treinamentos aqui adicionados. 2 4 com esse notebook aqui,

**Brazika Brasil:** integrar aqui também.

**Lucas F. N. Alves:** eu acho que você vai conseguir tudo.

**Brazika Brasil:** tá nesse mesmo Google seu.

**Lucas F. N. Alves:** Tirei, tá no mesmo

**Brazika Brasil:** Tá, então é só botar o MCP também ou API,

**Lucas F. N. Alves:** Google.

**Brazika Brasil:** se tiver.

**Lucas F. N. Alves:** É, só dá para botar o NCP aí também.

**Brazika Brasil:** Então eu vou organizar também.

**Lucas F. N. Alves:** Adicionei esses aqui, novas fontes. Olha, existem fontes.

**Brazika Brasil:** Aquele setzinho de música eu refiz ele.

**Lucas F. N. Alves:** Nossa, aquele ficou doido demais. Deixa eu, deixa eu ali rapidão. Ô Léo,

**Brazika Brasil:** Tem

**Lucas F. N. Alves:** aí eu vou mexer com o negócio da telemedicina. Você tem acesso a esse notebook LM aí?

**Brazika Brasil:** só escreve, me dá um norte assim que preciso fazer e daí eu já vou começar aí, ó os vídeos aí, ó,

**Lucas F. N. Alves:** Deixa eu ver aqui o que que você mandou.

  
  

### 01:05:10

  

**Brazika Brasil:** os link da da SCAL. Ah, ele achou até uma uma pasta aqui, ó.

**Lucas F. N. Alves:** Boa,

**Brazika Brasil:** Acho que nada a ver. Várias do projeto face com Léo. Ó legal.

**Lucas F. N. Alves:** boa, boa. Isso aqui é muito bom.

**Brazika Brasil:** Esse notebook LM aqui que é para mim

**Lucas F. N. Alves:** Eu te mandei um link aí,

**Brazika Brasil:** usar.

**Lucas F. N. Alves:** deixa eu ver aqui, no caso.

**Brazika Brasil:** Deixa eu ver se abriu aqui. Ah, pediu para liberar. Libera aí. É, vai ser anúncio Brasí.

**Lucas F. N. Alves:** Não, eu acho que ele não libera não. Você tem que entrar nele logado no meu

**Brazika Brasil:** É, se tá

**Lucas F. N. Alves:** M.

**Brazika Brasil:** certo. Bom, beleza. Vou vou jogar isso aqui tudo para ele aqui. Vamos ver o que ele faz.

**Lucas F. N. Alves:** Tipo, você vai usar isso aqui para identificar nas cals, vai dar uma olhada ali, uma assistida nas cal e aí depois a gente vai processar essas caus e fazer a análise do que tava mostrando também nas calus.

  
  

### 01:06:37

  

**Lucas F. N. Alves:** Tem um skill que eu vou te mandar ela aqui, ó. Deixa eu pegar aqui.

**Brazika Brasil:** W

**Lucas F. N. Alves:** M. Pera aí. Já achei aqui o link das duas.

**Brazika Brasil:** E agora que eu tenho acesso à CLC call, eu também mais para frente consegui replicar o vídeo que você fez aí da apresentação, implementar no no sistema.

**Lucas F. N. Alves:** Mano, sim, velho. Nós vamos aprimorar para c\*\*\*\*\*\* esse vídeo da apresentação aí. Nós vamos tipo ter essa apresentação para tudo. Depois que você extrair todas essas causas, que vocês tipo assim meio que se situar em que que é essas causas, aí nós vamos fazer uma análise mais aprofundada delas e vamos registrar tudo lá no Notion, tá ligado? como projeto. Então, por exemplo, essas com a Nicole, essas que eu tô fazendo com você, tipo, tudo relacionado a esse ecossistema de aquisição e atendimento de leaders, esse é o projeto nosso, o projeto Automatrix e tal. Então, a gente vai organizar tudo isso no nosso projeto lá no Nosso, que eu acho que eu até abri um projeto lá para nós, pra gente poder começar a configurar esses agentes.

  
  

### 01:09:23

  

**Lucas F. N. Alves:** Aí a gente vai eh identificar, tipo, organizar todos os projetos lá e ter a os arquivos de vídeo das explicações dos projetos organizados. E aí a gente vai começar a criar apresentação de tudo. Os essas três primeiras vai ser essa que eu tô fazendo do Cris,

**Brazika Brasil:** M.

**Lucas F. N. Alves:** que já tá de certa forma boa, a sua do Brasica, porque aí a gente vai mostrar tipo o que que alguém que aprendeu consegue fazer

**Brazika Brasil:** M.

**Lucas F. N. Alves:** e a gente vai mostrar essa do da aquisição de leads. Aí a gente vai mostrando todas, mano. Tipo, nós vamos tentar mapear, listar todas e mostrar todas, tipo assim, deixar todas, tá ligado?

**Brazika Brasil:** Uhum.

**Lucas F. N. Alves:** Porque com essa base de dados a gente consegue criar a plataforma, consegue alimentar os agentes aí e tudo mais. Então, para agora o que você tem que fazer é tipo dar uma explorada nas cal e criar promptes aí vários arquivos, né, que você vai criar e vai ler, vai me mandar. Eh, com as instruções tipo mais lapidadas assim, sabe, do dos agentes. Você vai ver tudo isso e falar: "Entendi, mano, entendi aqui o esquema. O negócio é mais ou menos esse aqui e tals." E eu vou te mandar a gravação dessa CUD agora também para você

  
  

### 01:10:43

  

**Lucas F. N. Alves:** poder.

**Brazika Brasil:** Já mande aí, já vou meter marcha

**Lucas F. N. Alves:** A gente precisa de iniciar esse processo de organização e estruturação dessas gravações de call para criar uma

**Brazika Brasil:** aqui.

**Lucas F. N. Alves:** base de dados métrica. Fechou?

**Brazika Brasil:** Já manda aí essa cal agora transcrita para

**Lucas F. N. Alves:** Vou mandar também a gravação dela.

**Brazika Brasil:** mim.

**Lucas F. N. Alves:** Agora você tá com a conexão com o meu Google, você consegue detonar. Aí eu tô fazendo mais duas coisas só para finalizar que tem que só para você saber dessas duas coisas. Uma delas é a aplicação de indexação de caus. Então eu fiz uma que indexa as cal e aí ela salva as cal tudo na memória. Tipo, ela vai lembrar dos frames de todas as cal. Essa daí nós vamos fazer ela por último, por último de tudo que você que a gente vai passar essas caus lá. Mas tem uma outra que a Iara começou a fazer de organização das caus no

**Brazika Brasil:** É,

**Lucas F. N. Alves:** Sheon.

**Brazika Brasil:** eu vi que você botou no GitHub lá, tava dando umaada

**Lucas F. N. Alves:** Eh, depois nós vamos nós vamos subir essas calus para lá,

  
  

### 01:11:38

  

**Brazika Brasil:** ontem.

**Lucas F. N. Alves:** entendeu? Mas se você quiser já baixar essas cálculas aí pro seu PC e tentar reduzir o tamanho delas sem perder a qualidade, já pode ir. Mas o mais importante é tipo você realmente assistir as causas. Eh,

**Brazika Brasil:** vai dar os agentes de novo,

**Lucas F. N. Alves:** est é,

**Brazika Brasil:** né? Fazer eles responder melhor, analisar melhor

**Lucas F. N. Alves:** mas tipo não muda a configuração dos agentes ainda, só extrai e monta os prontos assim, sabe? De coisas que a gente vai Uhum.

**Brazika Brasil:** aqueles agente MD, aqueles bagulhos que você fez lá.

**Lucas F. N. Alves:** Vou te mandar aqui, vou te mandar minhas skill aqui, ó. Agency os eh, assembly, automatrix context, que mais walkthrough vídeo walk through. A mais importante é essa. Deixa eu ver se tem mais algum aqui. Não é só essas mesmo. Na verdade, eu vou mandar só essa aqui por enquanto para mim. Walk to scrits. Esse essa video walkthrough é a que gera aquele sht hub com a transcrição, saca?

  
  

### 01:13:29

  

**Lucas F. N. Alves:** Aí você vai você pode passar essa videon todas essas causas aí, porque tipo essa transcrição do Google ela é boa para você identificar ali algumas coisas, mas a do assembly que deixa perfeitinho com time stamps e ele frames também. Aí vai dar para ver uns frames,

**Brazika Brasil:** Boa.

**Lucas F. N. Alves:** sacou? Então você usa essa skill video true aí nas causas, vai assistindo nas cal, fazendo as transcrições e analisando aí para você poder entender como que atende os clientes.

**Brazika Brasil:** Top.

**Lucas F. N. Alves:** Coisas que você você precisar entender aí,

**Brazika Brasil:** Vou fazer.

**Lucas F. N. Alves:** coisa que qualquer coisa vai me perguntando

**Brazika Brasil:** Fechou.

**Lucas F. N. Alves:** aí.

**Brazika Brasil:** Foi. Fechou. Depois dá uma opinião aí no trampo aí se eu tô falando certo, se tem alguma coisa que eu preciso

**Lucas F. N. Alves:** Tá da hora. Tá da hora. É só tipo,

**Brazika Brasil:** mudar.

**Lucas F. N. Alves:** eh, eu só preciso ver o, o negócio funcionando, tipo, melhor assim, igual se esse negócio aí do, do Olama Cloud resolver mesmo, mano, show de bola. Mas aí no final do dia você vai monitorando aí você me dá

  
  

### 01:14:36

  

**Brazika Brasil:** É, mas você acha que eu tô entregando resultado?

**Lucas F. N. Alves:** um

**Brazika Brasil:** Eu tô trampando legal. Tem alguma coisa quer que eu muda em relação a isso,

**Lucas F. N. Alves:** Não,

**Brazika Brasil:** não ao projeto,

**Lucas F. N. Alves:** eu tá tá suave,

**Brazika Brasil:** o a ao trampo

**Lucas F. N. Alves:** tá suave.

**Brazika Brasil:** mesmo.

**Lucas F. N. Alves:** A gente só tem que a gente só tem que tipo ter mais organização lá no no negócio da gestão de projeto, mas isso aí nós vamos desenvolver juntos da questão de de fazer os trem assim,

**Brazika Brasil:** Fechou?

**Lucas F. N. Alves:** tá? Tá massa.

**Brazika Brasil:** Então beleza, vamos lá. Bora. Você fala que virou da cal aí do Júnior.

**Lucas F. N. Alves:** Beleza. Como é que é?

**Brazika Brasil:** Você fala que que virou da cal do

**Lucas F. N. Alves:** Beleza. Vou te eu te falo.

**Brazika Brasil:** Júnior.

**Lucas F. N. Alves:** Mas o nosso lá a nossa lá é o é o da vistoria. Esse de agora vai ser do da telemedicina.

**Brazika Brasil:** É, é de ser mesmo.

**Lucas F. N. Alves:** passar os treinos do WhatsApp dele. Mas eh depois que você depois que a gente resolver essa parada aqui do banco de dados, que a gente pegar tipo que a gente meio que entender o que que a gente vai fazer para resolver de fato esse banco de dados e essa tarefa tiver tipo correndo assim bem, aí eu vou te passar as paradas do WhatsApp dele que eu já fiz bastante coisa lá com ele já também no WhatsApp.

**Brazika Brasil:** Fechou,

**Lucas F. N. Alves:** Beleza,

**Brazika Brasil:** fechou. Valeu. Até depois, então.

**Lucas F. N. Alves:** fechou. Então, valeu até daqui a pouco.

  
  

### A transcrição foi encerrada após 01:16:06

  

*Esta transcrição editável foi gerada por computador e pode conter erros. As pessoas também podem alterar o texto depois que ele for cr
