import React from "react";
import { useVideoConfig } from "remotion";
import { BASE_W, BASE_H, C } from "../theme";

/** Canvas base 1280×720 escalado p/ preencher 1920×1080 (texto nítido). */
export const Stage: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { width } = useVideoConfig();
  const scale = width / BASE_W;
  return (
    <div style={{ position: "absolute", inset: 0, background: C.bg }}>
      <div
        style={{
          position: "absolute",
          width: BASE_W,
          height: BASE_H,
          left: "50%",
          top: "50%",
          transform: `translate(-50%,-50%) scale(${scale})`,
          transformOrigin: "center center",
          overflow: "hidden",
        }}
      >
        {children}
      </div>
    </div>
  );
};
