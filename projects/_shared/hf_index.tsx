import React from "react";
import { Composition, registerRoot } from "remotion";
import { HF, Props } from "./HF";

// props 走 --props 传进来；atelier 暂存只拷源码，import props.json 会把 webpack 打挂
const placeholder: Props = {
  fps: 30, word: { th: "", rom: "", zh: "", xie: "" },
  palette: { ink: "#0A1613", ink2: "#12241E", accent: "#E8B65C" },
  badge: "", poster: { t1: "", t2: "" },
  hook: { start: 0, dur: 1, audio: [] }, pages: [],
  outro: { start: 0, dur: 1, audio: "", audioAt: 0 },
  bgm: { src: "", gain: 0 }, speak: [],
};

registerRoot(() => (
  <Composition id="HF" component={HF as any}
    fps={30} width={1080} height={1920} durationInFrames={30}
    defaultProps={placeholder as any}
    calculateMetadata={({ props }: any) => ({
      durationInFrames: props.totalFrames || 30, fps: props.fps || 30, width: 1080, height: 1920,
    })}
  />
));
