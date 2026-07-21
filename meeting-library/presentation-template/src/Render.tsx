import React from "react";
import { AbsoluteFill, Series, Audio, staticFile } from "remotion";
import { CONTENT } from "./content";
import { DURS, AUDIO } from "./durations";
import { C } from "./theme";
import { IntroScene, ScreensScene, FlowScene, StackScene, OutroScene, MetricsScene, QuoteScene, CompareScene, CtaScene } from "./components/scenes";

const DEFAULT_DUR = 150;
export const sceneDur = (i: number) => (DURS && DURS[i]) || CONTENT.scenes[i].dur || DEFAULT_DUR;
export const TOTAL = CONTENT.scenes.reduce((a, _s, i) => a + sceneDur(i), 0);

const renderScene = (s: typeof CONTENT.scenes[number]) => {
  switch (s.type) {
    case "intro": return <IntroScene s={s} />;
    case "screens": return <ScreensScene s={s} />;
    case "flow": return <FlowScene s={s} />;
    case "stack": return <StackScene s={s} />;
    case "metrics": return <MetricsScene s={s} />;
    case "quote": return <QuoteScene s={s} />;
    case "compare": return <CompareScene s={s} />;
    case "cta": return <CtaScene s={s} />;
    case "outro": return <OutroScene s={s} />;
  }
};

export const Presentation: React.FC = () => (
  <AbsoluteFill style={{ background: C.bg }}>
    {AUDIO && <Audio src={staticFile("audio/narration-final.mp3")} />}
    <Series>
      {CONTENT.scenes.map((s, i) => (
        <Series.Sequence key={i} durationInFrames={sceneDur(i)}>
          {renderScene(s)}
        </Series.Sequence>
      ))}
    </Series>
  </AbsoluteFill>
);
