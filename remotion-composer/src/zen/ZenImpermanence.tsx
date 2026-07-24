import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  continueRender,
  delayRender,
} from "remotion";

// ---------------------------------------------------------------------------
// Fonts (local, bundled in public/zen/fonts)
// ---------------------------------------------------------------------------
const handle = delayRender("zen-fonts");
Promise.all([
  new FontFace(
    "SarabunBold",
    `url(${staticFile("zen/fonts/Sarabun-Bold.ttf")})`
  ).load(),
  new FontFace(
    "SarabunRegular",
    `url(${staticFile("zen/fonts/Sarabun-Regular.ttf")})`
  ).load(),
  new FontFace(
    "NotoSerifSCBold",
    `url(${staticFile("zen/fonts/NotoSerifSC-Bold.otf")})`
  ).load(),
])
  .then((fonts) => {
    fonts.forEach((f) => (document.fonts as FontFaceSet).add(f));
    continueRender(handle);
  })
  .catch(() => continueRender(handle));

const THAI = "SarabunBold, sans-serif";
const THAI_R = "SarabunRegular, sans-serif";
const ZH = "NotoSerifSCBold, serif";
const GOLD = "#E4C06B";
const CREAM = "#F3ECDD";

// ---------------------------------------------------------------------------
// Procedural zen background — soft drifting light over an ink gradient.
// No stock footage; every pixel is generated in-engine.
// ---------------------------------------------------------------------------
const ZenBackground: React.FC<{ warmth: number }> = ({ warmth }) => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  // slow drifting glow centers
  const g1x = 50 + Math.sin(t * 0.18) * 22;
  const g1y = 34 + Math.cos(t * 0.14) * 14;
  const g2x = 40 + Math.cos(t * 0.11) * 26;
  const g2y = 70 + Math.sin(t * 0.16) * 12;
  // warmth 0..1 pushes the palette from cool ink toward warm dusk
  const base1 = `hsl(${205 - warmth * 24}, 34%, ${8 + warmth * 3}%)`;
  const base2 = `hsl(${180 - warmth * 30}, 22%, ${11 + warmth * 4}%)`;
  const goldA = 0.1 + warmth * 0.16;
  return (
    <AbsoluteFill>
      <AbsoluteFill
        style={{
          background: `linear-gradient(160deg, ${base1} 0%, ${base2} 100%)`,
        }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(60% 42% at ${g1x}% ${g1y}%, rgba(228,192,107,${goldA}) 0%, rgba(228,192,107,0) 70%)`,
        }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(58% 46% at ${g2x}% ${g2y}%, rgba(120,168,190,0.16) 0%, rgba(120,168,190,0) 68%)`,
        }}
      />
      {/* vignette */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(120% 78% at 50% 42%, rgba(0,0,0,0) 40%, rgba(0,0,0,0.55) 100%)",
        }}
      />
      {/* faint grain */}
      <AbsoluteFill
        style={{
          opacity: 0.05,
          mixBlendMode: "overlay",
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")",
          backgroundSize: "180px 180px",
        }}
      />
    </AbsoluteFill>
  );
};

// fade helper: fades in over `inF` and out over last `outF` frames of a window
const useFade = (from: number, dur: number, inF = 16, outF = 16) => {
  const frame = useCurrentFrame();
  const local = frame - from;
  return interpolate(
    local,
    [0, inF, dur - outF, dur],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
};

const SeriesTag: React.FC = () => (
  <div
    style={{
      position: "absolute",
      top: 70,
      left: 44,
      fontFamily: ZH,
      fontSize: 22,
      letterSpacing: 3,
      color: "rgba(243,236,221,0.62)",
    }}
  >
    泰语千词 · 每天一句
  </div>
);

// -- Section 1: Hook -------------------------------------------------------
const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const op = useFade(0, 100, 22, 18);
  const rise = interpolate(frame, [0, 40], [26, 0], {
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill
      style={{ justifyContent: "center", alignItems: "center", opacity: op }}
    >
      <div
        style={{
          fontFamily: ZH,
          fontSize: 52,
          lineHeight: 1.5,
          color: CREAM,
          textAlign: "center",
          transform: `translateY(${rise}px)`,
          textShadow: "0 2px 24px rgba(0,0,0,0.5)",
          maxWidth: 420,
        }}
      >
        有什么，
        <br />
        是永远不会改变的？
      </div>
    </AbsoluteFill>
  );
};

// -- Section 2: Reflection (Thai zen line + 中文) --------------------------
const Reflection: React.FC = () => {
  const frame = useCurrentFrame();
  const op = useFade(0, 220, 26, 22);
  const rise = interpolate(frame, [0, 50], [30, 0], {
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill
      style={{ justifyContent: "center", alignItems: "center", opacity: op }}
    >
      <div
        style={{
          transform: `translateY(${rise}px)`,
          textAlign: "center",
          padding: "0 60px",
        }}
      >
        <div
          style={{
            fontFamily: THAI,
            fontSize: 58,
            lineHeight: 1.4,
            color: CREAM,
            textShadow: "0 2px 26px rgba(0,0,0,0.55)",
          }}
        >
          ไม่มีอะไร
          <br />
          อยู่กับเราได้ตลอดไป
        </div>
        <div
          style={{
            marginTop: 34,
            fontFamily: ZH,
            fontSize: 30,
            letterSpacing: 2,
            color: "rgba(243,236,221,0.72)",
          }}
        >
          没有什么能永远陪着我们
        </div>
      </div>
    </AbsoluteFill>
  );
};

// -- Section 3: Vocabulary -------------------------------------------------
const Vocab: React.FC = () => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const op = useFade(0, 100, 16, 16);
  const s = spring({ frame, fps, config: { damping: 16, stiffness: 90 } });
  const scale = interpolate(s, [0, 1], [0.9, 1]);
  return (
    <AbsoluteFill
      style={{ justifyContent: "center", alignItems: "center", opacity: op }}
    >
      <div style={{ textAlign: "center", transform: `scale(${scale})` }}>
        <div style={{ fontFamily: THAI, fontSize: 96, color: GOLD }}>
          เปลี่ยน
        </div>
        <div
          style={{
            fontFamily: THAI_R,
            fontSize: 30,
            color: "rgba(243,236,221,0.6)",
            marginTop: 6,
            letterSpacing: 2,
          }}
        >
          plìan
        </div>
        <div
          style={{
            width: 60,
            height: 2,
            background: GOLD,
            opacity: 0.5,
            margin: "22px auto",
          }}
        />
        <div style={{ fontFamily: ZH, fontSize: 46, color: CREAM }}>改变</div>
      </div>
    </AbsoluteFill>
  );
};

// -- Section 4: App demo ---------------------------------------------------
const AppDemo: React.FC = () => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const op = useFade(0, 90, 14, 14);
  const s = spring({ frame, fps, config: { damping: 18, stiffness: 80 } });
  const scale = interpolate(s, [0, 1], [0.86, 1]);
  const pulse = 0.5 + 0.5 * Math.sin(frame / 6);
  return (
    <AbsoluteFill
      style={{ justifyContent: "center", alignItems: "center", opacity: op }}
    >
      <div
        style={{
          position: "relative",
          transform: `scale(${scale})`,
          borderRadius: 34,
          overflow: "hidden",
          boxShadow: "0 24px 70px rgba(0,0,0,0.55)",
          border: "1px solid rgba(228,192,107,0.25)",
        }}
      >
        <Img
          src={staticFile("zen/app/word_detail.png")}
          style={{ width: 360, display: "block" }}
        />
        {/* gold focus ring hinting the tap-to-play area */}
        <div
          style={{
            position: "absolute",
            top: "34%",
            left: "50%",
            width: 120,
            height: 120,
            marginLeft: -60,
            borderRadius: "50%",
            border: `2px solid rgba(228,192,107,${0.35 + pulse * 0.4})`,
            boxShadow: `0 0 ${18 + pulse * 22}px rgba(228,192,107,${
              0.2 + pulse * 0.25
            })`,
          }}
        />
      </div>
      <div
        style={{
          marginTop: 30,
          fontFamily: ZH,
          fontSize: 26,
          color: "rgba(243,236,221,0.7)",
        }}
      >
        在「泰语千词」里点一下，就会读
      </div>
    </AbsoluteFill>
  );
};

// -- Section 5: CTA --------------------------------------------------------
const CTA: React.FC = () => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const op = useFade(0, 60, 16, 8);
  const s = spring({ frame, fps, config: { damping: 20, stiffness: 90 } });
  const scale = interpolate(s, [0, 1], [0.8, 1]);
  return (
    <AbsoluteFill
      style={{ justifyContent: "center", alignItems: "center", opacity: op }}
    >
      <div style={{ textAlign: "center" }}>
        <Img
          src={staticFile("zen/app/app_icon.png")}
          style={{
            width: 132,
            height: 132,
            borderRadius: 30,
            transform: `scale(${scale})`,
            boxShadow: "0 14px 40px rgba(0,0,0,0.5)",
          }}
        />
        <div
          style={{
            marginTop: 26,
            fontFamily: ZH,
            fontSize: 44,
            color: GOLD,
            letterSpacing: 2,
          }}
        >
          泰语千词
        </div>
        <div
          style={{
            marginTop: 12,
            fontFamily: ZH,
            fontSize: 26,
            color: "rgba(243,236,221,0.75)",
          }}
        >
          每天学一点自然泰语
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
export const ZenImpermanence: React.FC = () => {
  // warmth ramps across the piece for a gentle emotional arc
  const frame = useCurrentFrame();
  const warmth = interpolate(frame, [0, 320, 400, 510], [0, 0.5, 0.9, 0.7], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ backgroundColor: "#0a1420" }}>
      <ZenBackground warmth={warmth} />
      <SeriesTag />

      <Sequence from={0} durationInFrames={100} name="hook">
        <Hook />
      </Sequence>
      <Sequence from={96} durationInFrames={224} name="reflection">
        <Reflection />
      </Sequence>
      <Sequence from={320} durationInFrames={104} name="vocab">
        <Vocab />
      </Sequence>
      <Sequence from={420} durationInFrames={92} name="app">
        <AppDemo />
      </Sequence>
      <Sequence from={508} durationInFrames={62} name="cta">
        <CTA />
      </Sequence>

      {/* Voiceover */}
      <Sequence from={120} name="vo-line1">
        <Audio src={staticFile("zen/audio/vo_line1.mp3")} volume={0.95} />
      </Sequence>
      <Sequence from={340} name="vo-word">
        <Audio src={staticFile("zen/audio/vo_word_plian.mp3")} volume={0.95} />
      </Sequence>
    </AbsoluteFill>
  );
};
