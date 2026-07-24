import React from "react";
import { Composition, registerRoot } from "remotion";
import { ZenProverbFriends, PROVERB_TOTAL_FRAMES } from "./zen/ZenProverbFriends";
import { ProverbCover } from "./zen/ProverbCover";

const Root: React.FC = () => (
  <>
    <Composition
      id="ZenProverbFriends"
      component={ZenProverbFriends}
      durationInFrames={PROVERB_TOTAL_FRAMES}
      fps={30}
      width={540}
      height={960}
      defaultProps={{ variant: "xhs" as const }}
    />
    <Composition id="ProverbCover" component={ProverbCover} durationInFrames={1} fps={30} width={1080} height={1920} />
  </>
);
registerRoot(Root);
