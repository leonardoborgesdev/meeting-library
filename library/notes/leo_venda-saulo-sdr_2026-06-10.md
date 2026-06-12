# Reunião — Saulo — SDR WhatsApp (GVG Gerência)

- **Data:** 2026-06-10
- **Pessoa (lib):** Leonardo (call comercial Automatrix; Leo na frente SDR)
- **Participantes:** Lucas F. N. Alves, GVG Gerência (Saulo)
- **Projeto:** SDR WhatsApp / GVG (venda + escopo)
- **Vídeo (Drive):** https://drive.google.com/file/d/1ccwmn-ScRjp0wC0B7KtT7j75Pb0wRDf4/view (102 MB)
- **Notas Gemini (PT):** doc 1yo3jbKnvuTvP54oWJOIvriKJ7oj4d57dxD8RjFEpkxQ

## Resumo
Discussão sobre migração para API oficial do WhatsApp com foco em integrações de sistema e segurança.

- **Problemas com API anterior:** API não oficial (Z-API) causou ban de número importante e ausência de integração com o CRM. Sem métricas/dashboards → sem análise nem histórico.
- **Transição para API oficial:** decisão de migrar para a API oficial (Cloud/Business) por segurança e tracking. Integra Google Calendar, pagamentos e dashboards.
- **Metodologia e fluxo:** Spin Selling com foco em scripts; testes constantes para ajuste fino antes do go-live.

## Próximas etapas
- [Lucas] Orçar implementação do SDR (dev + suporte) — enviar até a tarde seguinte.
- [Lucas] Criar grupo WhatsApp para centralizar orçamento/infos.
- [GVG] Enviar documentação técnica (portfólio, metodologia, tom de voz, processo de vendas).
- [GVG] Responder questionário de qualificação (critérios + fluxo comercial; coordenar com Bruna).
- [Lucas] Disponibilizar ambiente de teste (link de agente) para validação e feedback.

## Detalhes-chave
- Ban no WhatsApp = mandar msg para quem não te adicionou / não falou nas últimas 24h; API não oficial pode banir só pelo uso.
- Stack alvo: WhatsApp API oficial + RD Station (CRM/VoIP/contratos) + Google Calendar + plataforma de pagamento (link/Pix) + N8N + Power BI/Looker.
- Pediu sistema de ALERTAS (saber quando o agente cai) — dor do fornecedor anterior.
- Metodologia desejada: Spin Selling; tom de voz da CEO; ticket define se vai para link de pagamento ou agendamento com closer.
