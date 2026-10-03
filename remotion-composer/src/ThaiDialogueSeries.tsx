import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const FPS = 30;
const clamp = {extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const};
const C = {ink: "#243138", cream: "#FFF8EB", male: "#1594A4", female: "#EB684E", gold: "#E7A62E", brown: "#6B3D1E"};
const ZH_TITLE = '"STKaiti", "Kaiti SC", "Songti SC", serif';
const ZH_UI = '"PingFang SC", "Noto Sans CJK SC", sans-serif';
const TH = '"Sarabun", "Noto Sans Thai", sans-serif';

type Line = {role: string; speaker: "male" | "female"; th: string; zh: string; rom: string; start: number; end: number; replayStart?: number; replayEnd?: number};
type Word = {th: string; zh: string};
type Lesson = {start: number; end: number; label: string; eyebrow: string; th: string; rom: string; zh: string; note?: string; words: Word[]; cueStarts?: number[]; accent?: "male" | "female" | "gold"};

export type ThaiDialogueSeriesProps = {
  seriesName?: string;
  targetFont?: string;
  maleHonorific?: string;
  femaleHonorific?: string;
  footerSubtitle?: string;
  footerTagline?: string;
  footerTokens?: string;
  episode: string;
  topic: string;
  hook: string;
  exchangeLeft: string;
  exchangeRight: string;
  durationSeconds: number;
  imageSrc: string;
  narrationSrc: string;
  musicSrc: string;
  dialogueIntroStart?: number;
  dialogueStart: number;
  dialogueEnd: number;
  replayStart: number;
  replayIntroStart?: number;
  replayEnd: number;
  outroStart: number;
  lines: Line[];
  lessons: Lesson[];
  speechRanges?: {start: number; end: number}[];
};

const Photo: React.FC<{src: string; duration: number; dim?: number; blur?: number; focus?: string}> = ({src, duration, dim = 0, blur = 0, focus = "50% 45%"}) => {
  const frame = useCurrentFrame();
  const zoom = interpolate(frame, [0, duration * FPS], [1.01, 1.085], clamp);
  return <AbsoluteFill style={{overflow: "hidden", background: "#E8C58D"}}>
    <Img src={staticFile(src)} style={{position: "absolute", inset: -12, width: "calc(100% + 24px)", height: "calc(100% + 24px)", objectFit: "cover", objectPosition: focus, filter: `brightness(1.03) saturate(1.03) blur(${blur}px)`, transform: `scale(${zoom})`, transformOrigin: focus}} />
    <AbsoluteFill style={{background: `rgba(33,25,17,${dim})`}} />
  </AbsoluteFill>;
};

const Brand: React.FC<{label: string; seriesName?: string; light?: boolean}> = ({label, seriesName = "泰语千词", light = false}) => <div style={{position: "absolute", left: 44, right: 44, top: 42, display: "flex", justifyContent: "space-between", alignItems: "center"}}>
  <div style={{padding: "13px 21px", borderRadius: 999, background: light ? "rgba(255,255,255,.88)" : "rgba(25,31,31,.72)", color: light ? "#D05E31" : C.cream, fontFamily: ZH_UI, fontSize: 26, letterSpacing: 3, fontWeight: 800, boxShadow: "0 10px 30px rgba(37,25,14,.14)"}}>{seriesName}</div>
  <div style={{padding: "11px 17px", borderRadius: 999, background: "rgba(255,255,255,.84)", color: C.brown, fontFamily: ZH_UI, fontSize: 21, letterSpacing: 2}}>{label}</div>
</div>;

const SpeechCard: React.FC<{p: ThaiDialogueSeriesProps; line: Line; progress: number}> = ({p, line, progress}) => {
  const color = line.speaker === "male" ? C.male : C.female;
  return <div style={{position: "absolute", left: 62, right: 62, bottom: 310, padding: "28px 34px 32px", borderRadius: 34, background: "rgba(255,255,255,.94)", borderLeft: `10px solid ${color}`, boxShadow: "0 24px 65px rgba(60,38,18,.26)", opacity: progress, transform: `translateY(${(1-progress)*25}px)`}}>
    <div style={{fontFamily: ZH_UI, fontSize: 25, color, letterSpacing: 2, fontWeight: 800}}>{line.role} · {line.speaker === "male" ? (p.maleHonorific ?? "ครับ") : (p.femaleHonorific ?? "ค่ะ / คะ")}</div>
    <div style={{fontFamily: p.targetFont ?? TH, fontSize: line.th.length > 25 ? 55 : 67, fontWeight: 700, color: C.ink, lineHeight: 1.18, marginTop: 8}}>{line.th}</div>
    <div style={{display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 18, marginTop: 8}}>
      <div style={{fontFamily: ZH_TITLE, fontSize: 36, color: "#465156"}}>{line.zh}</div>
      <div style={{fontFamily: ZH_UI, fontSize: 20, color: "#788286", textAlign: "right"}}>谐音 · {line.rom}</div>
    </div>
  </div>;
};

const Hook: React.FC<{p: ThaiDialogueSeriesProps}> = ({p}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 18, stiffness: 120}});
  return <AbsoluteFill>
    <Photo src={p.imageSrc} duration={p.durationSeconds} dim={.2} />
    <AbsoluteFill style={{background: "linear-gradient(180deg, rgba(22,18,13,.10), rgba(22,18,13,.05) 42%, rgba(22,18,13,.80))"}} />
    <Brand label={`${p.episode} · ${p.topic}`} seriesName={p.seriesName} />
    <div style={{position: "absolute", left: 58, right: 58, bottom: 570, color: C.cream, opacity: enter, textAlign: "center", transform: `translateY(${(1-enter)*28}px)`}}>
      <div style={{fontFamily: ZH_TITLE, fontSize: 70, lineHeight: 1.25, textShadow: "0 7px 30px rgba(0,0,0,.28)"}}>{p.hook}</div>
      <div style={{display: "flex", justifyContent: "center", alignItems: "center", gap: 14, marginTop: 30}}>
        <div style={{fontFamily: ZH_UI, fontSize: 29, fontWeight: 800, color: "white", background: C.female, borderRadius: 999, padding: "15px 24px"}}>{p.exchangeLeft}</div>
        <div style={{fontFamily: ZH_TITLE, fontSize: 38, color: "#FFD987"}}>↔</div>
        <div style={{fontFamily: ZH_UI, fontSize: 29, fontWeight: 800, color: "white", background: C.male, borderRadius: 999, padding: "15px 24px"}}>{p.exchangeRight}</div>
      </div>
    </div>
    <div style={{position: "absolute", left: 58, right: 58, bottom: 180, textAlign: "center", fontFamily: ZH_UI, color: "rgba(255,255,255,.82)", fontSize: 23, letterSpacing: 3}}>真实情景 · 一来一回</div>
  </AbsoluteFill>;
};

const IntroScene: React.FC<{p: ThaiDialogueSeriesProps; start: number; label: string; eyebrow: string; title: string; subtitle: string; accent?: string}> = ({p, start, label, eyebrow, title, subtitle, accent = C.gold}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame: frame - Math.round(start * FPS), fps, config: {damping: 18, stiffness: 120}});
  return <AbsoluteFill>
    <Photo src={p.imageSrc} duration={p.durationSeconds} dim={.36} blur={1.4} />
    <AbsoluteFill style={{background: "linear-gradient(180deg, rgba(25,20,14,.08), rgba(25,20,14,.68))"}} />
    <Brand label={label} seriesName={p.seriesName} />
    <div style={{position: "absolute", left: 58, right: 58, top: "50%", padding: "42px 38px 46px", borderRadius: 40, background: "rgba(255,255,255,.95)", boxShadow: "0 28px 80px rgba(45,30,16,.30)", opacity: enter, transform: `translateY(calc(-50% + ${(1-enter)*30}px))`}}>
      <div style={{fontFamily: ZH_UI, fontSize: 27, color: accent, fontWeight: 900, letterSpacing: 3}}>{eyebrow}</div>
      <div style={{fontFamily: ZH_TITLE, fontSize: 61, color: C.ink, lineHeight: 1.3, marginTop: 22}}>{title}</div>
      <div style={{fontFamily: ZH_UI, fontSize: 31, color: "#647075", lineHeight: 1.55, marginTop: 26}}>{subtitle}</div>
    </div>
  </AbsoluteFill>;
};

const Dialogue: React.FC<{p: ThaiDialogueSeriesProps; replay?: boolean}> = ({p, replay = false}) => {
  const t = useCurrentFrame() / FPS;
  const base = replay ? p.replayStart : p.dialogueStart;
  const sourceLines = p.lines.map((line) => replay
    ? {...line, start: line.replayStart ?? base + (line.start - p.dialogueStart), end: line.replayEnd ?? base + (line.end - p.dialogueStart)}
    : line);
  const found = sourceLines.findIndex((line) => t >= line.start - .1 && t <= line.end + .2);
  const index = found >= 0 ? found : Math.max(0, Math.min(sourceLines.length - 1, Math.floor((t - base) / Math.max(.8, (p.dialogueEnd - p.dialogueStart) / sourceLines.length))));
  const line = sourceLines[index];
  const progress = found >= 0 ? interpolate(t, [line.start - .1, line.start + .2], [0, 1], clamp) : .74;
  return <AbsoluteFill>
    <Photo src={p.imageSrc} duration={p.durationSeconds} dim={.05} focus={line.speaker === "male" ? "43% 44%" : "57% 46%"} />
    <AbsoluteFill style={{background: "linear-gradient(180deg, rgba(25,20,14,.08), transparent 50%, rgba(43,28,14,.42))"}} />
    <Brand label={replay ? "慢速再听" : "完整对话"} seriesName={p.seriesName} light />
    <div style={{position: "absolute", top: 154, left: 50, padding: "12px 18px", borderRadius: 18, background: line.speaker === "male" ? "rgba(21,148,164,.94)" : "rgba(235,104,78,.94)", color: "white", fontFamily: ZH_UI, fontSize: 24, fontWeight: 800}}>{line.role}正在说</div>
    <SpeechCard p={p} line={line} progress={progress} />
  </AbsoluteFill>;
};

const LessonCard: React.FC<{p: ThaiDialogueSeriesProps; lesson: Lesson}> = ({p, lesson}) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const {fps} = useVideoConfig();
  const enter = spring({frame: frame - Math.round(lesson.start * FPS), fps, config: {damping: 19, stiffness: 125}});
  const local = t - lesson.start;
  const span = Math.max(1, lesson.end - lesson.start);
  const active = lesson.cueStarts?.length
    ? Math.max(0, lesson.cueStarts.filter((cue) => cue <= local).length - 1)
    : Math.min(lesson.words.length - 1, Math.max(0, Math.floor(local / span * lesson.words.length)));
  const accent = lesson.accent === "male" ? C.male : lesson.accent === "female" ? C.female : C.gold;
  return <AbsoluteFill>
    <Photo src={p.imageSrc} duration={p.durationSeconds} dim={.42} blur={2} />
    <Brand label={lesson.label} seriesName={p.seriesName} />
    <div style={{position: "absolute", top: 125, left: 58, right: 58, color: C.cream, fontFamily: ZH_TITLE, fontSize: 50}}>{lesson.eyebrow}</div>
    <div style={{position: "absolute", left: 58, right: 58, top: 215, padding: "38px 34px 38px", borderRadius: 38, background: "rgba(255,255,255,.95)", boxShadow: "0 28px 72px rgba(48,30,14,.30)", opacity: enter, transform: `translateY(${(1-enter)*24}px)`}}>
      <div style={{fontFamily: p.targetFont ?? TH, fontSize: lesson.th.length > 28 ? 54 : 70, fontWeight: 700, lineHeight: 1.16, textAlign: "center", color: C.ink}}>{lesson.th}</div>
      <div style={{fontFamily: ZH_UI, fontSize: 23, textAlign: "center", color: accent, marginTop: 8}}>谐音 · {lesson.rom}</div>
      <div style={{display: "grid", gridTemplateColumns: lesson.words.length === 1 ? "1fr" : "1fr 1fr", gap: 14, marginTop: 30}}>
        {lesson.words.map((word, i) => <div key={`${word.th}-${i}`} style={{minHeight: 140, padding: "16px 14px", borderRadius: 20, background: i === active ? "#F4C859" : "#EDF0EC", outline: i === active ? `5px solid ${accent}` : "none", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", transform: `scale(${i === active ? 1.02 : 1})`}}>
          <div style={{fontFamily: p.targetFont ?? TH, fontSize: word.th.length > 13 ? 38 : 48, fontWeight: 700, textAlign: "center", color: C.ink}}>{word.th}</div>
          <div style={{fontFamily: ZH_UI, fontSize: 25, color: "#596467", marginTop: 5, fontWeight: 800, textAlign: "center"}}>{word.zh}</div>
        </div>)}
      </div>
      <div style={{fontFamily: ZH_TITLE, fontSize: 44, textAlign: "center", color: C.ink, marginTop: 28}}>{lesson.zh}</div>
      {lesson.note ? <div style={{fontFamily: ZH_UI, fontSize: 24, textAlign: "center", color: "#6E7778", marginTop: 14, lineHeight: 1.5}}>{lesson.note}</div> : null}
    </div>
  </AbsoluteFill>;
};

const Outro: React.FC<{p: ThaiDialogueSeriesProps}> = ({p}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame: frame - Math.round(p.outroStart * FPS), fps, config: {damping: 18, stiffness: 125}});
  return <AbsoluteFill>
    <Photo src={p.imageSrc} duration={p.durationSeconds} dim={.55} blur={1.5} />
    <AbsoluteFill style={{background: "linear-gradient(180deg, rgba(45,30,15,.18), rgba(45,30,15,.72))"}} />
    <div style={{position: "absolute", left: 0, right: 0, top: 470, display: "flex", flexDirection: "column", alignItems: "center", opacity: enter, transform: `translateY(${(1-enter)*28}px)`}}>
      <div style={{fontFamily: ZH_TITLE, fontSize: 83, color: "#FFD376", letterSpacing: 8}}>{p.seriesName ?? "泰语千词"}</div>
      <div style={{fontFamily: ZH_UI, fontSize: 34, color: C.cream, letterSpacing: 4, marginTop: 18}}>{p.footerSubtitle ?? "听懂两句 · 回答两句"}</div>
      <div style={{width: 510, height: 2, background: "rgba(255,211,118,.40)", marginTop: 64}} />
      <div style={{fontFamily: ZH_TITLE, fontSize: 46, color: C.cream, marginTop: 60}}>{p.footerTagline ?? "泰语千词，在泰国生活够用了"}</div>
      <div style={{fontFamily: p.targetFont ?? TH, fontSize: 42, color: "rgba(255,255,255,.80)", marginTop: 58}}>{p.footerTokens ?? "ครับ · ค่ะ · คะ"}</div>
    </div>
  </AbsoluteFill>;
};

export const ThaiDialogueSeries: React.FC<ThaiDialogueSeriesProps> = (p) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  let scene: React.ReactNode;
  const replayIntroStart = p.replayIntroStart ?? p.replayStart;
  if (t < p.dialogueStart) scene = <Hook p={p} />;
  else if (t < p.dialogueEnd) scene = <Dialogue p={p} />;
  else {
    const lesson = p.lessons.find((item) => t >= item.start && t < item.end);
    if (lesson) scene = <LessonCard p={p} lesson={lesson} />;
    else if (t < p.replayEnd && t >= replayIntroStart) scene = <Dialogue p={p} replay />;
    else scene = <Outro p={p} />;
  }
  const speaking = (p.speechRanges ?? []).some((range) => t >= range.start - .12 && t <= range.end + .18);
  const musicBase = speaking ? .034 : .075;
  const musicVolume = musicBase * interpolate(t, [0, 1.2, p.durationSeconds - 2.5, p.durationSeconds], [0, 1, 1, 0], clamp);
  return <AbsoluteFill style={{background: "#E8C58D"}}>
    <AbsoluteFill>{scene}</AbsoluteFill>
    <Audio src={staticFile(p.musicSrc)} volume={musicVolume} loop />
    <Audio src={staticFile(p.narrationSrc)} />
    <div style={{position: "absolute", left: 48, right: 48, bottom: 34, height: 4, borderRadius: 4, background: "rgba(255,255,255,.28)", overflow: "hidden", opacity: t < .5 ? 0 : 1}}>
      <div style={{height: "100%", width: `${Math.min(100, t / p.durationSeconds * 100)}%`, background: "linear-gradient(90deg,#1594A4,#F4C859,#EB684E)"}} />
    </div>
  </AbsoluteFill>;
};
