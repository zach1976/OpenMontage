import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  OffthreadVideo,
  Sequence,
  continueRender,
  delayRender,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// 泰国人生小语：泰语短句大字 + 中文，实拍空镜做底，泰语女声逐句念。
// 第 0 帧就是封面（不做淡入）；封面两行等大、落在核心带 660–1260。

const clamp = {extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const};
const TH = '"SarabunQ", "Sarabun", "Thonburi", sans-serif';
const ZH = '"PingFang SC", "Noto Sans CJK SC", sans-serif';
const ZH_SERIF = '"STKaiti", "Kaiti SC", "Songti SC", serif';

type Item = {thai: string; chinese: string; start: number; end: number; audioAt: number};
type Scene = {src: string; start: number; end: number; srcDur: number};
export type ThaiQuotesProps = {
  episode: string;
  coverT1: string;
  coverT2: string;
  accent: string;
  motion: "rise" | "slide" | "pop" | "focus" | "wipe";
  column: string;
  durationSeconds: number;
  outroStart: number;
  coverHold: number;
  items: Item[];
  narrationSrc: string;
  bgmSrc: string;
  bgmGain: number;
  scenes: Scene[];
  appIconSrc: string;
  brand?: string;      // 泰语千词 / 越南语千词
  country?: string;    // 泰国 / 越南
  fontFile?: string;   // 外语字体（越南语用 Be Vietnam Pro）
};

let fontHandle: number | null = null;
const useThaiFont = (file = "zen/fonts/Sarabun-Bold.ttf") => {
  const [h] = React.useState(() => (fontHandle = delayRender("Sarabun")));
  React.useEffect(() => {
    const f = new FontFace("SarabunQ", `url(${staticFile(file)})`, {weight: "700"});
    f.load().then((ff) => { document.fonts.add(ff); continueRender(h); }).catch(() => continueRender(h));
  }, [h]);
};

const Film: React.FC<{p: ThaiQuotesProps}> = ({p}) => {
  const {fps} = useVideoConfig();
  const XF = 0.6;
  return <>
    {p.scenes.map((s, i) => {
      const from = Math.max(0, Math.round((s.start - (i ? XF : 0)) * fps));
      const len = Math.round((s.end - s.start + (i ? XF : 0)) * fps) + 1;
      const rate = Math.min(1, s.srcDur / (len / fps + 0.2));  // 素材不够长就放慢，不循环
      return <Sequence key={i} from={from} durationInFrames={len}>
        <FilmClip src={s.src} first={i === 0} xf={Math.round(XF * fps)} rate={rate} />
      </Sequence>;
    })}
  </>;
};

const FilmClip: React.FC<{src: string; first: boolean; xf: number; rate: number}> = ({src, first, xf, rate}) => {
  const frame = useCurrentFrame();
  const op = first ? 1 : interpolate(frame, [0, xf], [0, 1], clamp);
  const zoom = interpolate(frame, [0, 600], [1.04, 1.12]);
  return <AbsoluteFill style={{opacity: op}}>
    <OffthreadVideo src={staticFile(src)} muted playbackRate={rate}
      style={{width: "100%", height: "100%", objectFit: "cover", transform: `scale(${zoom})`, filter: "saturate(1.08) contrast(1.04)"}} />
  </AbsoluteFill>;
};

const Shade: React.FC = () => <AbsoluteFill style={{
  background: "linear-gradient(180deg, rgba(0,0,0,.42) 0%, rgba(0,0,0,.08) 26%, rgba(0,0,0,.30) 40%, rgba(0,0,0,.38) 60%, rgba(0,0,0,.10) 76%, rgba(0,0,0,.45) 100%)",
}} />;

const Brand: React.FC<{p: ThaiQuotesProps; big?: boolean}> = ({p}) => (
  <div style={{position: "absolute", top: 268, left: 0, right: 0, display: "flex", justifyContent: "center", alignItems: "center", gap: 18}}>
    <Img src={staticFile(p.appIconSrc)} style={{width: 54, height: 54, borderRadius: 14, boxShadow: "0 4px 16px rgba(0,0,0,.35)"}} />
    <div style={{fontFamily: ZH, fontSize: 34, fontWeight: 900, color: "#FFF", letterSpacing: 4, textShadow: "0 2px 12px rgba(0,0,0,.6)"}}>
      {p.brand ?? "泰语千词"} <span style={{color: p.accent}}>·</span> {p.column}
    </div>
  </div>
);

const stroke = (c: string, w: number) =>
  [[-1, -1], [1, -1], [-1, 1], [1, 1], [0, -1.3], [0, 1.3], [-1.3, 0], [1.3, 0]]
    .map(([x, y]) => `${x * w}px ${y * w}px 0 ${c}`).join(", ");

const Cover: React.FC<{p: ThaiQuotesProps}> = ({p}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const out = interpolate(frame, [p.coverHold * fps - 8, p.coverHold * fps], [1, 0], clamp);
  const n = Math.max(p.coverT1.length, p.coverT2.length);
  const size = Math.min(150, Math.floor(900 / n));
  const line = (t: string, c = "#FFF") => <div style={{fontFamily: ZH, fontWeight: 900, fontSize: size, lineHeight: 1.18, color: c,
    textShadow: `${stroke("rgba(0,0,0,.55)", 4)}, 0 10px 40px rgba(0,0,0,.5)`, whiteSpace: "nowrap"}}>{t}</div>;
  return <AbsoluteFill style={{opacity: out}}>
    <div style={{position: "absolute", top: 660, height: 600, left: 0, right: 0, display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center", gap: 22}}>
      {line(p.coverT1)}
      <div style={{width: 360, height: 10, borderRadius: 5, background: p.accent, boxShadow: `0 0 24px ${p.accent}`}} />
      {line(p.coverT2, p.accent)}
    </div>
  </AbsoluteFill>;
};

const Line: React.FC<{p: ThaiQuotesProps; it: Item}> = ({p, it}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const len = (it.end - it.start) * fps;
  const s = spring({frame, fps, config: {damping: 16, stiffness: 140}});
  const s2 = spring({frame: frame - 5, fps, config: {damping: 18, stiffness: 120}});
  const outOp = interpolate(frame, [len - 6, len], [1, 0], clamp);
  const thLen = it.thai.length;
  const thSize = Math.min(118, Math.floor(1700 / Math.max(thLen, 8)));
  // 每集一种入场动效（版式不变，动效换）
  const m = p.motion;
  const thStyle: React.CSSProperties =
    m === "rise" ? {transform: `translateY(${(1 - s) * 60}px)`, opacity: s} :
    m === "slide" ? {transform: `translateX(${(1 - s) * -120}px)`, opacity: s} :
    m === "pop" ? {transform: `scale(${0.6 + 0.4 * s})`, opacity: Math.min(1, s * 1.5)} :
    m === "focus" ? {filter: `blur(${(1 - s) * 18}px)`, opacity: s, transform: `scale(${1.15 - 0.15 * s})`} :
    {clipPath: `inset(0 ${(1 - s) * 100}% 0 0)`};
  const barW = interpolate(s2, [0, 1], [0, 1]);
  return <AbsoluteFill style={{opacity: outOp}}>
    <div style={{position: "absolute", top: 700, left: 40, right: 40, height: 520, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center"}}>
      <div style={{fontFamily: TH, fontWeight: 700, fontSize: thSize, lineHeight: 1.45, color: "#FFF", whiteSpace: "nowrap",
        textShadow: `${stroke("rgba(10,20,10,.75)", 5)}, 0 8px 30px rgba(0,0,0,.55)`, ...thStyle}}>{it.thai}</div>
      <div style={{width: 520, height: 8, marginTop: 6, borderRadius: 4, background: `linear-gradient(90deg, transparent, ${p.accent}, transparent)`,
        transform: `scaleX(${barW})`}} />
      <div style={{fontFamily: ZH, fontWeight: 800, fontSize: 60, color: p.accent, marginTop: 34, letterSpacing: 3, whiteSpace: "nowrap",
        textShadow: `${stroke("rgba(0,0,0,.6)", 3)}, 0 6px 24px rgba(0,0,0,.5)`, opacity: s2, transform: `translateY(${(1 - s2) * 24}px)`}}>{it.chinese}</div>
    </div>
  </AbsoluteFill>;
};

const Outro: React.FC<{p: ThaiQuotesProps}> = ({p}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const e = spring({frame, fps, config: {damping: 18, stiffness: 110}});
  return <AbsoluteFill style={{background: `rgba(6,12,16,${0.5 * e})`}}>
    <div style={{position: "absolute", top: 640, left: 0, right: 0, textAlign: "center", opacity: e, transform: `translateY(${(1 - e) * 40}px)`}}>
      <Img src={staticFile(p.appIconSrc)} style={{width: 230, height: 230, borderRadius: 54, boxShadow: `0 24px 70px rgba(0,0,0,.45), 0 0 0 4px ${p.accent}88`}} />
      <div style={{fontFamily: ZH_SERIF, fontSize: 96, color: p.accent, letterSpacing: 8, marginTop: 50, textShadow: "0 6px 26px rgba(0,0,0,.5)"}}>{p.brand ?? "泰语千词"}</div>
      <div style={{fontFamily: ZH, fontSize: 44, fontWeight: 800, color: "#FFF", marginTop: 24, letterSpacing: 2, textShadow: "0 4px 18px rgba(0,0,0,.6)"}}>在{p.country ?? "泰国"}生活，够用了</div>
    </div>
  </AbsoluteFill>;
};

export const ThaiQuotes: React.FC<ThaiQuotesProps> = (p) => {
  useThaiFont(p.fontFile);
  const {fps} = useVideoConfig();
  const f = (t: number) => Math.round(t * fps);
  return <AbsoluteFill style={{background: "#0B1418"}}>
    <Film p={p} />
    <Shade />
    <Brand p={p} />
    <Cover p={p} />
    {p.items.map((it, i) => <Sequence key={i} from={f(it.start)} durationInFrames={f(it.end) - f(it.start)}><Line p={p} it={it} /></Sequence>)}
    <Sequence from={f(p.outroStart)}><Outro p={p} /></Sequence>
    <Audio src={staticFile(p.narrationSrc)} />
    <Audio src={staticFile(p.bgmSrc)} volume={(fr) => p.bgmGain * interpolate(fr, [f(p.durationSeconds) - 30, f(p.durationSeconds)], [1, 0], clamp)} />
  </AbsoluteFill>;
};
