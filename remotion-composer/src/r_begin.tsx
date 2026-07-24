import React from "react";
import { Composition, registerRoot } from "remotion";
import { ZenBeginAgain, BEGIN_TOTAL_FRAMES } from "./zen/ZenBeginAgain";
registerRoot(() => (<Composition id="ZenBeginAgain" component={ZenBeginAgain} durationInFrames={BEGIN_TOTAL_FRAMES} fps={30} width={540} height={960} defaultProps={{ variant: "xhs" as const }} />));
