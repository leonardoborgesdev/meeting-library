// theme.ts — deriva a paleta da marca (content.brand) + dimensões pelo formato.
import { CONTENT } from "./content";

const b = CONTENT.brand;

export const C = {
  bg: "#F9FBFE",
  bgMuted: "#F2F5F9",
  panel: "#FFFFFF",
  surface3: "#E7ECF0",
  border: "#E6EAEF",
  borderStrong: "#D5DAE0",
  ink: b.ink || "#0B1723",
  ink2: "#2B3540",
  muted: "#555F69",
  dim: "#868D95",
  primary: b.primary || "#2275E8",
  accent: b.accent || "#E2F0FF",
  accentInk: "#0B3D82",
  gold: b.gold || "#DFB127",
  goldSoft: "#FFEDC1",
  goldFg: "#392500",
  green: "#137738",
} as const;

export const FONT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
export const SHADOW = {
  sm: "0 1px 2px rgba(11,23,35,.06)",
  md: "0 4px 8px rgba(11,23,35,.06), 0 8px 24px rgba(11,23,35,.05)",
  lg: "0 12px 32px rgba(11,23,35,.14)",
} as const;

// formato → base canvas (escalado p/ Full HD). Retrato = 9:16.
export const PORTRAIT = CONTENT.format === "9:16";
export const BASE_W = PORTRAIT ? 720 : 1280;
export const BASE_H = PORTRAIT ? 1280 : 720;
export const OUT_W = PORTRAIT ? 1080 : 1920;
export const OUT_H = PORTRAIT ? 1920 : 1080;
