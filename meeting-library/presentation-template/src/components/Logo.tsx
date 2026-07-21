import React from "react";
import { C, FONT } from "../theme";
import { CONTENT } from "../content";

export const Logo: React.FC<{ size?: number; sub?: string }> = ({ size = 26, sub }) => (
  <div style={{ display: "flex", alignItems: "center", gap: size * 0.34, fontFamily: FONT }}>
    <div
      style={{
        width: size, height: size, borderRadius: size * 0.28,
        background: `linear-gradient(135deg, ${C.primary}, ${C.gold})`,
        display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0,
        boxShadow: `0 4px 12px ${C.primary}44`,
      }}
    >
      <div style={{ width: 0, height: 0, borderTop: `${size * 0.2}px solid transparent`, borderBottom: `${size * 0.2}px solid transparent`, borderLeft: `${size * 0.3}px solid #fff`, marginLeft: size * 0.07 }} />
    </div>
    <div style={{ lineHeight: 1 }}>
      <div style={{ fontSize: size * 0.62, fontWeight: 800, color: C.ink, letterSpacing: -0.4 }}>{CONTENT.brand.name}</div>
      {sub && <div style={{ fontSize: size * 0.32, fontWeight: 500, color: C.dim, marginTop: size * 0.12 }}>{sub}</div>}
    </div>
  </div>
);
