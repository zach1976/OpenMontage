import React from "react";
import { Composition, registerRoot } from "remotion";
import { ZenProverbFriends, PROVERB_TOTAL_FRAMES } from "./zen/ZenProverbFriends";
registerRoot(() => (<Composition id="ZenProverbFriends" component={ZenProverbFriends} durationInFrames={PROVERB_TOTAL_FRAMES} fps={30} width={540} height={960} defaultProps={{ variant: "xhs" as const }} />));
