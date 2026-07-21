import { spring, interpolate, Easing } from "remotion";

/** entrada 0→1 com mola */
export const pop = (frame: number, fps: number, delay = 0, dur = 22) =>
  spring({
    frame: frame - delay,
    fps,
    config: { damping: 18, stiffness: 140 },
    durationInFrames: dur,
  });

/** fade/slide linear suave entre [a,b] */
export const lerp = (
  frame: number,
  a: number,
  b: number,
  from: number,
  to: number
) =>
  interpolate(frame, [a, b], [from, to], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

/** contador animado (count-up) */
export const countTo = (
  frame: number,
  target: number,
  delay = 0,
  dur = 26
) => {
  const p = interpolate(frame, [delay, delay + dur], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return target * p;
};
