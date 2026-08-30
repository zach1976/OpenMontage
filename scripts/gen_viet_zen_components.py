#!/usr/bin/env python3
"""生成越南语禅意五集的组件。底盘（BgFilm/Atmosphere/CoverPlate/Sentence/Outro）
是引擎知识，五集共用同一段模板；**装置和词卡各集独立**，写在 DEVICE/CARD 里。
"""
from pathlib import Path

REPO = Path("/Users/zhenyusong/projects/OpenMontage")

CHASSIS = '''import React from "react";
import { loadFonts, ZH_TITLE, ZH_UI } from "./CjkFonts";
import { AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, interpolate, staticFile,
         useCurrentFrame } from "remotion";

// ---------------------------------------------------------------------------
// 越南语千词 · 禅意 __NO__「__NAME__」
//
// 句子新写，卡上教的实词全部取自 viet1000 词库（scaffold_zen_viet.py --check 逐个核过）。
// 封面＝成片第一帧，整张由 ChatGPT 生成（品牌行/期号/标题/越南语/闲章都在图里），
// 代码不再画封面上的任何元素 —— 只铺图、末尾淡出交回空镜。
//
// 装置：__ART__
// 反模式：不做卡片、不做色块高亮、不弹跳、不催促、不烧 hashtag、不提评论区。
// ---------------------------------------------------------------------------

loadFonts([["VietBold", "BeVietnamPro-Bold.ttf"], ["VietSemi", "BeVietnamPro-SemiBold.ttf"],
           ["SerifSC", "NotoSerifSC-Bold.otf"]]);

const ZH = ZH_TITLE, ZH_S = ZH_UI;
const VI = "VietBold, sans-serif", VI_R = "VietSemi, sans-serif";

const INK = "__INK__";
const CREAM = "__CREAM__";
const DIM = "__DIM__";
const ACCENT = "__ACCENT__";        // 全片唯一的强色，只给越南语

export type Word = { id: string; thai: string; roman: string; zh: string;
                     start: number; dur: number;
                     zhAudio: string; thAudio: string; zhAt: number; thAt: number; thAt2: number };
export type Props = {
  hook: any; sentence: any; words: Word[]; again: any; outro: any;
  cover?: string;
  bg?: { src: string; start: number; dur: number; xf: number }[];
  bgm: { src: string; gain: number }; speak: number[][]; fps: number;
};

/** 底片：一段接一段，整条片子只挂这一层（放进各场景里会让视频每场重播） */
const BgFilm: React.FC<{ bg: any[]; fps: number }> = ({ bg, fps }) => (
  <AbsoluteFill>
    {bg.map((b, i) => {
      const from = Math.round(b.start * fps), len = Math.round((b.dur + b.xf) * fps);
      return (
        <Sequence key={i} from={from} durationInFrames={len} layout="none">
          <Clip src={b.src} xf={Math.round(b.xf * fps)} len={len} first={i === 0} />
        </Sequence>
      );
    })}
  </AbsoluteFill>
);

const Clip: React.FC<{ src: string; xf: number; len: number; first: boolean }> = ({ src, xf, len, first }) => {
  const f = useCurrentFrame();
  const inp = first ? 1 : interpolate(f, [0, xf], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const outp = interpolate(f, [len - xf, len], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ opacity: inp * outp }}>
      <OffthreadVideo src={staticFile(src)} muted
                      style={{ width: "100%", height: "100%", objectFit: "cover" }} />
    </AbsoluteFill>
  );
};

/** 墨色罩子。底片只是底纹，字必须永远压得住它；暗压在四角与下端，中段留一档给正文 */
const Atmosphere: React.FC = () => {
  const f = useCurrentFrame();
  const drift = (p: number, amp: number) => Math.sin(f / 300 + p) * amp;
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ backgroundColor: "__SCRIM__" }} />
      <AbsoluteFill style={{ background: "__RADIAL__" }} />
      {[[320, 560, 480, 0], [780, 1040, 540, 2.6]].map(([x, y, r, ph], i) => (
        <div key={i} style={{ position: "absolute", left: x + drift(ph, 22) - r / 2,
                              top: y + drift(ph + 1, 14) - r / 2, width: r, height: r,
                              borderRadius: "50%", filter: "blur(98px)",
                              background: "__FOG__" }} />
      ))}
      <AbsoluteFill style={{ background: "__VGRAD__" }} />
      <AbsoluteFill style={{ background:
        "radial-gradient(70% 50% at 50% 42%, rgba(0,0,0,0) 34%, rgba(0,0,0,0.62) 100%)" }} />
    </AbsoluteFill>
  );
};

/** 封面：整张生成图，只铺钩子那一段，末尾 26 帧淡出。不加任何罩子 —— 图里已有文字与明暗 */
const CoverPlate: React.FC<{ src: string; dur: number; fps: number }> = ({ src, dur, fps }) => {
  const f = useCurrentFrame(), n = Math.round(dur * fps);
  const out = interpolate(f, [n - 26, n], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ opacity: out }}>
      <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
    </AbsoluteFill>
  );
};

const Brand: React.FC = () => (
  <div style={{ position: "absolute", top: 150, width: "100%", textAlign: "center",
                fontFamily: ZH_S, fontSize: 28, letterSpacing: 8, color: DIM }}>
    越南语千词 · 每天一句
  </div>
);

const fade = (frame: number, a: number, b: number, c: number, d: number) =>
  interpolate(frame, [a, b, c, d], [0, 1, 1, 0],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

__DEVICE__

/** 钩子的画面整个来自生成图，这里只剩旁白 */
const Hook: React.FC<{ h: any; fps: number }> = ({ h, fps }) => (
  <AbsoluteFill>
    <Sequence from={Math.round((h.audioAt - h.start) * fps)}><Audio src={staticFile(h.audio)} /></Sequence>
  </AbsoluteFill>
);

const Sentence: React.FC<{ s: any; fps: number }> = ({ s, fps }) => {
  const f = useCurrentFrame(), n = Math.round(s.dur * fps);
  const p = fade(f, 0, 30, n - 22, n);
  const q = interpolate(f, [24, 56], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <Brand />
      {/* 断点自己定：越南语叠标多，交给浏览器断行会把词拆开 */}
      {(s.lines || [s.thai]).map((ln: string, i: number) => (
        <div key={i} style={{ position: "absolute", top: 700 + i * 104, width: 960, left: 60,
                              textAlign: "center", fontFamily: VI, fontSize: 62, lineHeight: 1.35,
                              letterSpacing: 0.5, color: ACCENT, opacity: p, whiteSpace: "nowrap" }}>
          {ln}
        </div>
      ))}
      <div style={{ position: "absolute", top: 1004, width: 960, left: 60, textAlign: "center",
                    fontFamily: ZH, fontSize: 52, lineHeight: 1.5, color: CREAM, opacity: q }}>
        {s.zh}
      </div>
      {s.audio ? (
        <Sequence from={Math.round((s.audioAt - s.start) * fps)}><Audio src={staticFile(s.audio)} /></Sequence>
      ) : null}
      {s.thAudio ? (
        <Sequence from={Math.round((s.thAt - s.start) * fps)}><Audio src={staticFile(s.thAudio)} /></Sequence>
      ) : null}
    </AbsoluteFill>
  );
};

__CARD__

const Outro: React.FC<{ o: any; fps: number }> = ({ o, fps }) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [0, 30], [0, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", top: 700, width: "100%", display: "flex",
                    justifyContent: "center", opacity: p }}>
        <div style={{ width: 172, height: 172, borderRadius: 40, overflow: "hidden",
                      border: "2px solid __BORDER__" }}>
          <Img src={staticFile("app/app_icon.png")} style={{ width: "100%", height: "100%" }} />
        </div>
      </div>
      <div style={{ position: "absolute", top: 928, width: "100%", textAlign: "center",
                    fontFamily: ZH, fontSize: 58, letterSpacing: 8, color: ACCENT, opacity: p }}>越南语千词</div>
      <div style={{ position: "absolute", top: 1018, width: "100%", textAlign: "center",
                    fontFamily: ZH_S, fontSize: 32, letterSpacing: 3, color: DIM, opacity: p }}>
        在越南生活，够用了
      </div>
      <Sequence from={Math.round((o.audioAt - o.start) * fps)}><Audio src={staticFile(o.audio)} /></Sequence>
    </AbsoluteFill>
  );
};

export const __COMP__: React.FC<Props> = ({ hook, sentence, words, again, outro, cover, bg, bgm, speak, fps }) => {
  const f = (s: number) => Math.round(s * fps);
  const duck = (frame: number) => {
    const t = frame / fps;
    return speak.some(([a, b]) => t >= a - 0.2 && t <= b + 0.3) ? bgm.gain * 0.55 : bgm.gain;
  };
  return (
    <AbsoluteFill style={{ backgroundColor: INK }}>
      {bg?.length ? <BgFilm bg={bg} fps={fps} /> : null}
      <Atmosphere />
      {cover ? (
        <Sequence from={0} durationInFrames={f(hook.dur) + 8} layout="none">
          <CoverPlate src={cover} dur={hook.dur} fps={fps} />
        </Sequence>
      ) : null}
      <Audio src={staticFile(bgm.src)} volume={duck} />
      <Sequence from={0} durationInFrames={f(hook.dur)}><Hook h={hook} fps={fps} /></Sequence>
      <Sequence from={f(sentence.start)} durationInFrames={f(sentence.dur)}>
        <Sentence s={sentence} fps={fps} />
      </Sequence>
      {words.map((w, i) => (
        <Sequence key={w.id} from={f(w.start)} durationInFrames={f(w.dur)}>
          <WordCard w={w} index={i} total={words.length} fps={fps} />
        </Sequence>
      ))}
      <Sequence from={f(again.start)} durationInFrames={f(again.dur)}>
        <Sentence s={again} fps={fps} />
      </Sequence>
      <Sequence from={f(outro.start)} durationInFrames={f(outro.dur)}>
        <Outro o={outro} fps={fps} />
      </Sequence>
    </AbsoluteFill>
  );
};
'''

# ── 每集独立的装置 + 词卡（创意部分，绝不共用） ─────────────────────────────
EPS = {}

# 01 无常：同一个方框，词一个个被顶进来又被顶走 —— 位置永远在，内容永远换
EPS["viet-zen-01-mainmai"] = dict(
  comp="MaiMai", no="01", name="无常",
  art="同一个位置反复被顶掉：所有词都出现在画面正中那个方框里，下一个进来就把上一个推走。",
  ink="#0C1416", cream="#E9E6DE", dim="rgba(233,230,222,0.42)", accent="#CFD8D2",
  scrim="rgba(12,20,22,0.30)", border="rgba(207,216,210,0.55)",
  radial="radial-gradient(126% 72% at 50% 34%, rgba(30,52,56,0.10) 0%, rgba(18,32,36,0.26) 48%, rgba(12,20,22,0.74) 100%)",
  fog="rgba(150,190,190,0.09)",
  vgrad="linear-gradient(180deg, rgba(12,20,22,0.46) 0%, rgba(12,20,22,0.05) 20%, rgba(12,20,22,0.40) 44%, rgba(12,20,22,0.40) 58%, rgba(12,20,22,0.06) 76%, rgba(12,20,22,0.62) 100%)",
  device='''/** 装置：一个固定的方框。词在里头被替换，框一动不动 —— 留下的是位置，不是内容 */
const Frame: React.FC<{ op: number }> = ({ op }) => {
  const L = 132, T = 726, W = 816, H = 300, C = 44;
  const seg = (s: React.CSSProperties) => (
    <div style={{ position: "absolute", background: "rgba(207,216,210,0.34)", ...s }} />
  );
  return (
    <div style={{ opacity: op }}>
      {seg({ left: L, top: T, width: C, height: 1 })}
      {seg({ left: L + W - C, top: T, width: C, height: 1 })}
      {seg({ left: L, top: T + H, width: C, height: 1 })}
      {seg({ left: L + W - C, top: T + H, width: C, height: 1 })}
      {seg({ left: L, top: T, width: 1, height: C })}
      {seg({ left: L + W, top: T, width: 1, height: C })}
      {seg({ left: L, top: T + H - C, width: 1, height: C })}
      {seg({ left: L + W, top: T + H - C, width: 1, height: C })}
    </div>
  );
};''',
  card='''const WordCard: React.FC<{ w: Word; index: number; total: number; fps: number }> =
({ w, index, total, fps }) => {
  const f = useCurrentFrame(), n = Math.round(w.dur * fps);
  // 进：从右侧被推进框；出：被下一个从左侧顶走。框本身不动
  const inx = interpolate(f, [0, 22], [96, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const outx = interpolate(f, [n - 20, n], [0, -96], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const p = fade(f, 0, 20, n - 18, n);
  const q = interpolate(f, [22, 50], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <Brand />
      <div style={{ position: "absolute", top: 236, width: "100%", textAlign: "center",
                    fontFamily: ZH_S, fontSize: 24, letterSpacing: 8, color: DIM, opacity: p }}>
        逐词拆解 {index + 1} / {total}
      </div>
      <Frame op={0.9} />
      <div style={{ position: "absolute", top: 800, width: 816, left: 132, textAlign: "center",
                    fontFamily: VI, fontSize: 92, lineHeight: 1.3, color: ACCENT, opacity: p,
                    transform: `translateX(${inx + outx}px)` }}>
        {w.thai}
      </div>
      <div style={{ position: "absolute", top: 940, width: 816, left: 132, textAlign: "center",
                    fontFamily: ZH, fontSize: 52, lineHeight: 1.4, color: CREAM, opacity: q,
                    transform: `translateX(${(inx + outx) * 0.5}px)` }}>
        {w.zh}
      </div>
      <Sequence from={Math.round((w.zhAt - w.start) * fps)}><Audio src={staticFile(w.zhAudio)} /></Sequence>
      <Sequence from={Math.round((w.thAt - w.start) * fps)}><Audio src={staticFile(w.thAudio)} /></Sequence>
      <Sequence from={Math.round((w.thAt2 - w.start) * fps)}><Audio src={staticFile(w.thAudio)} /></Sequence>
    </AbsoluteFill>
  );
};''')

# 02 放下：一对括号钳住词，念到第二遍向两侧张开把词放出去
EPS["viet-zen-02-buongbo"] = dict(
  comp="BuongBo", no="02", name="放下",
  art="张开的手：一对括号钳住词，念第二遍时向两侧张开，把词放出去。",
  ink="#130E0A", cream="#F0E7DA", dim="rgba(240,231,218,0.42)", accent="#DB9455",
  scrim="rgba(19,14,10,0.32)", border="rgba(219,148,85,0.55)",
  radial="radial-gradient(122% 70% at 50% 34%, rgba(64,40,20,0.12) 0%, rgba(32,22,14,0.28) 50%, rgba(19,14,10,0.76) 100%)",
  fog="rgba(219,148,85,0.09)",
  vgrad="linear-gradient(180deg, rgba(19,14,10,0.46) 0%, rgba(19,14,10,0.05) 20%, rgba(19,14,10,0.40) 44%, rgba(19,14,10,0.40) 58%, rgba(19,14,10,0.06) 76%, rgba(19,14,10,0.64) 100%)",
  device='''/** 装置：一对括号。收拢＝握着，张开＝放下。开合幅度由 `open` 驱动 */
const Grip: React.FC<{ open: number; op: number }> = ({ open, op }) => {
  const y = 862, h = 168, gap = 250 + open * 210;
  const arm = (x: number, dir: number) => (
    <svg viewBox="0 0 40 200" style={{ position: "absolute", left: x - 20, top: y - h / 2,
                                       width: 40, height: h, opacity: op }}>
      <path d={dir > 0 ? "M34,6 C10,54 10,146 34,194" : "M6,6 C30,54 30,146 6,194"}
            fill="none" stroke="#DB9455" strokeWidth="5" strokeLinecap="round" />
    </svg>
  );
  return (<>{arm(540 - gap, 1)}{arm(540 + gap, -1)}</>);
};''',
  card='''const WordCard: React.FC<{ w: Word; index: number; total: number; fps: number }> =
({ w, index, total, fps }) => {
  const f = useCurrentFrame(), n = Math.round(w.dur * fps);
  const p = fade(f, 0, 24, n - 20, n);
  const q = interpolate(f, [22, 50], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  // 第二遍开始张开 —— 跟读的那一拍，手正好松开
  const o2 = Math.round((w.thAt2 - w.start) * fps);
  const open = interpolate(f, [o2 - 6, o2 + 26], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <Brand />
      <div style={{ position: "absolute", top: 236, width: "100%", textAlign: "center",
                    fontFamily: ZH_S, fontSize: 24, letterSpacing: 8, color: DIM, opacity: p }}>
        逐词拆解 {index + 1} / {total}
      </div>
      <Grip open={open} op={p * 0.85} />
      <div style={{ position: "absolute", top: 800, width: 960, left: 60, textAlign: "center",
                    fontFamily: VI, fontSize: 90, lineHeight: 1.3, color: ACCENT, opacity: p,
                    transform: `translateY(${(open * 26).toFixed(1)}px)` }}>
        {w.thai}
      </div>
      <div style={{ position: "absolute", top: 986, width: 960, left: 60, textAlign: "center",
                    fontFamily: ZH, fontSize: 52, lineHeight: 1.4, color: CREAM, opacity: q }}>
        {w.zh}
      </div>
      <Sequence from={Math.round((w.zhAt - w.start) * fps)}><Audio src={staticFile(w.zhAudio)} /></Sequence>
      <Sequence from={Math.round((w.thAt - w.start) * fps)}><Audio src={staticFile(w.thAudio)} /></Sequence>
      <Sequence from={o2}><Audio src={staticFile(w.thAudio)} /></Sequence>
    </AbsoluteFill>
  );
};''')

# 03 平静：一条起伏的线。Lo lắng 那张波幅拉满，Bình tĩnh 那张收成直线
EPS["viet-zen-03-binhtinh"] = dict(
  comp="BinhTinh", no="03", name="平静",
  art="一条起伏的线：讲 Lo lắng 时波幅拉到最大，讲 Bình tĩnh 时收成直线 —— 平静不是没有波，是波小下来。",
  ink="#08131B", cream="#E8EFF3", dim="rgba(232,239,243,0.42)", accent="#8FC4DC",
  scrim="rgba(8,19,27,0.30)", border="rgba(143,196,220,0.55)",
  radial="radial-gradient(124% 70% at 50% 32%, rgba(28,62,84,0.10) 0%, rgba(14,34,48,0.26) 48%, rgba(8,19,27,0.76) 100%)",
  fog="rgba(143,196,220,0.09)",
  vgrad="linear-gradient(180deg, rgba(8,19,27,0.46) 0%, rgba(8,19,27,0.05) 20%, rgba(8,19,27,0.40) 44%, rgba(8,19,27,0.40) 58%, rgba(8,19,27,0.06) 76%, rgba(8,19,27,0.62) 100%)",
  device='''/** 装置：一条会起伏的线。`amp` 0 = 一条直线，1 = 波幅拉满 */
const Wave: React.FC<{ amp: number; frame: number; op: number }> = ({ amp, frame, op }) => {
  const W = 880, X0 = (1080 - W) / 2, Y = 1078;
  const pts: string[] = [];
  for (let i = 0; i <= 64; i++) {
    const u = i / 64;
    const env = Math.sin(u * Math.PI);                 // 两端收平，中间最开
    const y = 60 - Math.sin(u * 11 + frame / 12) * 46 * amp * env;
    pts.push(`${(u * W).toFixed(1)},${y.toFixed(1)}`);
  }
  return (
    <svg viewBox={`0 0 ${W} 120`} style={{ position: "absolute", left: X0, top: Y,
                                           width: W, height: 120, opacity: op }}>
      <path d={`M${pts.join("L")}`} fill="none" stroke="#8FC4DC"
            strokeWidth={2.4} strokeLinecap="round" />
    </svg>
  );
};''',
  card='''const WordCard: React.FC<{ w: Word; index: number; total: number; fps: number }> =
({ w, index, total, fps }) => {
  const f = useCurrentFrame(), n = Math.round(w.dur * fps);
  const p = fade(f, 0, 24, n - 20, n);
  const q = interpolate(f, [22, 50], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  // 波幅由这个词自己决定：担心＝最大，平静＝直线，其余居中
  const target = w.zh.indexOf("担心") >= 0 ? 1 : w.zh.indexOf("平静") >= 0 ? 0.04 : 0.42;
  const amp = interpolate(f, [0, 40], [0.42, target], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <Brand />
      <div style={{ position: "absolute", top: 236, width: "100%", textAlign: "center",
                    fontFamily: ZH_S, fontSize: 24, letterSpacing: 8, color: DIM, opacity: p }}>
        逐词拆解 {index + 1} / {total}
      </div>
      <div style={{ position: "absolute", top: 786, width: 960, left: 60, textAlign: "center",
                    fontFamily: VI, fontSize: 88, lineHeight: 1.3, color: ACCENT, opacity: p }}>
        {w.thai}
      </div>
      <div style={{ position: "absolute", top: 942, width: 960, left: 60, textAlign: "center",
                    fontFamily: ZH, fontSize: 52, lineHeight: 1.4, color: CREAM, opacity: q }}>
        {w.zh}
      </div>
      <Wave amp={amp} frame={f} op={p * 0.9} />
      <Sequence from={Math.round((w.zhAt - w.start) * fps)}><Audio src={staticFile(w.zhAudio)} /></Sequence>
      <Sequence from={Math.round((w.thAt - w.start) * fps)}><Audio src={staticFile(w.thAudio)} /></Sequence>
      <Sequence from={Math.round((w.thAt2 - w.start) * fps)}><Audio src={staticFile(w.thAudio)} /></Sequence>
    </AbsoluteFill>
  );
};''')

# 04 知足：天平。左盘"多"右盘"够"，每讲一个词摆一次，最后停平
EPS["viet-zen-04-hanhphuc"] = dict(
  comp="HanhPhuc", no="04", name="知足",
  art="天平：一根横梁，左盘装「多」右盘装「够」，每讲一个词摆一次，最后停平 —— 停平那一刻才是幸福。",
  ink="#0C1220", cream="#EFEADD", dim="rgba(239,234,221,0.42)", accent="#E3C98C",
  scrim="rgba(12,18,32,0.32)", border="rgba(227,201,140,0.55)",
  radial="radial-gradient(122% 70% at 50% 34%, rgba(34,46,86,0.12) 0%, rgba(20,28,52,0.28) 50%, rgba(12,18,32,0.76) 100%)",
  fog="rgba(227,201,140,0.08)",
  vgrad="linear-gradient(180deg, rgba(12,18,32,0.46) 0%, rgba(12,18,32,0.05) 20%, rgba(12,18,32,0.42) 44%, rgba(12,18,32,0.42) 58%, rgba(12,18,32,0.06) 76%, rgba(12,18,32,0.64) 100%)",
  device='''/** 装置：天平。`tilt` −1 左沉 / 0 停平 / +1 右沉 */
const Scale: React.FC<{ tilt: number; op: number }> = ({ tilt, op }) => {
  const cx = 540, cy = 1128, arm = 250, deg = tilt * 9;
  const pan = (side: number) => {
    const rad = (deg * Math.PI) / 180;
    const x = cx + side * arm * Math.cos(rad);
    const y = cy + side * arm * Math.sin(rad);
    return (
      <>
        <div style={{ position: "absolute", left: x - 0.5, top: y, width: 1, height: 34,
                      background: "rgba(227,201,140,0.5)" }} />
        <div style={{ position: "absolute", left: x - 44, top: y + 34, width: 88, height: 1,
                      background: "rgba(227,201,140,0.72)" }} />
      </>
    );
  };
  return (
    <div style={{ opacity: op }}>
      <div style={{ position: "absolute", left: cx - arm, top: cy - 1, width: arm * 2, height: 2,
                    background: "rgba(227,201,140,0.72)", transformOrigin: "50% 50%",
                    transform: `rotate(${deg.toFixed(2)}deg)` }} />
      <div style={{ position: "absolute", left: cx - 4, top: cy - 4, width: 8, height: 8,
                    borderRadius: 4, background: "#E3C98C" }} />
      <div style={{ position: "absolute", left: cx - 0.5, top: cy, width: 1, height: 120,
                    background: "rgba(227,201,140,0.34)" }} />
      {pan(-1)}{pan(1)}
    </div>
  );
};''',
  card='''const WordCard: React.FC<{ w: Word; index: number; total: number; fps: number }> =
({ w, index, total, fps }) => {
  const f = useCurrentFrame(), n = Math.round(w.dur * fps);
  const p = fade(f, 0, 24, n - 20, n);
  const q = interpolate(f, [22, 50], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  // 「多」让它彻底压向一边；最后一张收到停平
  const heavy = w.zh.indexOf("多") >= 0;
  const from = index % 2 === 0 ? -1 : 1;
  const to = index === total - 1 ? 0 : heavy ? 1 : from * 0.45;
  const tilt = interpolate(f, [8, 52], [from, to], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <Brand />
      <div style={{ position: "absolute", top: 236, width: "100%", textAlign: "center",
                    fontFamily: ZH_S, fontSize: 24, letterSpacing: 8, color: DIM, opacity: p }}>
        逐词拆解 {index + 1} / {total}
      </div>
      <div style={{ position: "absolute", top: 782, width: 960, left: 60, textAlign: "center",
                    fontFamily: VI, fontSize: 88, lineHeight: 1.3, color: ACCENT, opacity: p }}>
        {w.thai}
      </div>
      <div style={{ position: "absolute", top: 938, width: 960, left: 60, textAlign: "center",
                    fontFamily: ZH, fontSize: 52, lineHeight: 1.4, color: CREAM, opacity: q }}>
        {w.zh}
      </div>
      <Scale tilt={tilt} op={p * 0.9} />
      <Sequence from={Math.round((w.zhAt - w.start) * fps)}><Audio src={staticFile(w.zhAudio)} /></Sequence>
      <Sequence from={Math.round((w.thAt - w.start) * fps)}><Audio src={staticFile(w.thAudio)} /></Sequence>
      <Sequence from={Math.round((w.thAt2 - w.start) * fps)}><Audio src={staticFile(w.thAudio)} /></Sequence>
    </AbsoluteFill>
  );
};''')

# 05 重新开始：地平线上的光，每讲一个词升高一档
EPS["viet-zen-05-batdaulai"] = dict(
  comp="BatDauLai", no="05", name="重新开始",
  art="地平线上的光：一条地平线，每讲一个词线上的光带升高一档，到最后整条线亮起来 —— 天亮不是一下子的事。",
  ink="#0A1018", cream="#EDE8DC", dim="rgba(237,232,220,0.42)", accent="#E8C079",
  scrim="rgba(10,16,24,0.30)", border="rgba(232,192,121,0.55)",
  radial="radial-gradient(124% 70% at 50% 36%, rgba(40,44,64,0.10) 0%, rgba(20,26,40,0.26) 48%, rgba(10,16,24,0.76) 100%)",
  fog="rgba(232,192,121,0.08)",
  vgrad="linear-gradient(180deg, rgba(10,16,24,0.46) 0%, rgba(10,16,24,0.05) 20%, rgba(10,16,24,0.40) 44%, rgba(10,16,24,0.40) 58%, rgba(10,16,24,0.06) 76%, rgba(10,16,24,0.62) 100%)",
  device='''/** 装置：地平线上的光。`lit` 0→1，光带从线上一点点长出来 */
const Dawn: React.FC<{ lit: number; op: number }> = ({ lit, op }) => {
  const W = 880, X0 = (1080 - W) / 2, Y = 1096;
  return (
    <div style={{ opacity: op }}>
      <div style={{ position: "absolute", left: X0, top: Y, width: W, height: 1,
                    background: "rgba(237,232,220,0.22)" }} />
      <div style={{ position: "absolute", left: X0, top: Y - 54 * lit, width: W, height: 54 * lit,
                    background: `linear-gradient(180deg, rgba(232,192,121,0) 0%, rgba(232,192,121,${(0.34 * lit).toFixed(3)}) 100%)`,
                    filter: "blur(10px)" }} />
      <div style={{ position: "absolute", left: X0, top: Y - 1, width: W * lit, height: 2,
                    background: "#E8C079", boxShadow: `0 0 ${Math.round(22 * lit)}px #E8C079` }} />
    </div>
  );
};''',
  card='''const WordCard: React.FC<{ w: Word; index: number; total: number; fps: number }> =
({ w, index, total, fps }) => {
  const f = useCurrentFrame(), n = Math.round(w.dur * fps);
  const p = fade(f, 0, 24, n - 20, n);
  const q = interpolate(f, [22, 50], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  // 一档一档往上加，最后一张整条线亮满
  const a = index / total, b = (index + 1) / total;
  const lit = interpolate(f, [10, 54], [a, b], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <Brand />
      <div style={{ position: "absolute", top: 236, width: "100%", textAlign: "center",
                    fontFamily: ZH_S, fontSize: 24, letterSpacing: 8, color: DIM, opacity: p }}>
        逐词拆解 {index + 1} / {total}
      </div>
      <div style={{ position: "absolute", top: 790, width: 960, left: 60, textAlign: "center",
                    fontFamily: VI, fontSize: 88, lineHeight: 1.3, color: ACCENT, opacity: p }}>
        {w.thai}
      </div>
      <div style={{ position: "absolute", top: 946, width: 960, left: 60, textAlign: "center",
                    fontFamily: ZH, fontSize: 52, lineHeight: 1.4, color: CREAM, opacity: q }}>
        {w.zh}
      </div>
      <Dawn lit={lit} op={p} />
      <Sequence from={Math.round((w.zhAt - w.start) * fps)}><Audio src={staticFile(w.zhAudio)} /></Sequence>
      <Sequence from={Math.round((w.thAt - w.start) * fps)}><Audio src={staticFile(w.thAudio)} /></Sequence>
      <Sequence from={Math.round((w.thAt2 - w.start) * fps)}><Audio src={staticFile(w.thAudio)} /></Sequence>
    </AbsoluteFill>
  );
};''')

for pid, e in EPS.items():
    src = (CHASSIS
           .replace("__NO__", e["no"]).replace("__NAME__", e["name"]).replace("__ART__", e["art"])
           .replace("__INK__", e["ink"]).replace("__CREAM__", e["cream"]).replace("__DIM__", e["dim"])
           .replace("__ACCENT__", e["accent"]).replace("__SCRIM__", e["scrim"])
           .replace("__RADIAL__", e["radial"]).replace("__FOG__", e["fog"])
           .replace("__VGRAD__", e["vgrad"]).replace("__BORDER__", e["border"])
           .replace("__DEVICE__", e["device"]).replace("__CARD__", e["card"])
           .replace("__COMP__", e["comp"]))
    out = REPO / "projects" / pid / "composition" / f'{e["comp"]}.tsx'
    out.write_text(src, encoding="utf-8")
    print("✓", out.relative_to(REPO))
