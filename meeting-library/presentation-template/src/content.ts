// content.ts — DADOS do vídeo (o agente preenche isto a partir do repositório).
// O template é genérico: estas cenas/valores são só um exemplo (Meeting Library).
// O orquestrador sobrescreve este arquivo por job antes de renderizar.
//
// =====================================================================
// TIPOS DE CENA DISPONÍVEIS (campo `type`) — para quem gera o content:
// Todas são responsivas (16:9 e 9:16) e animadas. Arrays opcionais.
//
//  intro    { title, subtitle, kpis:[{v,label}], narration, dur? }
//             abertura com logo + subtítulo + KPIs grandes.
//
//  screens  { heading, sub?, cards:[{title,desc,icon?}], narration, dur? }
//             grade de cards de recursos/telas (1 col no 9:16).
//
//  flow     { heading, sub?, nodes:[{icon?|emoji?|txt?, label, sub, brand?}], narration, dur? }
//             pipeline horizontal (16:9) / vertical (9:16) com conectores.
//
//  stack    { heading, sub?, groups:[{title, items:[{icon?|txt?, mono?, brand?, name, role, tag}]}], narration, dur? }
//             integrações/tech agrupadas em colunas.
//
//  metrics  { heading?, sub?, items:[{v, label, sub?, brand?}], narration, dur? }
//             KPIs/números grandes em destaque, estilo dashboard. Count-up animado.
//
//  quote    { text, author?, role?, avatar?, narration, dur? }
//             depoimento/frase de impacto centralizada com autor opcional.
//
//  compare  { heading?, sub?, left:{title, items:string[], tone?}, right:{title, items:string[], tone?}, narration, dur? }
//             antes/depois ou 2 colunas lado a lado. tone: "bad"|"good"|"neutral".
//
//  cta      { title, url?, button?, tagline?, narration, dur? }
//             chamada final com botão/URL (estilo outro). `button` = texto do botão.
//
//  outro    { title, url, tagline?, narration, dur? }
//             encerramento com logo + URL.
// =====================================================================

export type Kpi = { v: string; label: string };
export type FeatureCard = { title: string; desc: string; icon?: string };
export type FlowNode = { icon?: string; emoji?: string; txt?: string; label: string; sub: string; brand?: string };
export type StackItem = { icon?: string; txt?: string; mono?: boolean; brand?: string; name: string; role: string; tag: string };
export type StackGroup = { title: string; items: StackItem[] };
export type Metric = { v: string; label: string; sub?: string; brand?: string };
export type CompareCol = { title: string; items: string[]; tone?: "bad" | "good" | "neutral" };

export type Scene =
  | { type: "intro"; title: string; subtitle: string; kpis: Kpi[]; narration: string; dur?: number }
  | { type: "screens"; heading: string; sub?: string; cards: FeatureCard[]; narration: string; dur?: number }
  | { type: "flow"; heading: string; sub?: string; nodes: FlowNode[]; narration: string; dur?: number }
  | { type: "stack"; heading: string; sub?: string; groups: StackGroup[]; narration: string; dur?: number }
  | { type: "metrics"; heading?: string; sub?: string; items: Metric[]; narration: string; dur?: number }
  | { type: "quote"; text: string; author?: string; role?: string; avatar?: string; narration: string; dur?: number }
  | { type: "compare"; heading?: string; sub?: string; left: CompareCol; right: CompareCol; narration: string; dur?: number }
  | { type: "cta"; title: string; url?: string; button?: string; tagline?: string; narration: string; dur?: number }
  | { type: "outro"; title: string; url: string; tagline?: string; narration: string; dur?: number };

export type Content = {
  brand: { name: string; primary: string; accent?: string; ink?: string; gold?: string };
  format: "16:9" | "9:16";
  lang: "pt" | "en";
  voice: string;
  scenes: Scene[];
};

export const CONTENT: Content = {
  brand: { name: "Meeting Library", primary: "#2275E8", accent: "#E2F0FF", ink: "#0B1723", gold: "#DFB127" },
  format: "16:9",
  lang: "pt",
  voice: "Eric",
  scenes: [
    {
      type: "intro",
      title: "Meeting Library",
      subtitle: "O catálogo inteligente das calls da Automatrix",
      kpis: [{ v: "112+", label: "gravações" }, { v: "10", label: "projetos" }, { v: "55", label: "frames/call" }],
      narration: "Meeting Library — o catálogo inteligente de todas as calls da Automatrix.",
    },
    {
      type: "screens",
      heading: "O que o sistema faz",
      sub: "principais telas e recursos",
      cards: [
        { title: "Biblioteca", desc: "Catálogo no estilo Notion, 5 visualizações" },
        { title: "Transcrição", desc: "AssemblyAI pt-BR com walkthrough visual" },
        { title: "Chat IA", desc: "Busca por linguagem natural (Gemini)" },
        { title: "Apresentações", desc: "Gera vídeos das aplicações" },
      ],
      narration: "A tela principal é uma biblioteca estilo Notion, com transcrição, chat e apresentações.",
    },
    {
      type: "metrics",
      heading: "Em números",
      sub: "o acervo hoje",
      items: [
        { v: "112+", label: "gravações", sub: "indexadas", brand: "#2275E8" },
        { v: "10", label: "projetos", sub: "cobertos", brand: "#1FA463" },
        { v: "6.000+", label: "frames", sub: "no Supabase", brand: "#8E75F8" },
        { v: "24/7", label: "online", sub: "no Fly.io", brand: "#DFB127" },
      ],
      narration: "Hoje são mais de cem gravações, dez projetos e milhares de frames, no ar o tempo todo.",
    },
    {
      type: "flow",
      heading: "Pipeline automático",
      sub: "como uma call vira card",
      nodes: [
        { icon: "googledrive", label: "Google Drive", sub: "rclone puxa as gravações", brand: "#1FA463" },
        { icon: "ffmpeg", label: "ffmpeg", sub: "áudio + 55 frames", brand: "#0B7A3B" },
        { txt: "AAI", label: "AssemblyAI", sub: "transcrição pt-BR", brand: "#6366F1" },
        { icon: "supabase", label: "Supabase", sub: "frames públicos", brand: "#3FCF8E" },
      ],
      narration: "O vídeo vem do Drive, o ffmpeg extrai os quadros, a AssemblyAI transcreve e o Supabase serve tudo.",
    },
    {
      type: "compare",
      heading: "Antes & depois",
      sub: "o que mudou na operação",
      left: { title: "Antes", tone: "bad", items: ["Gravações perdidas no Drive", "Sem busca por conteúdo", "Revisão manual de horas", "Conhecimento na cabeça de poucos"] },
      right: { title: "Depois", tone: "good", items: ["Catálogo único e buscável", "Chat IA sobre todas as calls", "Walkthrough visual automático", "Acervo seguro e compartilhável"] },
      narration: "Antes, o conhecimento se perdia. Depois, virou um acervo buscável por qualquer pessoa.",
    },
    {
      type: "stack",
      heading: "Aplicações & integrações",
      groups: [
        { title: "IA", items: [{ txt: "AAI", brand: "#6366F1", name: "AssemblyAI", role: "transcrição pt-BR", tag: "universal-2" }, { icon: "googlegemini", brand: "#8E75F8", name: "Gemini", role: "chat do acervo", tag: "2.5-flash" }] },
        { title: "Plataforma", items: [{ icon: "python", brand: "#3776AB", name: "Python", role: "server stdlib", tag: "backend" }, { icon: "flydotio", mono: true, brand: "#0B1723", name: "Fly.io", role: "hospedagem 24/7", tag: "hosting" }] },
      ],
      narration: "Por baixo: AssemblyAI e Gemini na inteligência, Python e Fly na plataforma.",
    },
    {
      type: "quote",
      text: "Achei a call de onboarding em 10 segundos — sem reassistir nada.",
      author: "Equipe Automatrix",
      role: "uso diário",
      narration: "Para quem usa: achar a call certa virou questão de segundos.",
    },
    {
      type: "outro",
      title: "Meeting Library",
      url: "meet.automatrix-ai.com",
      tagline: "Todo o conhecimento das calls — buscável e seguro.",
      narration: "Meeting Library. Em meet ponto automatrix ai ponto com.",
    },
  ],
};
