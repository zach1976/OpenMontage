import React from "react";
import { Composition, registerRoot } from "remotion";
import { ZenBeginAgainFresh, FRESH_TOTAL_FRAMES } from "./zen/ZenBeginAgainFresh";
registerRoot(() => (
  <Composition id="ZenBeginAgainFresh" component={ZenBeginAgainFresh} durationInFrames={FRESH_TOTAL_FRAMES}
    fps={30} width={540} height={960} defaultProps={{ variant: "xhs" as const }} />
));
