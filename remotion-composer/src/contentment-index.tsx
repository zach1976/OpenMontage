import React from "react";
import { Composition, registerRoot } from "remotion";
import { ZenContentment, CONTENT_TOTAL_FRAMES } from "./zen/ZenContentment";
import { ContentmentCover } from "./zen/ContentmentCover";
registerRoot(() => (<>
  <Composition id="ZenContentment" component={ZenContentment} durationInFrames={CONTENT_TOTAL_FRAMES} fps={30} width={540} height={960} defaultProps={{ variant: "xhs" as const }} />
  <Composition id="ContentmentCover" component={ContentmentCover} durationInFrames={1} fps={30} width={1080} height={1920} />
</>));
