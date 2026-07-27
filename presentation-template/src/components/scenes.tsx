import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Stage } from "./Stage";
import { Icon } from "./Icon";
import { Logo } from "./Logo";
import { C, FONT, SHADOW, PORTRAIT } from "../theme";
import { pop, lerp } from "../anim";
import type { Scene } from "../content";

const PAD = PORTRAIT ? 72 : 50;
// helpers responsivos: 1º valor = retrato (9:16), 2º = paisagem (16:9)
const rp = <T,>(portrait: T, landscape: T): T => (PORTRAIT ? portrait : landscape);
const HEADING = rp(42, 26);
const SUBHEAD = rp(20, 14);

/* ---------- INTRO ---------- */
export const IntroScene: React.FC<{ s: Extract<Scene, { type: "intro" }> }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const lp = pop(frame, fps, 6, 26);
  const subP = lerp(frame, 28, 50, 0, 1);
  return (
    <Stage>
      <div style={{ position: "absolute", inset: 0, background: `radial-gradient(circle at 30% 20%, ${C.accent}, ${C.bg} 55%), radial-gradient(circle at 80% 90%, ${C.goldSoft}, transparent 50%)`, fontFamily: FONT, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: PAD, boxSizing: "border-box", textAlign: "center" }}>
        <div style={{ transform: `scale(${0.85 + 0.15 * lp})`, opacity: lp }}>
          <Logo size={rp(72, 60)} />
        </div>
        <div style={{ fontSize: rp(30, 19), color: C.muted, marginTop: rp(40, 22), opacity: subP, transform: `translateY(${(1 - subP) * 12}px)`, fontWeight: 500, maxWidth: rp(600, 760), lineHeight: 1.35 }}>{s.subtitle}</div>
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: rp(44, 46), marginTop: rp(80, 44) }}>
          {(s.kpis||[]).map((k, i) => {
            const p = lerp(frame, 46 + i * 8, 70 + i * 8, 0, 1);
            return (
              <div key={i} style={{ textAlign: "center", opacity: p, transform: `translateY(${(1 - p) * 14}px)` }}>
                <div style={{ fontSize: rp(56, 42), fontWeight: 800, color: C.primary, letterSpacing: -1 }}>{k.v}</div>
                <div style={{ fontSize: rp(18, 13), color: C.muted, marginTop: 4 }}>{k.label}</div>
              </div>
            );
          })}
        </div>
      </div>
    </Stage>
  );
};

/* ---------- SCREENS (cards de recursos) ---------- */
export const ScreensScene: React.FC<{ s: Extract<Scene, { type: "screens" }> }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cols = PORTRAIT ? 1 : (s.cards||[]).length > 4 ? 3 : 2;
  return (
    <Stage>
      <div style={{ position: "absolute", inset: 0, background: C.bg, fontFamily: FONT, padding: PAD, boxSizing: "border-box", display: "flex", flexDirection: "column", justifyContent: PORTRAIT ? "center" : "flex-start" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}><Logo size={rp(30, 22)} /></div>
        <div style={{ fontSize: HEADING, fontWeight: 800, color: C.ink, marginTop: rp(28, 16) }}>{s.heading}</div>
        {s.sub && <div style={{ fontSize: SUBHEAD, color: C.muted, marginTop: 4 }}>{s.sub}</div>}
        <div style={{ display: "grid", gridTemplateColumns: `repeat(${cols},1fr)`, gap: rp(22, 16), marginTop: rp(44, 28) }}>
          {(s.cards||[]).map((c, i) => {
            const p = pop(frame, fps, 14 + i * 8, 20);
            return (
              <div key={i} style={{ background: C.panel, border: `1px solid ${C.border}`, borderRadius: 16, padding: rp("26px 28px", "18px 20px"), boxShadow: SHADOW.md, borderLeft: `${rp(6, 4)}px solid ${C.primary}`, opacity: p, transform: `translateY(${(1 - p) * 16}px)` }}>
                <div style={{ fontSize: rp(26, 17), fontWeight: 800, color: C.ink }}>{c.title}</div>
                <div style={{ fontSize: rp(18, 13), color: C.muted, marginTop: rp(10, 7), lineHeight: 1.4 }}>{c.desc}</div>
              </div>
            );
          })}
        </div>
      </div>
    </Stage>
  );
};

/* ---------- FLOW (pipeline) ---------- */
export const FlowScene: React.FC<{ s: Extract<Scene, { type: "flow" }> }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const N = (s.nodes||[]).length;
  const node = rp(110, 70);
  return (
    <Stage>
      <div style={{ position: "absolute", inset: 0, background: C.bg, fontFamily: FONT, padding: PAD, boxSizing: "border-box", display: "flex", flexDirection: "column" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}><Logo size={rp(30, 22)} /></div>
        <div style={{ fontSize: HEADING, fontWeight: 800, color: C.ink, marginTop: rp(28, 16) }}>{s.heading}</div>
        {s.sub && <div style={{ fontSize: SUBHEAD, color: C.muted, marginTop: 4 }}>{s.sub}</div>}
        <div style={{ display: "flex", flex: 1, flexDirection: PORTRAIT ? "column" : "row", alignItems: "center", justifyContent: "center", gap: PORTRAIT ? 22 : 0 }}>
          {(s.nodes||[]).map((n, i) => {
            const p = pop(frame, fps, 12 + i * 16, 22);
            const edge = lerp(frame, 22 + i * 16, 40 + i * 16, 0, 1);
            const brand = n.brand || C.primary;
            return (
              <React.Fragment key={i}>
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", opacity: p, transform: `translateY(${(1 - p) * 20}px)`, width: PORTRAIT ? "auto" : 150 }}>
                  {n.icon ? <Icon name={n.icon} size={node} borderColor={brand} /> : (
                    <div style={{ width: node, height: node, borderRadius: rp(26, 18), background: "#fff", border: `${rp(2, 1.5)}px solid ${brand}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: n.emoji ? rp(46, 30) : rp(26, 18), fontWeight: 800, color: brand, boxShadow: "0 4px 14px rgba(11,23,35,.07)" }}>{n.emoji || n.txt}</div>
                  )}
                  <div style={{ fontSize: rp(22, 13), fontWeight: 700, color: C.ink, marginTop: rp(16, 12), textAlign: "center" }}>{n.label}</div>
                  <div style={{ fontSize: rp(16, 10.5), color: C.muted, marginTop: rp(5, 3), textAlign: "center", maxWidth: rp(320, 150), lineHeight: 1.3 }}>{n.sub}</div>
                </div>
                {i < N - 1 && (
                  PORTRAIT
                    ? <div style={{ width: 4, height: 38, background: C.surface3, borderRadius: 99, position: "relative", overflow: "hidden" }}><div style={{ position: "absolute", top: 0, width: "100%", height: `${edge * 100}%`, background: C.primary }} /></div>
                    : <div style={{ flex: "0 0 40px", height: 3, background: C.surface3, borderRadius: 99, position: "relative", overflow: "hidden", marginTop: -34 }}><div style={{ position: "absolute", left: 0, height: "100%", width: `${edge * 100}%`, background: C.primary }} /></div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </Stage>
  );
};

/* ---------- STACK ---------- */
export const StackScene: React.FC<{ s: Extract<Scene, { type: "stack" }> }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  let idx = 0;
  const cols = PORTRAIT ? 1 : Math.min((s.groups||[]).length, 4);
  return (
    <Stage>
      <div style={{ position: "absolute", inset: 0, background: C.bgMuted, fontFamily: FONT, padding: PAD, boxSizing: "border-box", display: "flex", flexDirection: "column", justifyContent: PORTRAIT ? "center" : "flex-start" }}>
        <div style={{ fontSize: HEADING, fontWeight: 800, color: C.ink }}>{s.heading}</div>
        {s.sub && <div style={{ fontSize: SUBHEAD, color: C.muted, marginTop: 3 }}>{s.sub}</div>}
        <div style={{ display: "grid", gridTemplateColumns: `repeat(${cols},1fr)`, gap: rp(26, 14), marginTop: rp(36, 18), alignItems: "start" }}>
          {(s.groups||[]).map((g) => (
            <div key={g.title}>
              <div style={{ fontSize: rp(15, 10), fontWeight: 800, letterSpacing: 1, textTransform: "uppercase", color: C.primary, marginBottom: rp(14, 9) }}>{g.title}</div>
              <div style={{ display: "flex", flexDirection: "column", gap: rp(14, 9) }}>
                {(g.items||[]).map((it) => {
                  const ap = pop(frame, fps, 6 + idx++ * 5, 18);
                  const brand = it.brand || C.primary;
                  return (
                    <div key={it.name} style={{ background: C.panel, border: `1px solid ${C.border}`, borderRadius: rp(16, 12), padding: rp("18px 20px", "11px 12px"), opacity: ap, transform: `translateY(${(1 - ap) * 10}px)` }}>
                      <div style={{ display: "flex", alignItems: "center", gap: rp(14, 9) }}>
                        {it.icon ? <Icon name={it.icon} size={rp(52, 34)} mono={it.mono} borderColor={brand} /> : (
                          <div style={{ width: rp(52, 34), height: rp(52, 34), borderRadius: rp(13, 9), background: brand, color: "#fff", fontSize: rp(16, 11), fontWeight: 800, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>{it.txt}</div>
                        )}
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontSize: rp(20, 13), fontWeight: 700, color: C.ink, lineHeight: 1.1 }}>{it.name}</div>
                          <div style={{ fontSize: rp(14, 9.5), fontWeight: 700, color: brand, marginTop: rp(4, 2) }}>{it.tag}</div>
                        </div>
                      </div>
                      <div style={{ fontSize: rp(15, 10.5), color: C.muted, marginTop: rp(10, 7), lineHeight: 1.35 }}>{it.role}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </Stage>
  );
};

/* ---------- OUTRO ---------- */
export const OutroScene: React.FC<{ s: Extract<Scene, { type: "outro" }> }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const lp = pop(frame, fps, 6, 24);
  return (
    <Stage>
      <div style={{ position: "absolute", inset: 0, background: `radial-gradient(circle at 50% 35%, ${C.accent}, ${C.bg} 60%)`, fontFamily: FONT, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: PAD, boxSizing: "border-box", textAlign: "center" }}>
        <div style={{ transform: `scale(${0.85 + 0.15 * lp})`, opacity: lp }}><Logo size={rp(64, 52)} /></div>
        {s.tagline && <div style={{ fontSize: rp(26, 16), color: C.muted, marginTop: rp(36, 22), opacity: lerp(frame, 26, 44, 0, 1), fontWeight: 500, maxWidth: rp(600, 620), lineHeight: 1.35 }}>{s.tagline}</div>}
        <div style={{ marginTop: rp(48, 30), fontSize: rp(30, 20), fontWeight: 800, color: "#fff", background: C.primary, borderRadius: rp(16, 12), padding: rp("20px 44px", "13px 30px"), opacity: lerp(frame, 40, 58, 0, 1), boxShadow: `0 10px 30px ${C.primary}55` }}>{s.url}</div>
      </div>
    </Stage>
  );
};

/* ---------- METRICS (KPIs grandes / dashboard) ---------- */
export const MetricsScene: React.FC<{ s: Extract<Scene, { type: "metrics" }> }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const items = s.items || [];
  const cols = PORTRAIT ? (items.length <= 2 ? 1 : 2) : Math.min(items.length, 4);
  return (
    <Stage>
      <div style={{ position: "absolute", inset: 0, background: `radial-gradient(circle at 50% 0%, ${C.accent}, ${C.bg} 55%)`, fontFamily: FONT, padding: PAD, boxSizing: "border-box", display: "flex", flexDirection: "column", justifyContent: "center" }}>
        {s.heading && <div style={{ fontSize: HEADING, fontWeight: 800, color: C.ink, textAlign: "center" }}>{s.heading}</div>}
        {s.sub && <div style={{ fontSize: SUBHEAD, color: C.muted, marginTop: 4, textAlign: "center" }}>{s.sub}</div>}
        <div style={{ display: "grid", gridTemplateColumns: `repeat(${cols},1fr)`, gap: rp(26, 18), marginTop: rp(56, 36) }}>
          {items.map((m, i) => {
            const p = pop(frame, fps, 10 + i * 7, 22);
            const brand = m.brand || C.primary;
            return (
              <div key={i} style={{ background: C.panel, border: `1px solid ${C.border}`, borderTop: `${rp(6, 4)}px solid ${brand}`, borderRadius: rp(20, 16), padding: rp("34px 24px", "26px 20px"), boxShadow: SHADOW.md, textAlign: "center", opacity: p, transform: `translateY(${(1 - p) * 18}px) scale(${0.94 + 0.06 * p})` }}>
                <div style={{ fontSize: rp(58, 46), fontWeight: 800, color: brand, letterSpacing: -1.5, lineHeight: 1 }}>{m.v}</div>
                <div style={{ fontSize: rp(22, 16), fontWeight: 700, color: C.ink, marginTop: rp(12, 9) }}>{m.label}</div>
                {m.sub && <div style={{ fontSize: rp(16, 12), color: C.muted, marginTop: rp(5, 3) }}>{m.sub}</div>}
              </div>
            );
          })}
        </div>
      </div>
    </Stage>
  );
};

/* ---------- QUOTE (depoimento / frase de impacto) ---------- */
export const QuoteScene: React.FC<{ s: Extract<Scene, { type: "quote" }> }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const qp = pop(frame, fps, 8, 26);
  const ap = lerp(frame, 30, 50, 0, 1);
  const initials = (s.author || "").split(/\s+/).map((w) => w[0]).join("").slice(0, 2).toUpperCase();
  return (
    <Stage>
      <div style={{ position: "absolute", inset: 0, background: `radial-gradient(circle at 50% 30%, ${C.accent}, ${C.bg} 60%)`, fontFamily: FONT, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: PAD, boxSizing: "border-box", textAlign: "center" }}>
        <div style={{ fontSize: rp(120, 96), fontWeight: 800, color: C.primary, opacity: 0.18 * qp, lineHeight: 0.6, marginBottom: rp(8, 6), transform: `scale(${0.8 + 0.2 * qp})` }}>“</div>
        <div style={{ fontSize: rp(36, 30), fontWeight: 700, color: C.ink, lineHeight: 1.35, maxWidth: rp(620, 900), opacity: qp, transform: `translateY(${(1 - qp) * 16}px)` }}>{s.text}</div>
        {(s.author || s.role) && (
          <div style={{ display: "flex", alignItems: "center", gap: rp(16, 12), marginTop: rp(44, 30), opacity: ap, transform: `translateY(${(1 - ap) * 12}px)` }}>
            {s.author && (
              <div style={{ width: rp(64, 48), height: rp(64, 48), borderRadius: "50%", background: `linear-gradient(135deg, ${C.primary}, ${C.gold})`, color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, fontSize: rp(24, 18), flexShrink: 0 }}>{initials || "•"}</div>
            )}
            <div style={{ textAlign: "left" }}>
              {s.author && <div style={{ fontSize: rp(22, 17), fontWeight: 800, color: C.ink }}>{s.author}</div>}
              {s.role && <div style={{ fontSize: rp(16, 13), color: C.muted, marginTop: 2 }}>{s.role}</div>}
            </div>
          </div>
        )}
      </div>
    </Stage>
  );
};

/* ---------- COMPARE (antes/depois · 2 colunas) ---------- */
export const CompareScene: React.FC<{ s: Extract<Scene, { type: "compare" }> }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const toneColor = (t?: string) => (t === "good" ? C.green : t === "bad" ? "#C0392B" : C.muted);
  const col = (data: Extract<Scene, { type: "compare" }>["left"], side: number) => {
    const tc = toneColor(data.tone);
    const items = data.items || [];
    return (
      <div style={{ flex: 1, background: C.panel, border: `1px solid ${C.border}`, borderTop: `${rp(6, 4)}px solid ${tc}`, borderRadius: rp(20, 16), padding: rp("32px 28px", "22px 22px"), boxShadow: SHADOW.md }}>
        <div style={{ fontSize: rp(28, 20), fontWeight: 800, color: tc, marginBottom: rp(20, 14) }}>{data.title}</div>
        <div style={{ display: "flex", flexDirection: "column", gap: rp(16, 11) }}>
          {items.map((it, i) => {
            const p = pop(frame, fps, 10 + side * 6 + i * 6, 18);
            return (
              <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: rp(12, 9), opacity: p, transform: `translateX(${(1 - p) * (side ? 18 : -18)}px)` }}>
                <div style={{ width: rp(24, 18), height: rp(24, 18), borderRadius: "50%", background: tc, color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: rp(15, 12), fontWeight: 800, flexShrink: 0, marginTop: rp(2, 1) }}>{data.tone === "bad" ? "✕" : data.tone === "good" ? "✓" : "•"}</div>
                <div style={{ fontSize: rp(19, 14), color: C.ink2, lineHeight: 1.35 }}>{it}</div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };
  return (
    <Stage>
      <div style={{ position: "absolute", inset: 0, background: C.bg, fontFamily: FONT, padding: PAD, boxSizing: "border-box", display: "flex", flexDirection: "column", justifyContent: "center" }}>
        {s.heading && <div style={{ fontSize: HEADING, fontWeight: 800, color: C.ink, textAlign: "center" }}>{s.heading}</div>}
        {s.sub && <div style={{ fontSize: SUBHEAD, color: C.muted, marginTop: 4, textAlign: "center" }}>{s.sub}</div>}
        <div style={{ display: "flex", flexDirection: PORTRAIT ? "column" : "row", gap: rp(22, 20), marginTop: rp(44, 30), alignItems: "stretch" }}>
          {col(s.left, 0)}
          {col(s.right, 1)}
        </div>
      </div>
    </Stage>
  );
};

/* ---------- CTA (chamada final com botão/URL) ---------- */
export const CtaScene: React.FC<{ s: Extract<Scene, { type: "cta" }> }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const lp = pop(frame, fps, 6, 24);
  const tp = lerp(frame, 24, 42, 0, 1);
  const bp = pop(frame, fps, 40, 22);
  return (
    <Stage>
      <div style={{ position: "absolute", inset: 0, background: `radial-gradient(circle at 50% 40%, ${C.accent}, ${C.bg} 60%), radial-gradient(circle at 85% 95%, ${C.goldSoft}, transparent 50%)`, fontFamily: FONT, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: PAD, boxSizing: "border-box", textAlign: "center" }}>
        <div style={{ fontSize: rp(48, 38), fontWeight: 800, color: C.ink, letterSpacing: -1, lineHeight: 1.15, maxWidth: rp(640, 920), opacity: lp, transform: `translateY(${(1 - lp) * 16}px) scale(${0.92 + 0.08 * lp})` }}>{s.title}</div>
        {s.tagline && <div style={{ fontSize: rp(24, 17), color: C.muted, marginTop: rp(28, 18), opacity: tp, fontWeight: 500, maxWidth: rp(600, 700), lineHeight: 1.4 }}>{s.tagline}</div>}
        <div style={{ marginTop: rp(52, 36), display: "flex", flexDirection: "column", alignItems: "center", gap: rp(16, 12), opacity: bp, transform: `scale(${0.9 + 0.1 * bp})` }}>
          <div style={{ fontSize: rp(28, 20), fontWeight: 800, color: "#fff", background: C.primary, borderRadius: rp(99, 99), padding: rp("22px 56px", "15px 40px"), boxShadow: `0 12px 34px ${C.primary}55` }}>{s.button || "Começar agora"}</div>
          {s.url && <div style={{ fontSize: rp(22, 16), fontWeight: 700, color: C.primary }}>{s.url}</div>}
        </div>
      </div>
    </Stage>
  );
};
