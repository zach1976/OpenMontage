import React from "react";
import { Composition, registerRoot } from "remotion";
import { ZenImpermanenceFull, ZEN_TOTAL_FRAMES } from "./zen/ZenImpermanenceFull";
registerRoot(() => (<Composition id="ZenImpermanenceFull" component={ZenImpermanenceFull} durationInFrames={ZEN_TOTAL_FRAMES} fps={30} width={540} height={960} defaultProps={{ variant: "xhs" as const }} />));
