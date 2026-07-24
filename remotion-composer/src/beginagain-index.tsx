import React from "react";
import { Composition, registerRoot } from "remotion";
import { ZenBeginAgain, BEGIN_TOTAL_FRAMES } from "./zen/ZenBeginAgain";
import { BeginAgainCover } from "./zen/BeginAgainCover";
registerRoot(() => (<>
  <Composition id="ZenBeginAgain" component={ZenBeginAgain} durationInFrames={BEGIN_TOTAL_FRAMES} fps={30} width={540} height={960} defaultProps={{ variant: "xhs" as const }} />
  <Composition id="BeginAgainCover" component={BeginAgainCover} durationInFrames={1} fps={30} width={1080} height={1920} />
</>));
