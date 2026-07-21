import React from "react";
import { Img, staticFile } from "remotion";
import { C } from "../theme";

/** Ícone (logo SVG) sobre tile branco com borda — padrão de visibilidade da skill.
 *  openai/twilio são mono (pretos); recebem tint escuro. Demais já vêm coloridos. */
export const Icon: React.FC<{
  name: string;
  size?: number;
  borderColor?: string;
  mono?: boolean;
}> = ({ name, size = 52, borderColor = C.border, mono }) => (
  <div
    style={{
      width: size,
      height: size,
      borderRadius: size * 0.26,
      background: "#fff",
      border: `1.5px solid ${borderColor}`,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      boxShadow: "0 4px 14px rgba(11,31,26,.07)",
      flexShrink: 0,
    }}
  >
    {/* preload hidden (gotcha SVG headless) */}
    <Img src={staticFile(`icons/${name}.svg`)} style={{ position: "absolute", width: 1, height: 1, opacity: 0 }} />
    <Img
      src={staticFile(`icons/${name}.svg`)}
      style={{
        width: size * 0.56,
        height: size * 0.56,
        objectFit: "contain",
        filter: mono ? "brightness(0.15)" : "none",
      }}
    />
  </div>
);
