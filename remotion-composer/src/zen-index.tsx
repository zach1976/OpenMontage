import React from "react";
import { Composition, registerRoot } from "remotion";
import { ZenImpermanence } from "./zen/ZenImpermanence";
import {
  ZenImpermanenceFull,
  ZEN_TOTAL_FRAMES,
} from "./zen/ZenImpermanenceFull";
import { ZenCover } from "./zen/ZenCover";
import { ZenProverbFriends, PROVERB_TOTAL_FRAMES } from "./zen/ZenProverbFriends";

const ZenRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ZenImpermanence"
        component={ZenImpermanence}
        durationInFrames={570}
        fps={30}
        width={540}
        height={960}
      />
      <Composition
        id="ZenImpermanenceXHS"
        component={ZenImpermanenceFull}
        durationInFrames={ZEN_TOTAL_FRAMES}
        fps={30}
        width={540}
        height={960}
        defaultProps={{ variant: "xhs" as const }}
      />
      <Composition
        id="ZenImpermanenceOverseas"
        component={ZenImpermanenceFull}
        durationInFrames={ZEN_TOTAL_FRAMES}
        fps={30}
        width={540}
        height={960}
        defaultProps={{ variant: "overseas" as const }}
      />
      <Composition
        id="ZenProverbFriends"
        component={ZenProverbFriends}
        durationInFrames={PROVERB_TOTAL_FRAMES}
        fps={30}
        width={540}
        height={960}
        defaultProps={{ variant: "xhs" as const }}
      />
      <Composition
        id="ZenCover"
        component={ZenCover}
        durationInFrames={1}
        fps={30}
        width={1080}
        height={1920}
      />
    </>
  );
};

registerRoot(ZenRoot);
