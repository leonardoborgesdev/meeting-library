import { Composition, registerRoot } from "remotion";
import { loadFont } from "@remotion/google-fonts/Inter";
import { Presentation, TOTAL } from "./Render";
import { OUT_W, OUT_H } from "./theme";

loadFont();

export const Root: React.FC = () => (
  <Composition
    id="Presentation"
    component={Presentation}
    durationInFrames={Math.max(1, TOTAL)}
    fps={30}
    width={OUT_W}
    height={OUT_H}
  />
);

registerRoot(Root);
