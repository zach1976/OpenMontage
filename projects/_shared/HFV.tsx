import React from "react";
import { loadFonts, ZH_TITLE, ZH_UI } from "./CjkFonts";
import { AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile,
         useCurrentFrame } from "remotion";

// ---------------------------------------------------------------------------
// 越南语千词 · 高频词（老版式重做批）—— 16 个已发布的词，同一版式，逐集换配色 + 配图
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

loadFonts([["VietBold", "BeVietnamPro-Bold.ttf"], ["VietSemi", "BeVietnamPro-SemiBold.ttf"],
           ["SerifSC", "NotoSerifSC-Bold.otf"]]);

const ZH = ZH_TITLE, ZH_S = ZH_UI;
const TH = "VietBold, sans-serif", TH_R = "VietSemi, sans-serif";

// 配色由 props.palette 注入 —— **每集不同**（用户 2026-08-30 指令）。
// 版式刻意不变：高频词是格式化系列，老版 20 支同一张脸正是它被认出来的原因。
const CREAM = "#EDE9DE";
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

const ROW_H = 196, TABLE_TOP = 748, TABLE_L = 76, TABLE_W = 928;

/** 底：本集专属底色，四角压暗；配图压在下端当纹理（不是主角） */
const Backdrop: React.FC<{ photo?: string; ink: string; ink2: string; accent: string }> =
({ photo, ink, ink2, accent }) => {
  const f = useCurrentFrame();
  const d = (p: number, a: number) => Math.sin(f / 280 + p) * a;
  return (
    <AbsoluteFill style={{ backgroundColor: ink }}>
      <AbsoluteFill style={{ background:
        `radial-gradient(126% 74% at 50% 30%, ${ink2} 0%, ${hexA(ink2, 0.55)} 52%, ${ink} 100%)` }} />
      {photo ? (
        <div style={{ position: "absolute", left: 0, top: 1180, width: 1080, height: 740,
                      overflow: "hidden" }}>
          <Img src={staticFile(photo)} style={{ width: "100%", height: "100%",
                                                objectFit: "cover", opacity: 0.30 }} />
          {/* 上缘化开，别在画面中间切出一条硬边；整块再压一道本集底色 */}
          <AbsoluteFill style={{ background:
            `linear-gradient(180deg, ${ink} 0%, ${hexA(ink, 0.62)} 26%, ${hexA(ink, 0.52)} 62%, ${hexA(ink, 0.86)} 100%)` }} />
        </div>
      ) : null}
      {[[300, 620, 520, 0], [800, 1240, 560, 2.4]].map(([x, y, r, ph], i) => (
        <div key={i} style={{ position: "absolute", left: x + d(ph, 20) - r / 2,
                              top: y + d(ph + 1, 12) - r / 2, width: r, height: r,
                              borderRadius: "50%", filter: "blur(96px)",
                              background: hexA(accent, 0.055) }} />
      ))}
      <AbsoluteFill style={{ background:
        "radial-gradient(80% 58% at 50% 46%, rgba(0,0,0,0) 44%, rgba(0,0,0,0.42) 100%)" }} />
    </AbsoluteFill>
  );
};

const Brand: React.FC<{ badge: string }> = ({ badge }) => (
  <>
    <div style={{ position: "absolute", top: 96, width: "100%", textAlign: "center",
                  fontFamily: ZH_S, fontSize: 26, letterSpacing: 8, color: DIM }}>
      越南语千词 · 每天一个高频词
    </div>
    <div style={{ position: "absolute", top: 150, width: "100%", textAlign: "center",
                  fontFamily: ZH_S, fontSize: 24, letterSpacing: 9, color: GOLD_D }}>
      {badge}
    </div>
  </>
);

/** 词头：แล้ว 一直挂在上面不动 —— 12 行讲的都是它 */
const WordHead: React.FC<{ w: any; op?: number }> = ({ w, op = 1 }) => (
  <div style={{ opacity: op }}>
    <div style={{ position: "absolute", top: 232, width: "100%", textAlign: "center",
                  fontFamily: TH, fontSize: 100, lineHeight: 1.34, color: GOLD }}>
      {w.th}
    </div>
    <div style={{ position: "absolute", top: 388, width: "100%", textAlign: "center",
                  fontFamily: ZH, fontSize: 34, letterSpacing: 4, color: DIM }}>
      谐音「{w.xie}」
    </div>
    <div style={{ position: "absolute", top: 444, width: "100%", textAlign: "center",
                  fontFamily: ZH, fontSize: 42, letterSpacing: 2, color: CREAM }}>
      {w.zh}
    </div>
  </div>
);

/**
 * 一行。三种状态：
 *   0 未讲 —— 暗，只见轮廓
 *   1 正在讲 —— 金边亮起，泰语放大
 *   2 讲过了 —— **打勾 + 沉下去**，不还原（这就是 แล้ว）
 */
const TableRow: React.FC<{ r: Row; i: number; state: number; lit: number }> =
({ r, i, state, lit }) => {
  const y = TABLE_TOP + i * ROW_H;
  const on = state === 1, done = state === 2;
  const bg = on ? `rgba(232,182,92,${(0.10 + 0.06 * lit).toFixed(3)})`
                : done ? "rgba(237,233,222,0.028)" : "rgba(237,233,222,0.045)";
  const bd = on ? `rgba(232,182,92,${(0.55 + 0.35 * lit).toFixed(3)})`
                : done ? "rgba(232,182,92,0.16)" : "rgba(237,233,222,0.10)";
  const fade = done ? 0.44 : on ? 1 : 0.60;
  return (
    <div style={{ position: "absolute", left: TABLE_L, top: y, width: TABLE_W, height: ROW_H - 26,
                  borderRadius: 16, background: bg, border: `1.5px solid ${bd}`,
                  display: "flex", alignItems: "center", padding: "0 22px", opacity: fade }}>
      {/* 汉字 icon —— 老版最好用的那个锚点 */}
      <div style={{ width: 68, height: 68, borderRadius: 13, flexShrink: 0,
                    border: `1.5px solid ${on ? GOLD : "rgba(237,233,222,0.22)"}`,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontFamily: ZH, fontSize: 36, color: on ? GOLD : CREAM }}>
        {r.icon}
      </div>
      <div style={{ width: 190, marginLeft: 18, fontFamily: ZH, fontSize: 38,
                    color: CREAM, whiteSpace: "nowrap" }}>{r.zh}</div>
      {/* 泰语按词分开显示（用户 2026-08-30 指令）。**只是显示分词，配音仍用连写的 r.th** ——
          泰语 TTS 遇空格会断读。目标词 แล้ว 满色，其余部分压一档，
          于是「ไป แล้ว」和「แล้ว ไป」的词序差别一眼就能看出来。 */}
      <div style={{ flex: 1, display: "flex", alignItems: "baseline", gap: on ? 20 : 17,
                    fontFamily: TH, fontSize: on ? 46 : 41, lineHeight: 1.45,
                    whiteSpace: "nowrap" }}>
        {r.thParts.map((seg, k) => (
          <span key={k} style={{ color: GOLD, opacity: seg === "แล้ว" ? 1 : 0.72 }}>{seg}</span>
        ))}
      </div>
      {/* 最后一列是**中文谐音**（用户 2026-08-30 指令，不用音标）。
          按泰语音节一一对应，一个音节一个字，不超 3 字 —— 老版「毕巴度」那种
          乱拆音节的写法才是读不出来的原因，谐音本身没错。 */}
      <div style={{ width: 168, textAlign: "right", fontFamily: ZH, fontSize: 34,
                    color: on ? CREAM : DIM, letterSpacing: 1, whiteSpace: "nowrap" }}>{r.xie}</div>
      {/* 讲完就打勾 —— 老版扫过还原，这一版扫过结掉 */}
      <div style={{ width: 32, textAlign: "right", fontFamily: ZH_S, fontSize: 30,
                    color: GOLD, opacity: done ? 0.9 : 0 }}>✓</div>
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
                    fontFamily: TH, fontSize: 168, lineHeight: 1.34, color: GOLD }}>{w.th}</div>
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
      <WordHead w={w} op={0.92} />
      <div style={{ position: "absolute", top: 566, width: "100%", textAlign: "center",
                    fontFamily: ZH, fontSize: 44, letterSpacing: 4, color: GOLD }}>
        {p.title}
      </div>
      {p.rows.map((r, i) => {
        // 连读那一段：四行一起亮，观众跟着念
        const state = echoOn ? 1 : tSec >= r.start + r.dur ? 2 : tSec >= r.start ? 1 : 0;
        const r0 = Math.round((r.start - p.start) * fps);
        const lit = echoOn ? 1
          : state === 1 ? interpolate(f, [r0, r0 + 10], [0, 1],
                                     { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 0;
        return <TableRow key={r.id} r={r} i={i} state={state} lit={lit} />;
      })}
      <div style={{ position: "absolute", top: 1568, width: "100%", textAlign: "center",
                    fontFamily: ZH_S, fontSize: 30, letterSpacing: 6, color: GOLD,
                    opacity: echoOn ? 0.95 : 0 }}>
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
                    fontFamily: ZH, fontSize: 58, letterSpacing: 8, color: GOLD, opacity: p }}>越南语千词</div>
      <div style={{ position: "absolute", top: 1042, width: "100%", textAlign: "center",
                    fontFamily: ZH_S, fontSize: 32, letterSpacing: 3, color: DIM, opacity: p }}>
        在越南生活，够用了
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
