import React from "react";
import { Composition, registerRoot } from "remotion";
import { ZenCalm, CALM_TOTAL_FRAMES } from "./zen/ZenCalm";
import { CalmCover } from "./zen/CalmCover";
const Root: React.FC = () => (<>
  <Composition id="ZenCalm" component={ZenCalm} durationInFrames={CALM_TOTAL_FRAMES} fps={30} width={540} height={960} defaultProps={{ variant: "xhs" as const }} />
  <Composition id="CalmCover" component={CalmCover} durationInFrames={1} fps={30} width={1080} height={1920} />
</>);
registerRoot(Root);
