import React from "react";
import { Composition, registerRoot } from "remotion";
import { ZenLettingGo, LETTINGGO_TOTAL_FRAMES } from "./zen/ZenLettingGo";
registerRoot(() => (<Composition id="ZenLettingGo" component={ZenLettingGo} durationInFrames={LETTINGGO_TOTAL_FRAMES} fps={30} width={540} height={960} defaultProps={{ variant: "xhs" as const }} />));
