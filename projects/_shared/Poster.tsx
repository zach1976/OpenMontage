import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { ZH_TITLE, ZH_UI } from "./CjkFonts";

// ═══════════════════════════════════════════════════════════════════════════
// 封面海报组件库 —— 引擎知识，不是创意组件，所以 12 集共用同一份拷贝。
// 每集的「创意」落在传进来的 palette / bgVariant / ornament / plaque 形状上。
//
// 版式主张（2026-08-27 用户给的参考图）：**中文是主角**。
//   上行铺垫（小） → 下行点题（最大、最亮） → 描金匾里的副标题
//   外文词表和脚注放核心带外（y>1260），横屏封面裁掉也不影响理解。
//
// 核心带 y 660–1260：t1 / t2 / 匾 必须整个落在里面。
// ═══════════════════════════════════════════════════════════════════════════

// 注：下面各组件仍保留 `zh` 这个 prop 只为不改 13 处调用；
// 真正生效的是 CjkFonts 里的 ZH_TITLE / ZH_UI —— 排版分工统一在那里定。

export type Palette = {
  deep: string;      // 底色最暗处
  mid: string;       // 底色主调
  glow: string;      // 光源色
  g1: string; g2: string; g3: string; g4: string;  // 金字渐变四档（上→下）
  stroke: string;    // 金字描边（暗色，做出立体边）
  halo: string;      // 金字外发光
  plaqueFill: string;
  plaqueInk: string;
  line: string;      // 细线 / 纹样色
  soft: string;      // 弱化文字色
};

/** 朱漆描金（越南语千词的默认底） */
export const LACQUER_GOLD: Palette = {
  deep: "#3D0B08", mid: "#9E1F18", glow: "#FF6A3D",
  g1: "#FFF2CE", g2: "#FFD97E", g3: "#EFA829", g4: "#FFC85E",
  stroke: "#5A2410", halo: "rgba(255,168,60,0.62)",
  plaqueFill: "#EBD5A4", plaqueInk: "#7A1F14",
  line: "rgba(224,198,156,0.75)", soft: "rgba(245,225,190,0.72)",
};

// ── 背景 ──────────────────────────────────────────────────────────────────

export const PosterBg: React.FC<{
  p: Palette;
  /** 保留参数只为兼容各集的调用；现在只影响底色的明暗与重心，不再有光源 */
  variant?: "rays" | "halo" | "night" | "paper";
  sun?: [string, string];
}> = ({ p, variant = "rays" }) => {
  // 不放光源。早先用锥形渐变做光束、再在光源处补一团亮核 ——
  // 每张封面顶上都挂一个刺眼的光斑，喧宾夺主，用户直接叫停。
  // 现在只留**均匀的中心渐变 + 四角压暗**：有纵深，但没有那个"太阳"。
  if (variant === "paper") {
    return (
      <AbsoluteFill>
        <AbsoluteFill style={{ backgroundColor: p.plaqueFill }} />
        <AbsoluteFill style={{ background:
          `radial-gradient(150% 100% at 50% 50%, rgba(255,255,255,0.30) 0%, rgba(255,255,255,0) 70%)` }} />
      </AbsoluteFill>
    );
  }
  const stops =
    variant === "night"
      ? `${p.mid} 0%, ${p.deep} 62%, #050302 100%`
      : `${p.mid} 0%, ${p.mid} 18%, ${p.deep} 74%, #120402 100%`;
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ background: `radial-gradient(148% 104% at 50% 46%, ${stops})` }} />
      {/* 四角压暗：把注意力收回中间。这是唯一的明暗手段 */}
      <AbsoluteFill style={{ background:
        `radial-gradient(84% 62% at 50% 48%, rgba(0,0,0,0) 42%, rgba(0,0,0,0.40) 100%)` }} />
    </AbsoluteFill>
  );
};

/** 飘落的花瓣：瓣形（一头尖），不是米粒。数量克制，只做点缀。 */
export const Petals: React.FC<{ p: Palette }> = ({ p }) => {
  const spots: [number, number, number, number, number][] = [
    [92, 236, 46, -22, 0.34], [236, 452, 32, 34, 0.26], [936, 286, 40, 14, 0.30],
    [858, 548, 26, -46, 0.22], [124, 1548, 44, 26, 0.28], [966, 1642, 34, -16, 0.24],
    [612, 1486, 28, 48, 0.20],
  ];
  return (
    <>
      {spots.map(([x, y, r, a, o], i) => (
        <svg key={i} width={r} height={r} viewBox="0 0 32 32"
             style={{ position: "absolute", left: x, top: y, opacity: o,
                      transform: `rotate(${a}deg)` }}>
          <path d="M16 1 C24 9 27 18 16 31 C5 18 8 9 16 1 Z"
                fill={p.g2} />
        </svg>
      ))}
    </>
  );
};

/** 团花：十二瓣宝相花，垫在标题后面当底纹。参考图那种「满」是靠纹样撑的，不是靠空白。 */
export const Medallion: React.FC<{ p: Palette; cx?: number; cy?: number; r?: number; opacity?: number }> =
({ p, cx = 540, cy = 930, r = 560, opacity = 0.045 }) => (
  <svg width={r * 2} height={r * 2} viewBox="-200 -200 400 400"
       style={{ position: "absolute", left: cx - r, top: cy - r, opacity }}>
    {Array.from({ length: 12 }).map((_, i) => (
      <ellipse key={i} cx="0" cy="-118" rx="34" ry="78" fill={p.g2}
               transform={`rotate(${i * 30})`} />
    ))}
    {Array.from({ length: 12 }).map((_, i) => (
      <ellipse key={`b${i}`} cx="0" cy="-62" rx="22" ry="48" fill={p.g1}
               transform={`rotate(${i * 30 + 15})`} />
    ))}
    <circle cx="0" cy="0" r="26" fill="none" stroke={p.g2} strokeWidth="6" />
    <circle cx="0" cy="0" r="176" fill="none" stroke={p.g2} strokeWidth="2" />
  </svg>
);

/**
 * 底景实拍：把这一集的图压进画幅下端，顶上用底色渐隐接住 ——
 * 参考图的下半幅是荷花和帆船，我们没有插画素材，但有真实的配图。
 */
export const PhotoFoot: React.FC<{ p: Palette; photo: string; top?: number; focus?: string }> =
({ p, photo, top = 1430, focus = "center 40%" }) => (
  <div style={{ position: "absolute", left: 0, top, width: 1080, height: 1920 - top, overflow: "hidden" }}>
    <Img src={staticFile(photo)}
         style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: focus }} />
    <div style={{ position: "absolute", inset: 0, background:
      `linear-gradient(180deg, ${p.deep} 0%, ${p.deep}F2 9%, ${p.deep}B0 26%, ${p.deep}70 52%, ${p.deep}A8 100%)` }} />
    <div style={{ position: "absolute", inset: 0, background:
      `radial-gradient(80% 60% at 50% 40%, rgba(0,0,0,0) 30%, rgba(0,0,0,0.45) 100%)` }} />
  </div>
);

/**
 * 巨大的单字底纹。高频词系列用它替掉团花 —— 底纹就是这一集要教的那个词，
 * 纹样从内容里长出来，而不是外借一朵花。
 */
export const Glyph: React.FC<{ p: Palette; text: string; cy?: number; size?: number; opacity?: number; font?: string }> =
({ p, text, cy = 930, size = 720, opacity = 0.09, font }) => (
  <div style={{ position: "absolute", left: 0, top: cy - size * 0.62, width: 1080,
                textAlign: "center", fontFamily: font ?? "ThaiBold, sans-serif",
                fontSize: size, lineHeight: 1.24, color: p.g2, opacity }}>
    {text}
  </div>
);

/** 底部山水：三层剪影 + 水面反光。没有实拍时用它把下三分之一填住。 */
export const Landscape: React.FC<{ p: Palette; top?: number }> = ({ p, top = 1430 }) => (
  <svg width="1080" height={1920 - top} viewBox={`0 0 1080 ${1920 - top}`}
       style={{ position: "absolute", left: 0, top }}>
    <path d={`M0 210 C120 150 210 176 300 132 C398 84 470 128 560 106 C660 82 720 130 810 112 ` +
             `C900 94 990 140 1080 116 L1080 ${1920 - top} L0 ${1920 - top} Z`}
          fill={p.mid} opacity="0.45" />
    <path d={`M0 268 C140 226 236 252 340 218 C452 182 520 220 620 204 C720 188 800 226 900 210 ` +
             `C980 197 1030 216 1080 206 L1080 ${1920 - top} L0 ${1920 - top} Z`}
          fill={p.deep} opacity="0.72" />
    {[0, 1, 2].map((k) => (
      <path key={k} d={`M${-40 + k * 24} ${332 + k * 26} q 90 -18 180 0 t 180 0 t 180 0 t 180 0 t 180 0 t 180 0`}
            fill="none" stroke={p.g2} strokeWidth="2.4" opacity={0.30 - k * 0.07} />
    ))}
  </svg>
);

/** 四角回纹：中式版口的角花，四角各一，把版面框住 */
export const CornerFrets: React.FC<{ p: Palette; inset?: number; size?: number }> = ({ p, inset = 34, size = 116 }) => {
  const d = "M2 2 H114 M2 2 V114 M22 22 H94 M22 22 V94 M42 42 H74 M42 42 V74";
  const at: [number, number, string][] = [
    [inset, inset, "none"], [1080 - inset - size, inset, "scaleX(-1)"],
    [inset, 1920 - inset - size, "scaleY(-1)"], [1080 - inset - size, 1920 - inset - size, "scale(-1,-1)"],
  ];
  return (
    <>
      {at.map(([x, y, t], i) => (
        <svg key={i} width={size} height={size} viewBox="0 0 116 116"
             style={{ position: "absolute", left: x, top: y, opacity: 0.34,
                      transform: t === "none" ? undefined : t }}>
          <path d={d} fill="none" stroke={p.g2} strokeWidth="2.4" />
        </svg>
      ))}
    </>
  );
};

// ── 顶部品牌行 + 期号 ─────────────────────────────────────────────────────

export const PosterBrand: React.FC<{
  p: Palette; zh: string; brand: string; badge: string; top?: number;
}> = ({ p, zh, brand, badge, top = 296 }) => (
  <>
    <div style={{ position: "absolute", top, width: "100%", textAlign: "center",
                  fontFamily: ZH_UI, fontSize: 30, letterSpacing: 2, color: p.soft }}>
      {brand}
    </div>
    <div style={{ position: "absolute", top: top + 56, width: "100%",
                  display: "flex", justifyContent: "center", alignItems: "center", gap: 18 }}>
      <div style={{ width: 96, height: 1, background: p.line, opacity: 0.7 }} />
      <div style={{ position: "relative", padding: "8px 30px" }}>
        <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none"
             style={{ position: "absolute", inset: 0 }}>
          <path d="M6 0 H94 L100 14 V86 L94 100 H6 L0 86 V14 Z" fill="none"
                stroke={p.line} strokeWidth="2" vectorEffect="non-scaling-stroke" />
        </svg>
        <div style={{ position: "relative", fontFamily: ZH_UI, fontSize: 32,
                      letterSpacing: 4, color: p.g2 }}>{badge}</div>
      </div>
      <div style={{ width: 96, height: 1, background: p.line, opacity: 0.7 }} />
    </div>
  </>
);

// ── 立体金字 ──────────────────────────────────────────────────────────────

/**
 * 四层叠出「烫金浮雕」：外发光 → 暗色描边 → 向下位移的暗影 → 渐变字面。
 * 参考图那种字是印刷厂的烫金效果，用一层 color 是做不出来的。
 */
export const GoldText: React.FC<{
  p: Palette; zh: string; text: string; size: number;
  strokeW?: number; letterSpacing?: number; lineHeight?: number;
  align?: "center" | "left";
}> = ({ p, zh, text, size, strokeW, letterSpacing = 2, lineHeight = 1.2, align = "center" }) => {
  const sw = strokeW ?? Math.max(4, Math.round(size * 0.045));
  const common: React.CSSProperties = {
    position: "absolute", left: 0, top: 0, width: "100%", textAlign: align,
    fontFamily: ZH_TITLE, fontSize: size, lineHeight, letterSpacing, whiteSpace: "nowrap",
  };
  // 三层，顺序不能动：
  //   1 外发光（暖，模糊）
  //   2 暗色描边层 —— **必须画在字面下面**。-webkit-text-stroke 是居中描边，
  //     往字身里吃进去一半；只有让不带描边的字面盖在它上面，内部才干净，
  //     露在外面的只有描边的外半圈。
  //   3 字面（金属渐变）+ drop-shadow 给厚度
  //
  // 试过把描边和字面画在同一个元素上用 paint-order:stroke —— 这个 Chrome 不认，
  // 描边直接盖在字面之上，横画被吃掉一半，比原来更脏。别再试了。
  //
  // 另外两条是「缩略图上一片黑杂色」的真正来源，都已收窄：
  //   · 描边宽度从 0.072×字号 收到 0.045 —— 满幅看不出差别，
  //     缩到 330px 宽时暗边不再和渐变暗带糊成一坨。
  //   · 渐变的暗档提亮并收窄，小尺寸下整个字读作实心金，而不是「中间发黑」。
  return (
    <div style={{ position: "relative", width: "100%", height: size * lineHeight }}>
      <div style={{ ...common, color: p.glow, filter: "blur(30px)", opacity: 0.5 }}>{text}</div>
      <div style={{ ...common, color: p.stroke, WebkitTextStroke: `${sw}px ${p.stroke}` }}>{text}</div>
      <div style={{ ...common,
                    backgroundImage:
                      `linear-gradient(177deg, ${p.g1} 0%, ${p.g2} 30%, ${p.g4} 48%, ` +
                      `${p.g3} 55%, ${p.g4} 62%, ${p.g2} 86%, ${p.g1} 100%)`,
                    WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent",
                    filter: `drop-shadow(0 ${Math.round(size * 0.018)}px 0 ${p.stroke}) ` +
                            `drop-shadow(0 6px 14px rgba(90,36,16,0.5))` }}>
        {text}
      </div>
    </div>
  );
};

/**
 * 标题区。六种构图变体，同一套设计语言，但每集的排布不一样。
 *
 *   center   居中两行
 *   stack    外文词巨大压顶，中文在下
 *   left     左对齐贴边距，右侧一条竖金线
 *   split    一条横金线劈成上下两半
 *   frame    双描金框整个框住
 *   band     通栏实色块压住（字幕条式）
 *
 * ★ 2026-08-28 起：**封面文案总量不超过 12 个字**（用户指令「封面过于复杂了」）。
 *   t1 / t2 不再是「铺垫行 + 点题行」，而是**同一句话拆成的上下两行**，
 *   所以两行**等大**，不再做 0.72 的层级差。匾、词表、脚注一律不上封面 ——
 *   那些是把封面写成目录的东西。
 */
export type PosterLayout = "center" | "stack" | "left" | "split" | "frame" | "band";

const BT = 660, BB = 1260;

export const PosterTitle: React.FC<{
  p: Palette; zh: string; t1: string; t2: string;
  layout?: PosterLayout; word?: string; wordFont?: string;
}> = ({ p, zh, t1, t2, layout = "center", word, wordFont }) => {
  const len = (t: string) => Math.max([...(t || "")].length, 1);
  // 两行等大：按较长的那行定字号
  const size = Math.min(158, Math.floor(920 / Math.max(len(t1), len(t2))));
  const lh = 1.24, h = size * lh;
  const gold = (text: string, sz: number, ls = 2, align: "center" | "left" = "center") => (
    <GoldText p={p} zh={zh} text={text} size={sz} letterSpacing={ls} align={align} lineHeight={lh} />
  );

  if (layout === "stack") {
    const ws = Math.min(196, Math.floor(760 / Math.max(len(word || t2), 1)));
    const s2 = Math.min(148, size);
    const top = BT + 4;
    return (
      <>
        <div style={{ position: "absolute", top, width: "100%", textAlign: "center",
                      fontFamily: wordFont ?? "ThaiBold, sans-serif", fontSize: ws,
                      lineHeight: 1.42, color: p.g2, textShadow: `0 0 40px ${p.halo}` }}>
          {word ?? t2}
        </div>
        <div style={{ position: "absolute", top: top + ws * 1.42 + 20, width: "100%" }}>{gold(t1, s2)}</div>
        <div style={{ position: "absolute", top: top + ws * 1.42 + 20 + s2 * lh, width: "100%" }}>{gold(t2, s2)}</div>
      </>
    );
  }

  if (layout === "left") {
    const s2 = Math.min(148, Math.floor(880 / Math.max(len(t1), len(t2))));
    const top = Math.round(BT + (BB - BT - s2 * lh * 2) / 2);
    return (
      <>
        <div style={{ position: "absolute", left: 996, top: BT + 20, width: 3, height: BB - BT - 40,
                      background: `linear-gradient(180deg, rgba(0,0,0,0) 0%, ${p.g3} 30%, ${p.g3} 70%, rgba(0,0,0,0) 100%)`,
                      opacity: 0.7 }} />
        <div style={{ position: "absolute", left: 92, top, width: 900 }}>{gold(t1, s2, 2, "left")}</div>
        <div style={{ position: "absolute", left: 92, top: top + s2 * lh, width: 900 }}>{gold(t2, s2, 2, "left")}</div>
      </>
    );
  }

  if (layout === "split") {
    const ruleY = Math.round(BT + 300 - h / 2);
    return (
      <>
        <div style={{ position: "absolute", top: ruleY - h - 26, width: "100%" }}>{gold(t1, size)}</div>
        <div style={{ position: "absolute", left: 96, top: ruleY, width: 888, height: 3,
                      background: p.g3, opacity: 0.85 }} />
        <div style={{ position: "absolute", top: ruleY + 26, width: "100%" }}>{gold(t2, size)}</div>
      </>
    );
  }

  if (layout === "frame") {
    const s2 = Math.min(140, Math.floor(760 / Math.max(len(t1), len(t2))));
    const inner = s2 * lh * 2 + 88;
    const top = Math.round(BT + (BB - BT - inner) / 2);
    return (
      <>
        <div style={{ position: "absolute", left: 78, top, width: 924, height: inner,
                      border: `4px solid ${p.g3}` }} />
        <div style={{ position: "absolute", left: 92, top: top + 14, width: 896, height: inner - 28,
                      border: `1.6px solid ${p.g3}`, opacity: 0.55 }} />
        <div style={{ position: "absolute", top: top + 44, width: "100%" }}>{gold(t1, s2)}</div>
        <div style={{ position: "absolute", top: top + 44 + s2 * lh, width: "100%" }}>{gold(t2, s2)}</div>
      </>
    );
  }

  if (layout === "band") {
    // 字幕条：一条横贯画幅的**半透明压条**，字还是金的。
    //
    // 早先是金色渐变实心条 + 上下高光边 + 投影 + 深色字 —— 那是**按钮**的做法，
    // 看着就像画面中间贴了个大按钮（用户原话「不要做的像个大按钮」）。
    // 现在只压暗底、上下各一道细金线，文字沿用别的版式同一套烫金处理。
    const s2 = Math.min(148, Math.floor(880 / Math.max(len(t1), len(t2))));
    const barH = Math.round(s2 * lh * 2 + 44);
    const top = Math.round(BT + (BB - BT - barH) / 2);
    return (
      <>
        <div style={{ position: "absolute", left: 0, top, width: 1080, height: barH,
                      backgroundColor: "rgba(0,0,0,0.34)" }} />
        <div style={{ position: "absolute", left: 0, top, width: 1080, height: 2,
                      background: p.g3, opacity: 0.55 }} />
        <div style={{ position: "absolute", left: 0, top: top + barH - 2, width: 1080, height: 2,
                      background: p.g3, opacity: 0.55 }} />
        <div style={{ position: "absolute", top: top + 20, width: "100%" }}>{gold(t1, s2)}</div>
        <div style={{ position: "absolute", top: top + 20 + s2 * lh, width: "100%" }}>{gold(t2, s2)}</div>
      </>
    );
  }

  const top = Math.round(BT + (BB - BT - h * 2) / 2);
  return (
    <>
      <div style={{ position: "absolute", top, width: "100%" }}>{gold(t1, size)}</div>
      <div style={{ position: "absolute", top: top + h, width: "100%" }}>{gold(t2, size)}</div>
    </>
  );
};

// ── 描金匾 ────────────────────────────────────────────────────────────────

export const Plaque: React.FC<{
  p: Palette; zh: string; text: string; top: number;
  width?: number; height?: number; size?: number;
}> = ({ p, zh, text, top, width = 700, height = 118, size = 58 }) => (
  <div style={{ position: "absolute", left: (1080 - width) / 2, top, width, height }}>
    <svg width={width} height={height} style={{ position: "absolute", inset: 0 }}>
      <path d={`M22 2 H${width - 22} L${width - 2} ${height / 2} L${width - 22} ${height - 2} H22 L2 ${height / 2} Z`}
            fill={p.plaqueFill} stroke={p.g3} strokeWidth="3" />
      <path d={`M34 12 H${width - 34} L${width - 16} ${height / 2} L${width - 34} ${height - 12} H34 L16 ${height / 2} Z`}
            fill="none" stroke={p.g3} strokeWidth="1.4" opacity="0.55" />
    </svg>
    <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center",
                  justifyContent: "center", fontFamily: ZH_TITLE, fontSize: size, letterSpacing: 4,
                  color: p.plaqueInk, whiteSpace: "nowrap" }}>
      {text}
    </div>
  </div>
);

// ── 纹样分隔 + 带外的词表/脚注 ────────────────────────────────────────────

const MARKS: Record<string, string> = {
  // 莲：三瓣
  lotus: "M32 26 C22 26 14 20 12 12 C20 10 28 14 32 22 C36 14 44 10 52 12 C50 20 42 26 32 26 Z M32 24 C28 18 28 10 32 4 C36 10 36 18 32 24 Z",
  // 云：如意云头
  cloud: "M8 22 C8 15 14 11 20 13 C22 6 32 4 37 10 C44 8 52 13 52 20 C56 21 58 24 56 26 L10 26 C6 26 5 23 8 22 Z",
  // 水波
  wave: "M4 20 C10 12 18 12 24 20 C30 28 38 28 44 20 C50 12 56 12 60 18",
  // 钱：外圆内方
  coin: "M32 4 A18 18 0 1 0 32 40 A18 18 0 1 0 32 4 Z M25 15 H39 V29 H25 Z",
  // 稻穗／竹节
  bamboo: "M32 4 V40 M32 12 C24 12 20 8 20 4 M32 12 C40 12 44 8 44 4 M32 24 C24 24 20 20 20 16 M32 24 C40 24 44 20 44 16",
  // 星芒
  spark: "M32 2 L37 24 L58 30 L37 36 L32 58 L27 36 L6 30 L27 24 Z",
};

export const PosterFoot: React.FC<{
  p: Palette; zh: string; latin: string;
  ornament?: keyof typeof MARKS; row?: string[]; foot?: string; top?: number;
}> = ({ p, zh, latin, ornament = "lotus", row, foot, top = 1288 }) => (
  <>
    <div style={{ position: "absolute", top, width: "100%", display: "flex",
                  alignItems: "center", justifyContent: "center", gap: 20 }}>
      <div style={{ width: 190, height: 1, background: p.line, opacity: 0.5 }} />
      <svg width="64" height="44" viewBox="0 0 64 44">
        <path d={MARKS[ornament]} fill={ornament === "wave" || ornament === "bamboo" ? "none" : p.g2}
              stroke={p.g2} strokeWidth={ornament === "wave" || ornament === "bamboo" ? 2.4 : 0}
              opacity="0.9" />
      </svg>
      <div style={{ width: 190, height: 1, background: p.line, opacity: 0.5 }} />
    </div>
    {row && row.length ? (
      <div style={{ position: "absolute", top: top + 56, width: "100%", textAlign: "center",
                    fontFamily: latin, fontSize: 42, letterSpacing: 2, color: p.g2 }}>
        {row.join("  ·  ")}
      </div>
    ) : null}
    {foot ? (
      <div style={{ position: "absolute", top: top + 132, width: "100%", textAlign: "center",
                    fontFamily: ZH_UI, fontSize: 28, letterSpacing: 2, color: p.soft }}>
        {foot}
      </div>
    ) : null}
  </>
);
