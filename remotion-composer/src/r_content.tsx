import React from "react";
import { Composition, registerRoot } from "remotion";
import { ZenContentment, CONTENT_TOTAL_FRAMES } from "./zen/ZenContentment";
registerRoot(() => (<Composition id="ZenContentment" component={ZenContentment} durationInFrames={CONTENT_TOTAL_FRAMES} fps={30} width={540} height={960} defaultProps={{ variant: "xhs" as const }} />));
