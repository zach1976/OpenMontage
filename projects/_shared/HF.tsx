import React from "react";
import { loadFonts, ZH_TITLE, ZH_UI } from "./CjkFonts";
import { AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile,
         useCurrentFrame } from "remotion";

// ---------------------------------------------------------------------------
// 泰语千词 · 高频词（老版式重做批）—— 16 个已发布的词，同一版式，逐集换配色 + 配图
//
// 这一集不从 hf-01…05 那套（一集 5 张大留白词组卡）延续，而是**回到 2026-05-12
// 那一代**（`lang1000/.../make_thai_*_video.py`，已发 20 支）重做。那一代成在四件事，
// 这里全部保留：
//   1. 一条给 **12 个真用法** —— 信息密度，观众觉得赚到
//   2. **表格式版面**，静音刷也能扫读
//   3. **逐行推进**，跟得住
//   4. **汉字 icon 当锚点**，一眼知道这一行讲什么
// 去掉老版三个毛病：谐音（读不出也不可靠）、烧屏 hashtag、12 条平铺流水账。
//
// 变体点（这一集的视觉语言，从 แล้ว 自己的意思长出来）：
// **แล้ว 是完成态，所以讲过的行不还原，而是打上勾、沉下去留在表里。**
// 老版是高亮扫过就复原；这一版是扫过就"结掉"。到每组末尾四行全部打勾，
// 再连读一遍 —— 画面自己在演这个词。
//
// 配色跟已有四集刻意错开：01 炭墨+橙 / 02 墨蓝+青柠 / 03 暖褐+砖红 / 05 暗蓝+天蓝，
// 这一集是**深松绿 + 琥珀金**（金是老版的身份色，底色换掉）。
// ---------------------------------------------------------------------------

loadFonts([["ThaiBold", "Sarabun-Bold.ttf"], ["ThaiReg", "Sarabun-Regular.ttf"],
           ["SerifSC", "NotoSerifSC-Bold.otf"]]);

const ZH = ZH_TITLE, ZH_S = ZH_UI;
const TH = "ThaiBold, sans-serif", TH_R = "ThaiReg, sans-serif";

// 配色由 props.palette 注入 —— **每集不同**（用户 2026-08-30 指令）。
// 版式刻意不变：高频词是格式化系列，老版 20 支同一张脸正是它被认出来的原因。
const CREAM = "#F6F1E6";
const BRAND_LINE = "泰语千词 · 每天一个高频词";
const DIM = "rgba(237,233,222,0.44)";
let INK = "#0A1613", INK_2 = "#12241E", GOLD = "#E8B65C", GOLD_D = "rgba(232,182,92,0.30)";
const hexA = (hex: string, a: number) => {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
};

export type Row = { id: string; page: number; icon: string; zh: string; th: string;
                    thParts: string[]; rom: string; xie: string;
                    start: number; dur: number;
                    zhAudio: string; thAudio: string; zhAt: number; thAt: number };
export type Page = { index: number; title: string; start: number; dur: number; rows: Row[];
                     titleAudio: string; titleAt: number;
                     echoAudio: string; echoAt: number; echoDur: number };
export type Palette = { ink: string; ink2: string; accent: string };
export type Props = {
  word: { th: string; rom: string; zh: string; xie: string };
  palette: Palette; photo?: string;
  badge: string; poster: { t1: string; t2: string };
  hook: any; pages: Page[]; outro: any;
  bgm: { src: string; gain: number }; speak: number[][]; fps: number;
};

const ROW_H = 160, TABLE_TOP = 690, TABLE_L = 56, TABLE_W = 968;
// ── 2026-11 美化（ChatGPT 稿）：奶油气泡词头 + 胶囊/缎带 + 半透明行条；配图在表格下方正常显示。
const INK_TXT = "#2A2140";
const sameWord = (seg: string, th: string) => seg.trim().toLowerCase() === th.trim().toLowerCase();

/** 底：主色晕染到本集底色；配图压在表格下方，能看出是什么，但上缘化进底色 */
const Backdrop: React.FC<{ photo?: string; ink: string; ink2: string; accent: string }> =
({ photo, ink, ink2, accent }) => (
  <AbsoluteFill style={{ backgroundColor: ink }}>
    <AbsoluteFill style={{ background:
      `linear-gradient(170deg, ${hexA(accent, 0.30)} 0%, ${ink2} 34%, ${ink} 78%)` }} />
    <div style={{ position: "absolute", left: 140, top: 150, width: 800, height: 800, borderRadius: "50%",
                  background: `radial-gradient(circle, ${hexA(accent, 0.16)} 0%, transparent 62%)` }} />
    {photo ? (
      <div style={{ position: "absolute", left: 0, top: 1300, width: 1080, height: 620, overflow: "hidden",
                    WebkitMaskImage: "linear-gradient(180deg, transparent 0%, #000 30%, #000 80%, transparent 100%)" }}>
        <Img src={staticFile(photo)} style={{ width: "100%", height: "100%", objectFit: "cover", opacity: 0.9,
                                              filter: "saturate(1.15) brightness(0.92)" }} />
      </div>
    ) : null}
  </AbsoluteFill>
);

const Brand: React.FC<{ badge: string }> = () => (
  <div style={{ position: "absolute", top: 60, left: 48, height: 70, padding: "0 28px", borderRadius: 35,
                background: "#FFF7F4", boxShadow: "0 8px 20px rgba(16,24,39,.18)", display: "flex",
                alignItems: "center", fontFamily: ZH_S, fontSize: 30, fontWeight: 700, color: INK_TXT, letterSpacing: 1 }}>
    {BRAND_LINE}
  </div>
);

/** 词头：奶油气泡里的目标词 + 谐音胶囊 + 中文胶囊（期号不上屏 —— 每条视频独立） */
const WordHead: React.FC<{ w: any; op?: number }> = ({ w, op = 1 }) => {
  const latin = !/[฀-๿]/.test(w.th);
  return (
    <div style={{ opacity: op }}>
      <div style={{ position: "absolute", top: 150, width: "100%", display: "flex", justifyContent: "center" }}>
        <div style={{ padding: latin ? "0 64px" : "0 56px", height: 210, borderRadius: 105,
                      background: "radial-gradient(circle at 40% 30%, #FFFDF6, #FFF1D6)",
                      border: `5px solid ${GOLD}`, boxShadow: `0 16px 40px rgba(0,0,0,.28), 0 0 0 10px ${hexA(GOLD, 0.16)}`,
                      display: "flex", alignItems: "center", justifyContent: "center",
                      fontFamily: TH, fontSize: latin ? 120 : 132, lineHeight: 1.5, color: INK_TXT }}>{w.th}</div>
      </div>
      <div style={{ position: "absolute", top: 384, width: "100%", display: "flex", justifyContent: "center", gap: 18 }}>
        <div style={{ height: 76, padding: "0 34px", borderRadius: 38, background: "linear-gradient(90deg, #EFE2F4, #E2D2EE)",
                      display: "flex", alignItems: "center", fontFamily: ZH, fontSize: 38, color: "#4C3F66" }}>谐音「{w.xie}」</div>
        <div style={{ height: 76, padding: "0 40px", borderRadius: 38, background: "linear-gradient(180deg, #FFF9F0, #FFEBC8)",
                      border: `2px solid ${GOLD}`, display: "flex", alignItems: "center", fontFamily: ZH, fontSize: 44, color: INK_TXT }}>{w.zh}</div>
      </div>
    </div>
  );
};

/** 本组标题：金色缎带 */
const Ribbon: React.FC<{ text: string }> = ({ text }) => (
  <div style={{ position: "absolute", top: 520, width: "100%", display: "flex", justifyContent: "center" }}>
    <div style={{ position: "relative", height: 100, padding: "0 70px", display: "flex", alignItems: "center",
                  background: `linear-gradient(180deg, #FFE7A3, ${GOLD})`, clipPath: "polygon(0 0, 100% 0, 96% 50%, 100% 100%, 0 100%, 4% 50%)",
                  fontFamily: ZH, fontSize: 52, letterSpacing: 4, color: INK_TXT }}>{text}</div>
  </div>
);

/**
 * 一行，三种状态一眼可分：
 *   0 未讲 —— 半透明条，字稍淡
 *   1 正在讲 —— 奶油底高亮 + 主色描边发光，icon 变实色
 *   2 讲过了 —— 保持可读、打勾（不再压暗到看不清）
 */
const TableRow: React.FC<{ r: Row; i: number; state: number; lit: number; w: any }> =
({ r, i, state, lit, w }) => {
  const y = TABLE_TOP + i * ROW_H;
  const on = state === 1, done = state === 2;
  const txt = on ? INK_TXT : CREAM;
  return (
    <div style={{ position: "absolute", left: on ? TABLE_L - 10 : TABLE_L, top: y, width: on ? TABLE_W + 20 : TABLE_W,
                  height: ROW_H - 22, borderRadius: 30,
                  background: on ? "linear-gradient(180deg, #FFFAF0, #FFF0D6)" : `rgba(255,255,255,${done ? 0.10 : 0.07})`,
                  border: on ? `3px solid ${GOLD}` : "1.5px solid rgba(255,255,255,.20)",
                  boxShadow: on ? `0 0 ${26 + 14 * lit}px ${hexA(GOLD, 0.45)}, 0 14px 30px rgba(0,0,0,.25)` : "none",
                  display: "flex", alignItems: "center", padding: "0 26px", opacity: state === 0 ? 0.78 : 1 }}>
      <div style={{ width: 76, height: 76, borderRadius: 18, flexShrink: 0,
                    background: on ? GOLD : "transparent", border: on ? "none" : "2px solid rgba(255,255,255,.55)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontFamily: ZH, fontSize: 42, color: on ? "#FFFFFF" : CREAM }}>{r.icon}</div>
      <div style={{ width: 190, marginLeft: 22, fontFamily: ZH, fontSize: 44, color: txt, whiteSpace: "nowrap" }}>{r.zh}</div>
      <div style={{ width: 2, height: 54, background: on ? hexA(GOLD, 0.6) : "rgba(255,255,255,.25)", marginRight: 26 }} />
      <div style={{ flex: 1, display: "flex", alignItems: "baseline", gap: 18, fontFamily: TH,
                    fontSize: on ? 64 : 58, lineHeight: 1.5, whiteSpace: "nowrap" }}>
        {r.thParts.map((seg, k) => (
          <span key={k} style={{ color: sameWord(seg, w.th) ? GOLD : (on ? INK_TXT : CREAM),
                                 opacity: sameWord(seg, w.th) ? 1 : (on ? 0.85 : 0.72) }}>{seg}</span>
        ))}
      </div>
      <div style={{ minWidth: 120, height: on ? 64 : "auto", padding: on ? "0 22px" : 0, borderRadius: 32,
                    border: on ? `2px solid ${hexA(GOLD, 0.7)}` : "none", display: "flex", alignItems: "center",
                    justifyContent: "flex-end", fontFamily: ZH, fontSize: 36, color: txt, whiteSpace: "nowrap" }}>{r.xie}</div>
      <div style={{ width: 44, textAlign: "right", fontFamily: ZH_S, fontSize: 40, fontWeight: 700,
                    color: GOLD, opacity: done ? 1 : 0 }}>✓</div>
    </div>
  );
};

const Hook: React.FC<{ h: any; w: any; badge: string; poster: any; fps: number }> =
({ h, w, badge, poster, fps }) => {
  const f = useCurrentFrame(), n = Math.round(h.dur * fps);
  // 封面 = 第一帧，起手即成品，只在末尾淡出
  const out = interpolate(f, [n - 20, n], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ opacity: out }}>
      <Brand badge={badge} />
      <div style={{ position: "absolute", top: 296, width: "100%", textAlign: "center",
                    fontFamily: TH, fontSize: 200, lineHeight: 1.34, color: GOLD }}>{w.th}</div>
      <div style={{ position: "absolute", top: 552, width: "100%", textAlign: "center",
                    fontFamily: ZH, fontSize: 40, letterSpacing: 4, color: DIM }}>谐音「{w.xie}」</div>
      <div style={{ position: "absolute", left: 290, top: 656, width: 500, height: 1,
                    background: GOLD_D }} />
      {/* 核心带 660–1260：两行等大的点题 */}
      <div style={{ position: "absolute", top: 716, width: 960, left: 60, textAlign: "center",
                    fontFamily: ZH, fontSize: 90, lineHeight: 1.52, color: CREAM }}>
        {poster.t1}<br />{poster.t2}
      </div>
      <div style={{ position: "absolute", top: 996, width: "100%", textAlign: "center",
                    fontFamily: ZH, fontSize: 50, letterSpacing: 3, color: GOLD }}>
        1 个词 · 12 种用法
      </div>
      <div style={{ position: "absolute", top: 1090, width: "100%", textAlign: "center",
                    fontFamily: ZH_S, fontSize: 32, letterSpacing: 2, color: DIM }}>
        {w.zh}
      </div>
      {h.audio.map((a: any, i: number) => (
        <Sequence key={i} from={Math.round(a.at * fps)}>
          <Audio src={staticFile(a.src)} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

const PageScene: React.FC<{ p: Page; w: any; badge: string; fps: number }> =
({ p, w, badge, fps }) => {
  const f = useCurrentFrame(), n = Math.round(p.dur * fps);
  const enter = interpolate(f, [0, 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const leave = interpolate(f, [n - 14, n], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const op = enter * leave;
  const tSec = p.start + f / fps;
  const echoOn = tSec >= p.echoAt - 0.15;
  return (
    <AbsoluteFill style={{ opacity: op }}>
      <Brand badge={badge} />
      <WordHead w={w} />
      <Ribbon text={p.title} />
      {p.rows.map((r, i) => {
        // 连读那一段：四行一起亮，观众跟着念
        const state = echoOn ? 1 : tSec >= r.start + r.dur ? 2 : tSec >= r.start ? 1 : 0;
        const r0 = Math.round((r.start - p.start) * fps);
        const lit = echoOn ? 1
          : state === 1 ? interpolate(f, [r0, r0 + 10], [0, 1],
                                     { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 0;
        return <TableRow key={r.id} r={r} i={i} state={state} lit={lit} w={w} />;
      })}
      <div style={{ position: "absolute", top: 1350, width: "100%", textAlign: "center",
                    fontFamily: ZH, fontSize: 40, letterSpacing: 6, color: "#FFF7E6",
                    textShadow: "0 3px 12px rgba(0,0,0,.6)", opacity: echoOn ? 1 : 0 }}>
        跟着念一遍
      </div>
      {/* 分组标题的配音 —— 第一版漏挂了，校验器逐段量出来的（比垫乐高不出 6dB 就判没响） */}
      <Sequence from={Math.round((p.titleAt - p.start) * fps)}>
        <Audio src={staticFile(p.titleAudio)} />
      </Sequence>
      {p.rows.map((r) => (
        <React.Fragment key={r.id}>
          <Sequence from={Math.round((r.zhAt - p.start) * fps)}>
            <Audio src={staticFile(r.zhAudio)} />
          </Sequence>
          <Sequence from={Math.round((r.thAt - p.start) * fps)}>
            <Audio src={staticFile(r.thAudio)} />
          </Sequence>
        </React.Fragment>
      ))}
      <Sequence from={Math.round((p.echoAt - p.start) * fps)}>
        <Audio src={staticFile(p.echoAudio)} />
      </Sequence>
    </AbsoluteFill>
  );
};

const Outro: React.FC<{ o: any; fps: number }> = ({ o, fps }) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [0, 26], [0, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", top: 720, width: "100%", display: "flex",
                    justifyContent: "center", opacity: p }}>
        <div style={{ width: 176, height: 176, borderRadius: 40, overflow: "hidden",
                      border: `2px solid ${hexA(GOLD, 0.55)}` }}>
          <Img src={staticFile("app/app_icon.png")} style={{ width: "100%", height: "100%" }} />
        </div>
      </div>
      <div style={{ position: "absolute", top: 952, width: "100%", textAlign: "center",
                    fontFamily: ZH, fontSize: 58, letterSpacing: 8, color: GOLD, opacity: p }}>泰语千词</div>
      <div style={{ position: "absolute", top: 1042, width: "100%", textAlign: "center",
                    fontFamily: ZH_S, fontSize: 32, letterSpacing: 3, color: DIM, opacity: p }}>
        在泰国生活，够用了
      </div>
      <Sequence from={Math.round((o.audioAt - o.start) * fps)}>
        <Audio src={staticFile(o.audio)} />
      </Sequence>
    </AbsoluteFill>
  );
};

export const HF: React.FC<Props> = ({ word, palette, photo, badge, poster,
                                     hook, pages, outro, bgm, speak, fps }) => {
  INK = palette.ink; INK_2 = palette.ink2;
  GOLD = palette.accent; GOLD_D = hexA(palette.accent, 0.30);
  const f = (s: number) => Math.round(s * fps);
  const duck = (frame: number) => {
    const t = frame / fps;
    return speak.some(([a, b]) => t >= a - 0.2 && t <= b + 0.3) ? bgm.gain * 0.5 : bgm.gain;
  };
  return (
    <AbsoluteFill style={{ backgroundColor: INK }}>
      <Backdrop photo={photo} ink={palette.ink} ink2={palette.ink2} accent={palette.accent} />
      <Audio src={staticFile(bgm.src)} volume={duck} />
      <Sequence from={0} durationInFrames={f(hook.dur)}>
        <Hook h={hook} w={word} badge={badge} poster={poster} fps={fps} />
      </Sequence>
      {pages.map((p) => (
        <Sequence key={p.index} from={f(p.start)} durationInFrames={f(p.dur)}>
          <PageScene p={p} w={word} badge={badge} fps={fps} />
        </Sequence>
      ))}
      <Sequence from={f(outro.start)} durationInFrames={f(outro.dur)}>
        <Outro o={outro} fps={fps} />
      </Sequence>
    </AbsoluteFill>
  );
};
