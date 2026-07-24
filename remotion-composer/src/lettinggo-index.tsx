import React from "react";
import { Composition, registerRoot } from "remotion";
import { ZenLettingGo, LETTINGGO_TOTAL_FRAMES } from "./zen/ZenLettingGo";
import { LettingGoCover } from "./zen/LettingGoCover";
const Root: React.FC = () => (
  <>
    <Composition id="ZenLettingGo" component={ZenLettingGo} durationInFrames={LETTINGGO_TOTAL_FRAMES}
      fps={30} width={540} height={960} defaultProps={{ variant: "xhs" as const }} />
    <Composition id="LettingGoCover" component={LettingGoCover} durationInFrames={1} fps={30} width={1080} height={1920} />
  </>
);
registerRoot(Root);
