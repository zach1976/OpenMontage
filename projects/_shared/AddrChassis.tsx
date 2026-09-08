import React from "react";
import { AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Palette, LACQUER_GOLD, PosterBg, Petals, Landscape, CornerFrets, PosterBrand, PosterTitle } from "./Poster";
import { ZH, ZH_S, VietOutro } from "./VietBase";

// ---------------------------------------------------------------------------
// 越南称呼系列 —— 共用的**引擎知识**：底色、品牌行、封面壳、反转卡、片尾、时间轴装配。
// 每一集自己写的是 Device（装置）、配色和词卡版式 —— 那是创意，绝不共用。
// 见 CLAUDE.md「同一系列每集必须换视觉语言」与 AGENT_GUIDE 的 atelier 原则。
// ---------------------------------------------------------------------------

export type Skin = {
  deep: string; mid: string; light: string;   // 底色三档
  accent: string; accentSoft: string;         // 这一集唯一的强色
  paper: string; paperDim: string;            // 字色
  onAccent: string;                           // 压在强色上的字
  posterGlow: string; posterStroke: string; plaqueInk: string;
  layout: "center" | "stack" | "left" | "split" | "frame" | "band";
};

export type CardSpec = {
  id: string; order: number; start: number; dur: number;
  vi: string; xie: string; zh: string; note: string;
  viAudio: string; zhAudio: string; viAt: number; vi2At: number; zhAt: number;
};

export type Props = {
  fps: number; totalFrames: number; totalSeconds: number;
  hook: { start: number; dur: number; audio: string; audioAt: number; poster: any; badge: string };
  cards: CardSpec[];
  reveal: { start: number; dur: number; audio: string; audioAt: number;
            line1: string; line2: string; rule: string; beats: string[] };
  outro: { start: number; dur: number; audio: string; audioAt: number;
           line1: string; line2: string; cta: string; tags: string[] };
  bgm: { file: string; volume: number };
  speak: number[][];
};

export const Backdrop: React.FC<{ s: Skin }> = ({ s }) => (
  <AbsoluteFill style={{ backgroundColor: s.deep }}>
    <AbsoluteFill style={{ background: `radial-gradient(120% 64% at 50% 43%, ${s.light} 0%, ${s.mid} 54%, ${s.deep} 100%)` }} />
    <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 6, background: s.accent }} />
    <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 6, background: s.accent }} />
  </AbsoluteFill>
);

export const Brand: React.FC<{ s: Skin; label?: string }> = ({ s, label }) => (
  <>
    <div style={{ position: "absolute", top: 128, width: "100%", textAlign: "center",
                  fontFamily: ZH_S, fontSize: 26, letterSpacing: 2, color: s.paperDim }}>
      越南语千词 app · 在越南生活够用了
    </div>
    {label ? (
      <div style={{ position: "absolute", top: 194, width: "100%", textAlign: "center",
                    fontFamily: ZH_S, fontSize: 38, letterSpacing: 8, color: s.accentSoft }}>
        {label}
      </div>
    ) : null}
  </>
);

/** 封面 = 全片第一帧，frame 0 即成品；核心带 660–1260 里只有一句话，两行等大 */
export const Cover: React.FC<{ s: Skin; badge: string; poster: any; audio?: string; audioAt?: number }> =
  ({ s, badge, poster, audio, audioAt }) => {
    const frame = useCurrentFrame();
    const { fps, durationInFrames } = useVideoConfig();
    const fadeOut = interpolate(frame, [durationInFrames - 8, durationInFrames], [1, 0],
                                { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const P: Palette = { ...LACQUER_GOLD, deep: s.deep, mid: s.mid, glow: s.posterGlow,
                         stroke: s.posterStroke, plaqueFill: s.paper, plaqueInk: s.plaqueInk };
    return (
      <AbsoluteFill style={{ opacity: fadeOut }}>
        <PosterBg p={P} variant="night" sun={["50%", "28%"]} />
        <Landscape p={P} top={1460} />
        <CornerFrets p={P} />
        <Petals p={P} />
        <PosterBrand p={P} zh={ZH} brand="越南语千词 app · 在越南生活够用了" badge={badge} />
        <PosterTitle p={P} zh={ZH} t1={poster?.t1} t2={poster?.t2} layout={s.layout} />
        {audio ? (
          <Sequence from={Math.round((audioAt ?? 0) * fps)}><Audio src={staticFile(audio)} /></Sequence>
        ) : null}
      </AbsoluteFill>
    );
  };

export const Reveal: React.FC<{ s: Skin; reveal: Props["reveal"] }> = ({ s, reveal }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const at = (d: number) =>
    interpolate(frame, [d, d + 16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [durationInFrames - 8, durationInFrames], [1, 0],
                              { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ opacity: fadeOut }}>
      <Brand s={s} />
      <div style={{ position: "absolute", top: 300, width: "100%", textAlign: "center",
                    fontFamily: ZH, fontSize: 46, color: s.paperDim, opacity: at(4) }}>
        {reveal.line1}
      </div>
      <div style={{ position: "absolute", top: 374, width: "100%", textAlign: "center",
                    fontFamily: ZH, fontSize: 92, lineHeight: 1.25, color: s.accentSoft, opacity: at(12) }}>
        {reveal.line2}
      </div>
      {reveal.beats.map((b, i) => (
        <div key={i} style={{ position: "absolute", top: 590 + i * 150, left: 110, width: 860,
                              backgroundColor: s.light, borderLeft: `10px solid ${s.accent}`,
                              padding: "22px 28px", fontFamily: ZH_S, fontSize: 36, lineHeight: 1.5,
                              color: s.paper, whiteSpace: "pre-line", opacity: at(38 + i * 78),
                              transform: `translateY(${interpolate(at(38 + i * 78), [0, 1], [16, 0])}px)` }}>
          {b}
        </div>
      ))}
      <div style={{ position: "absolute", top: 1090, width: "100%", display: "flex",
                    justifyContent: "center", opacity: at(300) }}>
        <div style={{ backgroundColor: s.accent, color: s.onAccent, fontFamily: ZH, fontSize: 62,
                      padding: "16px 44px", letterSpacing: 3, boxShadow: "0 14px 34px rgba(0,0,0,0.45)" }}>
          {reveal.rule}
        </div>
      </div>
      <Sequence from={Math.round(reveal.audioAt * fps)}><Audio src={staticFile(reveal.audio)} /></Sequence>
    </AbsoluteFill>
  );
};

/** 时间轴装配：各集只把自己的 Card 组件传进来 */
export const Film: React.FC<Props & { s: Skin; label: string;
  Card: React.FC<{ card: CardSpec; s: Skin; label: string }> }> =
  ({ hook, cards, reveal, outro, bgm, speak, fps, s, label, Card }) => {
    const f = (x: number) => Math.round(x * fps);
    const duck = (frame: number) => {
      const t = frame / fps;
      return speak.some(([a, b]) => t >= a - 0.15 && t <= b + 0.2) ? bgm.volume * 0.6 : bgm.volume;
    };
    return (
      <AbsoluteFill>
        <Backdrop s={s} />
        <Audio src={staticFile(bgm.file)} volume={duck} />
        <Sequence from={f(hook.start)} durationInFrames={f(hook.dur)}>
          <Cover s={s} badge={hook.badge} poster={hook.poster} audio={hook.audio} audioAt={hook.audioAt} />
        </Sequence>
        {cards.map((c) => (
          <Sequence key={c.id} from={f(c.start)} durationInFrames={f(c.dur)}>
            <Card card={c} s={s} label={label} />
          </Sequence>
        ))}
        <Sequence from={f(reveal.start)} durationInFrames={f(reveal.dur)}>
          <Reveal s={s} reveal={reveal} />
        </Sequence>
        <Sequence from={f(outro.start)} durationInFrames={f(outro.dur)}>
          <VietOutro outro={outro} />
          <Sequence from={Math.round(outro.audioAt * fps)}><Audio src={staticFile(outro.audio)} /></Sequence>
        </Sequence>
      </AbsoluteFill>
    );
  };
