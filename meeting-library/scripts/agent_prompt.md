# Tarefa: gerar o content.ts de um vídeo explainer a partir de um repositório

Você é um agente que analisa um repositório de software e produz os DADOS de um
vídeo de apresentação (explainer) sobre ele. Você NÃO escreve componentes React —
só produz um objeto `content` estruturado. Um template Remotion já renderiza esse
objeto num vídeo polido.

## Passos
1. Explore o repositório em `{REPO_DIR}`. Leia README, docs, package.json/requirements,
   o frontend (telas, paleta de cores no CSS), e a arquitetura (APIs, serviços, modelos).
2. Extraia FATOS REAIS: nome/marca, cor primária (hex — converta de oklch se preciso),
   principais telas/recursos, o pipeline/fluxo de dados, e a stack (apps/APIs com papel).
3. Escreva o arquivo `{OUT_FILE}` exatamente no formato abaixo (TypeScript), em {LANG}
   ({LANG_NAME}). Use no máximo 5–7 cenas. Narração: 1 frase curta e natural por cena,
   números por extenso, sem jargão. NÃO invente dados que não estão no repo.

## Formato EXATO do arquivo a escrever (`{OUT_FILE}`)
```ts
import type { Content } from "./content";
export const CONTENT: Content = {
  brand: { name: "<nome>", primary: "<#hex da cor primária>", accent: "<#hex claro>", ink: "#0B1723", gold: "#DFB127" },
  format: "{FORMAT}",
  lang: "{LANG}",
  voice: "{VOICE}",
  scenes: [
    { type: "intro", title: "<marca>", subtitle: "<o que é, 1 linha>",
      kpis: [{ v: "<num>", label: "<rótulo>" }, ...3 no máx],
      narration: "<1 frase>" },
    { type: "screens", heading: "<título>", sub: "<subtítulo opcional>",
      cards: [{ title: "<recurso>", desc: "<descrição curta>" }, ...3-6],
      narration: "<1 frase>" },
    { type: "flow", heading: "<título>", sub: "<opcional>",
      nodes: [{ icon: "<slug simpleicons OU vazio>", emoji: "<emoji se sem icon>", txt: "<2-3 letras se sem icon/emoji>", label: "<nome>", sub: "<o que faz>", brand: "<#hex>" }, ...3-6],
      narration: "<1 frase>" },
    { type: "stack", heading: "Aplicações & integrações",
      groups: [{ title: "<grupo>", items: [{ icon: "<slug ou vazio>", txt: "<iniciais se sem icon>", mono: <true se logo preto>, brand: "<#hex>", name: "<nome>", role: "<papel>", tag: "<modelo/versão>" }] }],
      narration: "<1 frase>" },
    { type: "outro", title: "<marca>", url: "<domínio do projeto se houver>", tagline: "<frase de efeito>",
      narration: "<1 frase>" },
  ],
};
```

## Tipos de cena disponíveis (escolha 5–7 que façam sentido pro repo, em boa ordem narrativa)
- `intro` { title, subtitle, kpis:[{v,label}], narration }
- `screens` { heading, sub?, cards:[{title,desc,icon?}], narration } — recursos/telas
- `metrics` { heading?, sub?, items:[{v,label,sub?,brand?}], narration } — números grandes/KPIs
- `flow` { heading, sub?, nodes:[{icon?|emoji?|txt?, label, sub, brand?}], narration } — pipeline
- `compare` { heading?, sub?, left:{title,items:string[],tone?}, right:{title,items:string[],tone?}, narration } — antes/depois (tone: "bad"|"good"|"neutral")
- `quote` { text, author?, role?, narration } — frase de impacto/depoimento
- `stack` { heading, sub?, groups:[{title, items:[{icon?|txt?, mono?, brand?, name, role, tag}]}], narration } — apps/APIs
- `cta` { title, url?, button?, tagline?, narration } — chamada à ação
- `outro` { title, url, tagline?, narration } — encerramento
Comece com `intro` e termine com `outro` (ou `cta`). Use `metrics`/`compare`/`quote` quando o repo tiver números, um "antes/depois" claro, ou valor pra destacar.

## Ícones (campo `icon`)
Use slugs do simpleicons.org quando a marca tiver logo conhecido (ex.: `supabase`,
`googledrive`, `ffmpeg`, `python`, `react`, `nextdotjs`, `vercel`, `cloudflare`,
`openai`, `googlegemini`, `notion`, `telegram`, `tailwindcss`, `postgresql`, `docker`,
`flydotio`, `nodedotjs`, `typescript`). Para logos monocromáticos (preto) ponha `mono: true`.
Se não houver logo, deixe `icon` vazio e use `emoji` (cena flow) ou `txt` (iniciais).

## Regras
- Responda SOMENTE escrevendo o arquivo `{OUT_FILE}`. Não imprima explicações.
- O objeto deve ser TypeScript válido e casar com o tipo `Content` de `./content`.
- Cores em hex (#RRGGBB). Tudo em {LANG_NAME}.
