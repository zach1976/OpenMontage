import React from "react";
import { Composition, registerRoot } from "remotion";
import { ZenCalm, CALM_TOTAL_FRAMES } from "./zen/ZenCalm";
registerRoot(() => (<Composition id="ZenCalm" component={ZenCalm} durationInFrames={CALM_TOTAL_FRAMES} fps={30} width={540} height={960} defaultProps={{ variant: "xhs" as const }} />));
