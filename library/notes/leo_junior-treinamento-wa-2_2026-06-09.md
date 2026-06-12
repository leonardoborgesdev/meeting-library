# Junior — Treinamento IA — WhatsApp 2

- **Data:** 2026-06-09
- **Pessoa (lib):** Leonardo (por instrução; call é com cliente Junior/Camila)
- **Participantes:** Lucas F. N. Alves, Camila, Luis Henrique Genda de Almeida (convidado vergamini65@gmail.com)
- **Projeto:** SDR imobiliária (Plá / Salesforce + Kinbox)
- **Vídeo (Drive):** https://drive.google.com/file/d/1rVf-BVhO0_s0XhTv-doCdUPpbwmYs0dq/view (134 MB)
- **Notas Gemini (PT):** doc 1GkfztOqEV4j0OON-jDDrzNQ17Y-kelGPHvZ9Q3hiXhc

## Resumo
Integração de IA com Salesforce e otimização de fluxos de atendimento automatizado.

- **Arquitetura de agentes:** baseada em **sessão** e **canal** — memória isolada (uma sessão por lead) ou compartilhada. Um agente pode orquestrar vários leads, cada um com sessão única.
- **Fluxo operacional:** Cron job a cada 20 min processa leads do Salesforce → API → web hook valida/cria contato e conversa no Kinbox → bot pede ao cliente iniciar contato.
- **Padronização de dados:** salvar nome do cliente como `nome + empreendimento + bloco + unidade` (vindo do Salesforce). Permissões do Kinbox limitam o usuário criado (só envio); automações ficam na conta principal da Camila.

## Próximas etapas
- [Lucas] Enviar vídeo explicativo da IA para a equipe assistir.
- [Lucas] Demonstrar IA na prática com o Junior presente.
- [Lucas] Conectar WhatsApp para testes na próxima reunião.
- [Lucas] Padronizar contatos no Salesforce (nome/empreendimento/bloco/unidade).
- [Lucas] Validar canal para iniciar disparos automáticos.
- [Lucas] Agendar reunião de acompanhamento (mesmo horário no dia seguinte).
