import React from "react";
import {
  AbsoluteFill, Audio, Img, Loop, OffthreadVideo, Sequence,
  interpolate, spring, staticFile, useCurrentFrame, useVideoConfig,
  continueRender, delayRender,
} from "remotion";

const handle = delayRender("proverb-fonts", { timeoutInMilliseconds: 240000 });
Promise.all([
  new FontFace("SarabunBold", `url(${staticFile("zen/fonts/Sarabun-Bold.ttf")})`).load(),
  new FontFace("SarabunRegular", `url(${staticFile("zen/fonts/Sarabun-Regular.ttf")})`).load(),
  new FontFace("NotoSerifSCBold", `url(${staticFile("zen/fonts/NotoSerifSC-Bold-subset.woff2")})`).load(),
]).then((fonts) => { fonts.forEach((f) => (document.fonts as FontFaceSet).add(f)); continueRender(handle); }).catch(() => continueRender(handle));

const THAI = "SarabunBold, sans-serif";
const THAI_R = "SarabunRegular, sans-serif";
const ZH = "NotoSerifSCBold, serif";
const GOLD = "#FFC94D";
const CREAM = "#FFFBF0";
const FPS = 30;
const s = (sec: number) => Math.round(sec * FPS);

// per-word start times inside pv_th.mp3 (word-by-word read) — for karaoke highlight
const TOKEN_STARTS = [0.0, 0.246, 0.491, 1.16, 1.413, 1.583, 1.752, 1.92, 2.474, 2.613, 3.33, 3.932, 4.132, 4.333, 4.533];
const PV_TH_TOTAL = 4.734;
const VO_OFFSET = 0.5; // pv_th starts 0.5s into the sentence/recap card

const DUR: Record<string, number> = {
  pv_hook: 4.56, pv_th: 4.734, pv_zh: 7.8, zh_cta: 3.672,
  pw1_th: 1.776, pw2_th: 1.776, pw3_th: 1.776, pw4_th: 1.656, pw5_th: 1.776, pw6_th: 1.68, pw7_th: 1.776,
  pw1_zh: 1.8, pw2_zh: 1.944, pw3_zh: 2.472, pw4_zh: 1.872, pw5_zh: 1.824, pw6_zh: 1.944, pw7_zh: 1.944,
};

const SENTENCE = {
  // each line is an array of words; rendered with an explicit gap between words
  th: [
    ["คบ", "คน", "พาล"],
    ["พาล", "พา", "ไป", "หา", "ผิด"],
    ["คบ", "บัณฑิต"],
    ["บัณฑิต", "พา", "ไป", "หา", "ผล"],
  ],
  zh: ["结交坏人，被带向过错", "结交贤者，被带向善果"],
};
const WORDS = [
  { th: "คบ", roman: "kóp", zh: "结交" },
  { th: "พาล", roman: "phaan", zh: "坏人 · 恶徒" },
  { th: "พา", roman: "phaa", zh: "带 · 引领" },
  { th: "หา", roman: "hǎa", zh: "走向 · 寻" },
  { th: "ผิด", roman: "phìt", zh: "过错 · 错" },
  { th: "บัณฑิต", roman: "ban-dìt", zh: "贤者 · 智者" },
  { th: "ผล", roman: "phǒn", zh: "成果 · 结果" },
];

type Cue = { start: number; dur: number; file: string };
const cues: Cue[] = [];
const cue = (start: number, dur: number, file: string) => cues.push({ start, dur, file });
type Block = { start: number; end: number };

const HOOK: Block = { start: 0, end: 5.0 };
cue(0.6, DUR.pv_hook, "pv_hook");
let cur = HOOK.end;
const sTh = cur + 0.5;
const sZh = sTh + DUR.pv_th + 0.5;
const SENT: Block = { start: cur, end: sZh + DUR.pv_zh + 0.8 };
cue(sTh, DUR.pv_th, "pv_th");
cue(sZh, DUR.pv_zh, "pv_zh");
cur = SENT.end;
const wordBlocks: Block[] = [];
WORDS.forEach((_, i) => {
  const start = cur;
  const t = start + 0.35;
  const z = t + DUR[`pw${i + 1}_th`] + 0.25;
  const end = z + DUR[`pw${i + 1}_zh`] + 0.55;
  cue(t, DUR[`pw${i + 1}_th`], `pw${i + 1}_th`);
  cue(z, DUR[`pw${i + 1}_zh`], `pw${i + 1}_zh`);
  wordBlocks.push({ start, end });
  cur = end;
});
const rTh = cur + 0.5;
const RECAP: Block = { start: cur, end: rTh + DUR.pv_th + 0.9 };
cue(rTh, DUR.pv_th, "pv_th");
cur = RECAP.end;
const CTA_B: Block = { start: cur + 0.4, end: cur + 0.4 + DUR.zh_cta + 1.6 };
cue(CTA_B.start + 0.6, DUR.zh_cta, "zh_cta");
const TOTAL = CTA_B.end;

const VideoLayer: React.FC<{ src: string; loopFrames: number }> = ({ src, loopFrames }) => (
  <AbsoluteFill><Loop durationInFrames={loopFrames}><OffthreadVideo src={staticFile(src)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} /></Loop></AbsoluteFill>
);
const FadeInBg: React.FC<{ children: React.ReactNode; fade: number }> = ({ children, fade }) => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [0, fade], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ opacity: op }}>{children}</AbsoluteFill>;
};
const Scrim: React.FC = () => (
  <AbsoluteFill>
    <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(10,14,20,0.32) 0%, rgba(10,14,20,0.14) 42%, rgba(10,14,20,0.5) 100%)" }} />
    <AbsoluteFill style={{ background: "radial-gradient(64% 42% at 50% 50%, rgba(10,14,20,0.34) 0%, rgba(10,14,20,0) 72%)" }} />
    <AbsoluteFill style={{ opacity: 0.05, mixBlendMode: "overlay", backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")", backgroundSize: "180px 180px" }} />
  </AbsoluteFill>
);
const fadeWin = (local: number, dur: number, inF: number, outF: number) =>
  interpolate(local, [0, inF, dur - outF, dur], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

const SeriesTag: React.FC = () => (
  <div style={{ position: "absolute", top: 66, left: 44, fontFamily: ZH, fontSize: 22, letterSpacing: 3, color: "rgba(243,236,221,0.66)", zIndex: 30, textShadow: "0 2px 10px rgba(0,0,0,0.6)" }}>泰语千词 · 每天学一句</div>
);
const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const op = fadeWin(frame, s(HOOK.end - HOOK.start), 20, 16);
  const rise = interpolate(frame, [0, 36], [24, 0], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: op }}>
      <div style={{ fontFamily: ZH, fontSize: 48, lineHeight: 1.5, color: CREAM, textAlign: "center", transform: `translateY(${rise}px)`, textShadow: "0 2px 20px rgba(0,0,0,0.75)" }}>
        跟什么样的人，<div>就走什么样的路？</div>
      </div>
    </AbsoluteFill>
  );
};
const SentenceCard: React.FC<{ dur: number; label?: string }> = ({ dur, label }) => {
  const frame = useCurrentFrame();
  const op = fadeWin(frame, s(dur), 22, 20);
  const rise = interpolate(frame, [0, 44], [22, 0], { extrapolateRight: "clamp" });
  // karaoke: which word is being spoken right now
  const elapsed = frame / FPS - VO_OFFSET;
  let active = -1;
  if (elapsed >= 0 && elapsed <= PV_TH_TOTAL + 0.25) {
    for (let k = 0; k < TOKEN_STARTS.length; k++) if (elapsed >= TOKEN_STARTS[k]) active = k;
  }
  let flat = -1;
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: op }}>
      <div style={{ transform: `translateY(${rise}px)`, textAlign: "center", padding: "0 30px" }}>
        {label && <div style={{ fontFamily: ZH, fontSize: 24, letterSpacing: 4, color: "rgba(243,236,221,0.6)", marginBottom: 22, textShadow: "0 2px 10px rgba(0,0,0,0.7)" }}>{label}</div>}
        <div style={{ fontFamily: THAI, fontSize: 40, lineHeight: 1.55, textShadow: "0 2px 22px rgba(0,0,0,0.85)" }}>
          {SENTENCE.th.map((words, i) => (
            <div key={i} style={{ display: "flex", justifyContent: "center", gap: "0.55em" }}>
              {words.map((w, j) => {
                flat += 1;
                const on = flat === active;
                return (
                  <span key={j} style={{ color: on ? GOLD : "rgba(255,251,240,0.62)", transform: on ? "scale(1.06)" : "scale(1)", display: "inline-block", textShadow: on ? "0 0 26px rgba(255,201,77,0.95), 0 2px 18px rgba(0,0,0,0.7)" : "0 2px 16px rgba(0,0,0,0.7)", transition: "none" }}>{w}</span>
                );
              })}
            </div>
          ))}
        </div>
        <div style={{ width: 46, height: 2, background: GOLD, opacity: 0.45, margin: "20px auto" }} />
        <div style={{ fontFamily: ZH, fontSize: 29, lineHeight: 1.55, color: CREAM, textShadow: "0 2px 16px rgba(0,0,0,0.85)" }}>
          {SENTENCE.zh.map((t, i) => (<div key={i} style={{ whiteSpace: "nowrap", color: i >= 1 ? "#EAD8A6" : CREAM }}>{t}</div>))}
        </div>
      </div>
    </AbsoluteFill>
  );
};
const WordCard: React.FC<{ w: (typeof WORDS)[number]; dur: number; idx: number; total: number }> = ({ w, dur, idx, total }) => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const op = fadeWin(frame, s(dur), 12, 12);
  const sp = spring({ frame, fps, config: { damping: 16, stiffness: 95 } });
  const scale = interpolate(sp, [0, 1], [0.9, 1]);
  const size = w.th.length > 8 ? 64 : 92;
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: op }}>
      <div style={{ position: "absolute", top: 152, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 10 }}>
        {Array.from({ length: total }).map((_, i) => (<div key={i} style={{ width: 8, height: 8, borderRadius: "50%", background: i === idx ? GOLD : "rgba(243,236,221,0.3)" }} />))}
      </div>
      <div style={{ position: "absolute", top: 196, left: 0, right: 0, textAlign: "center", fontFamily: ZH, fontSize: 24, letterSpacing: 4, color: "rgba(243,236,221,0.6)", textShadow: "0 2px 10px rgba(0,0,0,0.7)" }}>逐字拆解 {idx + 1} / {total}</div>
      <div style={{ textAlign: "center", transform: `scale(${scale})` }}>
        <div style={{ fontFamily: THAI, fontSize: size, color: GOLD, lineHeight: 1.2, textShadow: "0 2px 20px rgba(0,0,0,0.7)" }}>{w.th}</div>
        <div style={{ fontFamily: THAI_R, fontSize: 28, color: "rgba(243,236,221,0.7)", marginTop: 8, letterSpacing: 1, textShadow: "0 1px 8px rgba(0,0,0,0.8)" }}>{w.roman}</div>
        <div style={{ width: 56, height: 2, background: GOLD, opacity: 0.5, margin: "20px auto" }} />
        <div style={{ fontFamily: ZH, fontSize: 44, color: CREAM, textShadow: "0 2px 16px rgba(0,0,0,0.8)" }}>{w.zh}</div>
      </div>
    </AbsoluteFill>
  );
};
const CTA: React.FC<{ variant: "xhs" | "overseas" }> = ({ variant }) => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const op = fadeWin(frame, s(CTA_B.end - CTA_B.start), 16, 8);
  const sp = spring({ frame, fps, config: { damping: 20, stiffness: 90 } });
  const scale = interpolate(sp, [0, 1], [0.8, 1]);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: op }}>
      <div style={{ textAlign: "center" }}>
        <Img src={staticFile("zen/app/app_icon.png")} style={{ width: 128, height: 128, borderRadius: 29, transform: `scale(${scale})`, boxShadow: "0 14px 40px rgba(0,0,0,0.55)" }} />
        <div style={{ marginTop: 24, fontFamily: ZH, fontSize: 46, color: GOLD, letterSpacing: 2, textShadow: "0 2px 16px rgba(0,0,0,0.7)" }}>泰语千词</div>
        <div style={{ marginTop: 14, fontFamily: ZH, fontSize: 32, color: CREAM, letterSpacing: 1, textShadow: "0 2px 12px rgba(0,0,0,0.8)" }}>在泰国生活，够用了</div>
        {variant === "overseas" && (<div style={{ marginTop: 26, fontFamily: ZH, fontSize: 22, color: "rgba(243,236,221,0.7)", letterSpacing: 1 }}>App Store · Google Play</div>)}
      </div>
    </AbsoluteFill>
  );
};

export const ZenProverbFriends: React.FC<{ variant: "xhs" | "overseas" }> = ({ variant }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#0a1420" }}>
      <AbsoluteFill>
        <VideoLayer src="zen/scenes/scene_watarun.mp4" loopFrames={785} />
        <Sequence from={s(32)} name="bg-buddha"><FadeInBg fade={40}><VideoLayer src="zen/scenes/scene_buddha.mp4" loopFrames={919} /></FadeInBg></Sequence>
        <Scrim />
      </AbsoluteFill>
      <SeriesTag />
      <Sequence from={s(HOOK.start)} durationInFrames={s(HOOK.end - HOOK.start)} name="hook"><Hook /></Sequence>
      <Sequence from={s(SENT.start)} durationInFrames={s(SENT.end - SENT.start)} name="sentence"><SentenceCard dur={SENT.end - SENT.start} /></Sequence>
      {WORDS.map((w, i) => {
        const b = wordBlocks[i];
        return (<Sequence key={i} from={s(b.start)} durationInFrames={s(b.end - b.start)} name={`word-${i}`}><WordCard w={w} dur={b.end - b.start} idx={i} total={WORDS.length} /></Sequence>);
      })}
      <Sequence from={s(RECAP.start)} durationInFrames={s(RECAP.end - RECAP.start)} name="recap"><SentenceCard dur={RECAP.end - RECAP.start} label="整句 · 再读一次" /></Sequence>
      <Sequence from={s(CTA_B.start)} durationInFrames={s(CTA_B.end - CTA_B.start) + 4} name="cta"><CTA variant={variant} /></Sequence>
      {cues.map((c, i) => (<Sequence key={`a-${i}`} from={s(c.start)} name={`a-${c.file}-${i}`}><Audio src={staticFile(`zen/audio/${c.file}.mp3`)} volume={0.98} /></Sequence>))}
    </AbsoluteFill>
  );
};
export const PROVERB_TOTAL_FRAMES = s(TOTAL) + 4;
