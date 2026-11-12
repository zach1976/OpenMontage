import React from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const clamp = {extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const};
const TH = '"Sarabun", "Noto Sans Thai", sans-serif';
const ZH = '"PingFang SC", "Noto Sans CJK SC", sans-serif';
const ZH_SERIF = '"STKaiti", "Kaiti SC", "Songti SC", serif';

export type ThaiLearningItem = {
  thai: string;
  homophone: string;
  chinese: string;
  breakdown?: {thai: string; chinese: string; homophone?: string; tip?: string}[];
  wordTimings?: {start: number; end: number}[];
  note?: string;
  pair?: {dish: string; icon?: string; made: string};
  photoSrc?: string;
  photoCaption?: string;  // 实拍照片卡的小标题，默认「招牌上这样写」（海报用「海报上这样写」）  // 卡片中间的实物图（替代拆词格子/emoji 插画区）  // 酱料一类：配什么菜 + 用什么做的，画在卡片下方
  start: number;
  end: number;
  imageSrc?: string;
  phase?: "lesson" | "analysis";
};

export type ThaiLearningCardsProps = {
  seriesName: string;
  episode: string;
  topic: string;
  hook: string;
  coverTitle?: string;
  accent: string;
  accent2?: string;
  durationSeconds: number;
  coverEnd: number;
  outroStart: number;
  narrationSrc: string;
  musicSrc: string;
  backgroundSrc?: string;
  musicGain?: number;              // 垫乐倍率，默认 1（蘸酱那集要听得出泰国味，给 2.5）
  coverImageSrc?: string;          // 照片封面：整幅实物图 + 中段两行等大标题（蘸酱那集起）
  coverLines?: [string, string];
  appIconSrc?: string;
  mode?: "grid" | "cards" | "food";
  // 独立成片模式（2026-11）：给了 coverVariant 就不上期号，封面构图由它决定，
  // 原来放期号数字的位置改放 glyph（默认取主题首字）。
  coverVariant?: number;
  glyph?: string;
  items: ThaiLearningItem[];
  recap?: {start: number; end: number; words: {thai: string; chinese: string; start: number; end: number}[]} | null;
  speechRanges?: {start: number; end: number}[];
  // 实拍招牌（2026-11-11 用户：「海报需要有完整海报的画面」）：开头看整张、结尾对着整张再读一遍
  overview?: PosterView & {start: number; end: number} | null;
  posterReview?: PosterView & {start: number; end: number; follow?: boolean; steps: {start: number; end: number; thai: string; chinese: string; box: number[]}[]} | null;
};
type PosterView = {src: string; w: number; h: number; label: string; boxes?: number[][]; caption?: string};

const Background: React.FC<{p: ThaiLearningCardsProps; item?: ThaiLearningItem}> = ({p, item}) => {
  const frame = useCurrentFrame();
  const zoom = interpolate(frame, [0, p.durationSeconds * 30], [1.02, 1.09], clamp);
  const src = item?.imageSrc ?? p.backgroundSrc;
  return <AbsoluteFill style={{background: `linear-gradient(155deg, ${p.accent} 0%, #101B25 62%, #071016 100%)`, overflow: "hidden"}}>
    {src ? <Img src={staticFile(src)} style={{position: "absolute", inset: -18, width: "calc(100% + 36px)", height: "calc(100% + 36px)", objectFit: "cover", transform: `scale(${zoom})`, filter: "saturate(1.05) contrast(1.03)"}} /> : null}
    <AbsoluteFill style={{background: src?.includes("/sign_") ? "linear-gradient(180deg, transparent 70%, rgba(5,13,19,.5))" : src ? "linear-gradient(180deg, rgba(5,13,19,.20), rgba(5,13,19,.48) 58%, rgba(5,13,19,.86))" : "radial-gradient(circle at 80% 8%, rgba(255,255,255,.15), transparent 34%)"}} />
  </AbsoluteFill>;
};

const Header: React.FC<{p: ThaiLearningCardsProps; label?: string}> = ({p, label}) => <div style={{position: "absolute", top: 52, left: 48, right: 48, display: "flex", justifyContent: "space-between", alignItems: "center"}}>
  <div style={{fontFamily: ZH, fontSize: 27, fontWeight: 800, letterSpacing: 2, padding: "13px 22px", borderRadius: 999, color: "#203039", background: "rgba(255,255,255,.92)", boxShadow: "0 12px 36px rgba(0,0,0,.16)"}}>{p.seriesName}</div>
  <div style={{fontFamily: ZH, fontSize: 23, letterSpacing: 2, padding: "12px 18px", borderRadius: 999, color: "#FFF7E9", background: "rgba(15,29,37,.72)"}}>{label ?? `${p.episode} · ${p.topic}`}</div>
</div>;

const CoverMotif: React.FC<{p: ThaiLearningCardsProps}> = ({p}) => {
  const isEmergency = p.seriesName.includes("紧急应急");
  const isFood = p.seriesName.includes("泰国美食");
  const isAddress = p.seriesName.includes("怎么称呼");
  const isThaiParcel = p.seriesName.includes("泰语千词 · 场景短句") && (p.episode === "NO.21" || p.topic === "在泰国寄快递");
  const gold = p.accent2 ?? "#F5C45A";

  if (isEmergency) {
    return <div style={{position: "absolute", top: 180, left: "50%", width: 334, height: 334, transform: "translateX(-50%)"}}>
      <div style={{position: "absolute", inset: 0, borderRadius: "50%", border: "2px solid rgba(255,255,255,.18)"}} />
      <div style={{position: "absolute", inset: 34, borderRadius: "50%", border: `9px solid ${gold}`, boxShadow: `0 0 70px ${gold}55, inset 0 0 46px rgba(0,0,0,.18)`, background: "rgba(8,18,25,.28)"}} />
      <div style={{position: "absolute", left: 154, top: 88, width: 26, height: 158, borderRadius: 20, background: "#FFF8E9", boxShadow: "0 8px 24px rgba(0,0,0,.2)"}} />
      <div style={{position: "absolute", left: 154, top: 266, width: 26, height: 26, borderRadius: "50%", background: gold}} />
      {[0, 1, 2].map((i) => <div key={i} style={{position: "absolute", left: 163, top: 163, width: 178 + i * 70, height: 178 + i * 70, borderRadius: "50%", border: "1px solid rgba(255,255,255,.11)", transform: "translate(-50%, -50%)"}} />)}
    </div>;
  }

  if (isFood) {
    return <div style={{position: "absolute", top: 190, left: "50%", width: 430, height: 300, transform: "translateX(-50%)"}}>
      {[0, 1, 2].map((i) => <div key={i} style={{position: "absolute", top: 0, left: 122 + i * 72, width: 60, height: 132, borderRadius: "50%", borderLeft: `8px solid ${i === 1 ? gold : "rgba(255,255,255,.72)"}`, transform: `rotate(${i === 1 ? 8 : -8}deg)`}} />)}
      <div style={{position: "absolute", left: 38, right: 38, bottom: 34, height: 128, borderRadius: "0 0 190px 190px", border: "10px solid #FFF8E9", borderTop: `14px solid ${gold}`, background: "rgba(8,18,25,.26)", boxShadow: `0 28px 70px rgba(0,0,0,.3), 0 0 54px ${gold}33`}} />
      <div style={{position: "absolute", left: 95, right: 95, bottom: 0, height: 10, borderRadius: 999, background: "rgba(255,255,255,.42)"}} />
    </div>;
  }

  return <div style={{position: "absolute", top: 184, left: "50%", width: 470, height: 300, transform: "translateX(-50%)"}}>
    <div style={{position: "absolute", left: 0, top: 20, width: 310, height: 178, borderRadius: 48, background: "rgba(255,255,255,.94)", boxShadow: "0 28px 70px rgba(0,0,0,.26)"}}>
      <div style={{position: "absolute", left: 56, top: 69, display: "flex", gap: 24}}>{[0, 1, 2].map((i) => <span key={i} style={{width: 28, height: 28, borderRadius: "50%", background: i === 1 ? gold : p.accent}} />)}</div>
      <div style={{position: "absolute", left: 58, bottom: -28, width: 58, height: 58, background: "rgba(255,255,255,.94)", clipPath: "polygon(0 0, 100% 0, 0 100%)"}} />
    </div>
    <div style={{position: "absolute", right: 0, bottom: 0, width: 260, height: 146, borderRadius: 42, border: `7px solid ${gold}`, background: "rgba(8,18,25,.72)", boxShadow: `0 22px 55px rgba(0,0,0,.28), 0 0 42px ${gold}33`}}>
      <div style={{position: "absolute", right: 46, bottom: -25, width: 52, height: 52, background: gold, clipPath: "polygon(0 0, 100% 0, 100% 100%)"}} />
      <div style={{fontFamily: ZH_SERIF, fontSize: 88, lineHeight: 1, color: gold, textAlign: "center", marginTop: 20}}>“ ”</div>
    </div>
  </div>;
};

// 照片封面：第一帧就是成品（平台拿它当封面），标题两行等大、整块落在核心带 660–1260，
// 品牌行放 y≈296（躲开抖音顶部 220px 遮挡，3:4 版位也看得见）。
const CoverPhoto: React.FC<{p: ThaiLearningCardsProps}> = ({p}) => {
  const f = useCurrentFrame();
  const gold = p.accent2 ?? "#F5C45A";
  const brand = p.seriesName.includes("越南语") ? "越南语千词" : "泰语千词";
  const [l1, l2] = p.coverLines ?? [p.coverTitle ?? p.topic, ""];
  const size = Math.min(168, Math.floor(900 / Math.max(l1.length, l2.length, 1)));
  return <AbsoluteFill style={{background: "#140C08"}}>
    <Img src={staticFile(p.coverImageSrc!)} style={{position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", transform: `scale(${1.02 + f * 0.0006})`}} />
    <AbsoluteFill style={{background: "linear-gradient(180deg, rgba(20,10,6,.30) 0%, rgba(20,10,6,0) 22%, rgba(20,10,6,0) 78%, rgba(20,10,6,.38) 100%)"}} />
    <div style={{position: "absolute", left: 0, right: 0, top: 690, height: 540, background: "linear-gradient(180deg, rgba(24,12,6,0) 0%, rgba(24,12,6,.72) 14%, rgba(24,12,6,.78) 86%, rgba(24,12,6,0) 100%)", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center"}}>
      <div style={{fontFamily: ZH, fontSize: 34, fontWeight: 800, letterSpacing: 4, color: "#F3E2C8", marginBottom: 22}}>{brand} · {p.episode}</div>
      <div style={{width: 120, height: 6, borderRadius: 3, background: gold, marginBottom: 34}} />
      <div style={{fontFamily: ZH_SERIF, fontWeight: 900, fontSize: size, lineHeight: 1.22, color: "#FFF6E6", letterSpacing: 6, textShadow: "0 6px 28px rgba(0,0,0,.55)"}}>{l1}</div>
      {l2 ? <div style={{fontFamily: ZH_SERIF, fontWeight: 900, fontSize: size, lineHeight: 1.22, color: gold, letterSpacing: 6, textShadow: "0 6px 28px rgba(0,0,0,.55)"}}>{l2}</div> : null}
      <div style={{width: 120, height: 6, borderRadius: 3, background: gold, marginTop: 34}} />
    </div>
  </AbsoluteFill>;
};

const Cover: React.FC<{p: ThaiLearningCardsProps}> = ({p}) => {
  const languageBrand = p.seriesName.includes("越南语") ? "越南语千词" : "泰语千词";
  const targetLanguage = p.seriesName.includes("越南语") ? "越南语" : "泰语";
  const country = p.seriesName.includes("越南语") ? "越南" : "泰国";
  const isFood = p.seriesName.includes("泰国美食");
  const isAddress = p.seriesName.includes("怎么称呼");
  const isThaiParcel = p.seriesName.includes("泰语千词 · 场景短句") && (p.episode === "NO.21" || p.topic === "在泰国寄快递");
  const unit = isFood ? "个美食词" : "句实用表达";
  const standalone = p.coverVariant !== undefined && p.coverVariant !== null;
  const episodeNumber = standalone ? (p.glyph ?? p.topic.slice(0, 1)) : (p.episode.replace(/[^0-9]/g, "") || p.episode);
  const episodeIndex = Math.max(0, Number(episodeNumber) - 1);
  const seriesOffset = p.seriesName.includes("紧急应急") ? 2 : isFood ? 4 : 0;
  const variant = standalone ? ((p.coverVariant as number) % 6 + 6) % 6 : (episodeIndex + seriesOffset) % 6;
  const gold = p.accent2 ?? "#F5C45A";
  const seriesShort = p.seriesName.split("·").pop()?.trim();
  const primaryItemCount = p.items.filter((item) => item.phase !== "analysis").length;
  const smallMeta = `${primaryItemCount}${unit} · 先听${targetLanguage}再看谐音`;
  const coverText = p.coverTitle ?? p.hook;
  const patterns = [
    "repeating-linear-gradient(135deg, rgba(255,255,255,.028) 0 2px, transparent 2px 24px)",
    "radial-gradient(circle at 18% 24%, rgba(255,255,255,.10) 0 2px, transparent 3px)",
    "repeating-linear-gradient(90deg, rgba(255,255,255,.035) 0 1px, transparent 1px 62px)",
    "repeating-radial-gradient(circle at 82% 20%, rgba(255,255,255,.04) 0 2px, transparent 3px 34px)",
    "linear-gradient(120deg, transparent 46%, rgba(255,255,255,.045) 46% 47%, transparent 47%)",
    "repeating-linear-gradient(0deg, rgba(255,255,255,.025) 0 2px, transparent 2px 38px)",
  ];
  const motifShift = ["translate(270px, -10px) scale(.82)", "translate(-235px, 235px) scale(.68)", "translate(250px, 520px) scale(.72)", "translate(-250px, -5px) scale(.78)", "translate(0, 30px) scale(.88)", "translate(255px, 250px) scale(.70)"][variant];
  const motif = <div style={{position: "absolute", inset: 0, transform: motifShift, transformOrigin: "center top"}}><CoverMotif p={p} /></div>;
  const brand = <div style={{fontFamily: ZH, fontSize: 25, fontWeight: 900, letterSpacing: 3, color: "#FFF8E9"}}>{languageBrand} <span style={{color: gold}}>•</span> {seriesShort}</div>;
  const meta = <div style={{fontFamily: ZH, fontSize: 23, fontWeight: 700, letterSpacing: 2, color: "rgba(255,255,255,.70)"}}>{smallMeta}</div>;
  const ghostTopic = <div style={{fontFamily: ZH_SERIF, fontSize: 230, lineHeight: .86, fontWeight: 900, color: "rgba(255,255,255,.052)", writingMode: "vertical-rl", letterSpacing: -24}}>{p.topic.slice(0, 4)}</div>;

  let layout: React.ReactNode;
  if (isThaiParcel) {
    layout = <>
      <div style={{position: "absolute", top: 54, left: 54}}>{brand}</div>
      <div style={{position: "absolute", top: 50, right: 54, fontFamily: ZH, color: gold, fontSize: 34, fontWeight: 950}}>{p.episode}</div>
      <div style={{position: "absolute", top: 185, right: 42, fontFamily: ZH, fontSize: 300, lineHeight: 1, fontWeight: 950, color: "rgba(255,255,255,.055)"}}>{episodeNumber}</div>
      <div style={{position: "absolute", left: 72, right: 72, top: 575, padding: "64px 58px 60px", borderRadius: 42, background: "rgba(246,242,232,.97)", borderTop: `11px solid ${gold}`, boxShadow: "0 38px 100px rgba(0,0,0,.38)"}}>
        <div style={{fontFamily: ZH, fontSize: 28, fontWeight: 950, color: p.accent, textAlign: "center", letterSpacing: 5}}>{p.episode} · {p.topic}</div>
        <div style={{fontFamily: ZH_SERIF, fontSize: 118, lineHeight: 1.16, fontWeight: 900, color: "#17262D", textAlign: "center", marginTop: 34}}>{coverText}</div>
        <div style={{width: 180, height: 7, background: gold, margin: "38px auto 28px"}} />
        <div style={{fontFamily: ZH, fontSize: 34, fontWeight: 850, color: "#526167", textAlign: "center"}}>最常用的 5 句话</div>
      </div>
      <div style={{position: "absolute", left: 0, right: 0, bottom: 185, textAlign: "center"}}>{meta}</div>
    </>;
  } else if (isAddress) {
    layout = <>
      <div style={{position: "absolute", top: 54, left: 54}}>{brand}</div>
      <div style={{position: "absolute", top: 50, right: 54, fontFamily: ZH, color: gold, fontSize: 31, fontWeight: 950}}>{p.episode}</div>
      <div style={{position: "absolute", top: 205, right: 30, fontFamily: ZH, fontSize: 270, fontWeight: 950, lineHeight: 1, color: "rgba(255,255,255,.055)"}}>{episodeNumber}</div>
      <div style={{position: "absolute", left: 64, right: 64, top: 530, padding: "58px 44px 62px", background: "rgba(246,242,232,.97)", borderRadius: 34, boxShadow: "0 36px 100px rgba(0,0,0,.34)", borderTop: `10px solid ${gold}`}}>
        <div style={{display: "inline-block", padding: "10px 20px", borderRadius: 999, background: p.accent, color: "white", fontFamily: ZH, fontSize: 28, fontWeight: 950}}>{p.topic}</div>
        <div style={{fontFamily: ZH_SERIF, fontSize: coverText.length > 8 ? 84 : 96, lineHeight: 1.2, color: "#17262D", marginTop: 34, whiteSpace: "nowrap", letterSpacing: 1}}>{coverText}</div>
        <div style={{height: 3, background: `linear-gradient(90deg, ${gold}, transparent)`, margin: "38px 0 28px"}} />
        <div style={{fontFamily: ZH, fontSize: 26, color: "#5F6C71", fontWeight: 800}}>{smallMeta}</div>
      </div>
      <div style={{position: "absolute", left: 92, bottom: 185, fontFamily: ZH, fontSize: 29, color: "rgba(255,255,255,.76)", letterSpacing: 3}}>在{country}生活 · 开口自然称呼</div>
    </>;
  } else if (variant === 0) {
    layout = <>
      <div style={{position: "absolute", top: 54, left: 54}}>{brand}</div>
      <div style={{position: "absolute", top: 125, left: 54, fontFamily: ZH, fontSize: 245, lineHeight: 1, fontWeight: 950, letterSpacing: -24, color: "rgba(255,255,255,.07)"}}>{episodeNumber}</div>
      {motif}
      <div style={{position: "absolute", left: 62, right: 180, top: 690}}>
        <div style={{display: "inline-block", padding: "11px 20px", background: gold, color: "#17242B", fontFamily: ZH, fontSize: 27, fontWeight: 950, borderRadius: "4px 22px 22px 4px"}}>{p.episode} / {p.topic}</div>
        <div style={{fontFamily: ZH_SERIF, fontSize: coverText.length > 8 ? 76 : 88, lineHeight: 1.25, color: "#FFF8E9", marginTop: 28, textShadow: "0 10px 36px rgba(0,0,0,.28)"}}>{coverText}</div>
        <div style={{width: 168, height: 8, background: gold, marginTop: 38}} />
      </div>
      <div style={{position: "absolute", left: 62, bottom: 180}}>{meta}</div>
      <div style={{position: "absolute", right: 52, bottom: 150, fontFamily: ZH, fontSize: 80, fontWeight: 950, color: gold, transform: "rotate(-90deg)", transformOrigin: "right bottom", letterSpacing: 5}}>{standalone ? "" : `NO.${episodeNumber}`}</div>
    </>;
  } else if (variant === 1) {
    layout = <>
      <div style={{position: "absolute", inset: "0 0 auto", height: 1360, background: `linear-gradient(155deg, ${p.accent}EE, ${p.accent}55)`}} />
      <div style={{position: "absolute", top: 52, left: 58, right: 58, display: "flex", justifyContent: "space-between"}}>{brand}<div style={{fontFamily: ZH, fontSize: 31, fontWeight: 950, color: gold}}>{p.episode}</div></div>
      <div style={{position: "absolute", left: 82, right: 82, top: 700}}>
        <div style={{fontFamily: ZH, fontSize: 32, fontWeight: 900, color: gold, letterSpacing: 7}}>{p.episode} / {p.topic}</div>
        <div style={{fontFamily: ZH_SERIF, fontSize: coverText.length > 8 ? 76 : 88, lineHeight: 1.26, color: "white", marginTop: 26}}>{coverText}</div>
        <div style={{fontFamily: ZH, fontSize: 25, fontWeight: 800, color: "rgba(255,255,255,.72)", marginTop: 40}}>{smallMeta}</div>
      </div>
      {motif}
      <div style={{position: "absolute", left: 0, right: 0, top: 1360, bottom: 0, background: "#F3EFE4", clipPath: "polygon(0 7%, 100% 0, 100% 100%, 0 100%)"}}>
        <div style={{position: "absolute", left: 62, top: 210, fontFamily: ZH_SERIF, fontSize: 156, lineHeight: 1, color: `${p.accent}22`, fontWeight: 900}}>{p.topic}</div>
        <div style={{position: "absolute", left: 64, right: 64, top: 450, display: "flex", justifyContent: "space-between", alignItems: "flex-end", borderTop: `3px solid ${p.accent}`, paddingTop: 30}}>
          <div style={{fontFamily: ZH, color: "#35434A", fontSize: 27, fontWeight: 800}}>在{country}生活，开口就能用</div>
          <div style={{fontFamily: ZH, color: p.accent, fontSize: 29, fontWeight: 950}}>{smallMeta}</div>
        </div>
      </div>
    </>;
  } else if (variant === 2) {
    layout = <>
      <div style={{position: "absolute", left: 44, top: 48}}>{brand}</div>
      <div style={{position: "absolute", left: 38, top: 200}}>{ghostTopic}</div>
      {motif}
      <div style={{position: "absolute", left: 250, right: 54, top: 650, minHeight: 560, padding: "42px 46px", border: `3px solid ${gold}`, borderRadius: "120px 16px 120px 16px", background: "rgba(7,16,22,.82)", boxShadow: "0 32px 80px rgba(0,0,0,.3)"}}>
        <div style={{fontFamily: ZH, color: gold, fontSize: 28, fontWeight: 950, letterSpacing: 5}}>{p.episode} / {p.topic}</div>
        <div style={{fontFamily: ZH_SERIF, fontSize: coverText.length > 8 ? 70 : 80, lineHeight: 1.25, color: "#FFF8E9", marginTop: 30}}>{coverText}</div>
        <div style={{marginTop: 34, fontFamily: ZH, color: "rgba(255,255,255,.68)", fontSize: 24, lineHeight: 1.55}}>{smallMeta}<br/>收藏这一集，下次直接开口</div>
      </div>
      <div style={{position: "absolute", left: 56, bottom: 175, width: 200, height: 200, borderRadius: "50%", border: `2px solid ${gold}66`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: ZH, fontSize: 70, fontWeight: 950, color: gold}}>{episodeNumber}</div>
    </>;
  } else if (variant === 3) {
    layout = <>
      <div style={{position: "absolute", top: 48, left: 56}}>{brand}</div>
      <div style={{position: "absolute", top: 118, right: 42, fontFamily: ZH, fontSize: 260, lineHeight: 1, fontWeight: 950, color: "rgba(255,255,255,.07)", transform: "rotate(7deg)"}}>{episodeNumber}</div>
      {motif}
      <div style={{position: "absolute", left: 76, right: 76, top: 640, minHeight: 535, padding: "44px 50px", background: "#F4F0E6", transform: "rotate(-2.4deg)", boxShadow: "22px 30px 0 rgba(5,13,18,.24), 0 34px 90px rgba(0,0,0,.32)"}}>
        <div style={{display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: `5px solid ${p.accent}`, paddingBottom: 22}}>
          <div style={{fontFamily: ZH, fontSize: 29, fontWeight: 950, color: p.accent}}>{p.topic}</div>
          <div style={{fontFamily: ZH, fontSize: 25, color: "#536066", fontWeight: 800}}>{p.episode}</div>
        </div>
        <div style={{fontFamily: ZH_SERIF, fontSize: coverText.length > 8 ? 72 : 82, lineHeight: 1.22, color: "#17262D", marginTop: 32}}>{coverText}</div>
        <div style={{marginTop: 34, display: "inline-block", border: `3px solid ${p.accent}`, padding: "12px 20px", fontFamily: ZH, fontSize: 24, fontWeight: 900, color: p.accent}}>先听{targetLanguage} / 再看谐音</div>
      </div>
      <div style={{position: "absolute", left: 65, bottom: 165}}>{meta}</div>
    </>;
  } else if (variant === 4) {
    layout = <>
      <div style={{position: "absolute", top: 50, left: 0, right: 0, textAlign: "center"}}>{brand}</div>
      {motif}
      <div style={{position: "absolute", left: 105, right: 105, top: 680, textAlign: "center"}}>
        <div style={{fontFamily: ZH, fontSize: 31, fontWeight: 950, color: gold, letterSpacing: 8}}>{p.episode} / {p.topic}</div>
        <div style={{fontFamily: ZH_SERIF, fontSize: coverText.length > 8 ? 76 : 88, lineHeight: 1.28, color: "#FFF8E9", marginTop: 32}}>{coverText}</div>
        <div style={{height: 2, background: `linear-gradient(90deg, transparent, ${gold}, transparent)`, margin: "46px 0 34px"}} />
        <div style={{fontFamily: ZH, fontSize: 26, fontWeight: 800, color: "rgba(255,255,255,.7)"}}>{smallMeta}</div>
      </div>
      <div style={{position: "absolute", left: 330, right: 330, bottom: 190, height: 146, border: `2px solid ${gold}`, borderRadius: 999, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: ZH, color: gold, fontSize: 42, fontWeight: 950}}>{p.episode}</div>
    </>;
  } else {
    layout = <>
      <div style={{position: "absolute", inset: "45px 45px 120px", border: "1px solid rgba(255,255,255,.22)"}} />
      <div style={{position: "absolute", top: 46, left: 48, padding: "26px 30px", background: gold}}><div style={{fontFamily: ZH, color: "#17242B", fontSize: 30, fontWeight: 950}}>{seriesShort}</div></div>
      <div style={{position: "absolute", top: 46, right: 48, width: 250, height: 132, borderLeft: "1px solid rgba(255,255,255,.22)", borderBottom: "1px solid rgba(255,255,255,.22)", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: ZH, color: "white", fontSize: 38, fontWeight: 950}}>{p.episode}</div>
      {motif}
      <div style={{position: "absolute", left: 48, right: 48, top: 635, display: "grid", gridTemplateColumns: "1fr 2.1fr", minHeight: 560}}>
        <div style={{background: p.accent, padding: "48px 28px", display: "flex", flexDirection: "column", justifyContent: "space-between"}}>
          <div style={{fontFamily: ZH_SERIF, writingMode: "vertical-rl", fontSize: 72, lineHeight: 1.1, fontWeight: 900, color: "white", letterSpacing: 6}}>{coverText}</div>
          <div style={{fontFamily: ZH, fontSize: 24, color: gold, fontWeight: 900}}>{primaryItemCount}{unit}</div>
        </div>
        <div style={{background: "rgba(246,242,232,.96)", padding: "54px 42px", display: "flex", flexDirection: "column", justifyContent: "space-between"}}>
          <div style={{fontFamily: ZH, fontSize: 23, color: p.accent, fontWeight: 950, marginBottom: 18}}>{p.episode}</div>
          <div style={{fontFamily: ZH_SERIF, fontSize: coverText.length > 8 ? 68 : 78, lineHeight: 1.22, color: "#18262D"}}>{coverText}</div>
          <div style={{fontFamily: ZH, fontSize: 24, color: "#667276", fontWeight: 800, borderTop: `3px solid ${gold}`, paddingTop: 28}}>先听{targetLanguage}<br/>再看中文谐音</div>
        </div>
      </div>
      <div style={{position: "absolute", left: 58, bottom: 170}}>{meta}</div>
    </>;
  }
  return <AbsoluteFill>
    <Background p={p} />
    <AbsoluteFill style={{background: `${patterns[variant]}, radial-gradient(circle at ${18 + variant * 13}% ${16 + (variant % 3) * 12}%, rgba(255,255,255,.12), transparent 32%)`, opacity: 1}} />
    {layout}
  </AbsoluteFill>;
};

const MainCard: React.FC<{p: ThaiLearningCardsProps; item: ThaiLearningItem; index: number}> = ({p, item, index}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const localFrame = frame - Math.round(item.start * fps);
  const enter = spring({frame: localFrame, fps, config: {damping: 20, stiffness: 125}});
  const tail = interpolate(frame / fps, [item.end - .28, item.end], [1, 0], clamp);
  const progress = Math.max(0, Math.min(1, enter * tail));
  const shown = p.items.slice(0, index + 1);
  const phase = item.phase ?? "lesson";
  const phaseItems = p.items.filter((x) => (x.phase ?? "lesson") === phase);
  const phaseIndex = phaseItems.indexOf(item);
  const isTraffic = p.seriesName.includes("交通标志");
  const isSignboard = (p.seriesName.includes("招牌识字") || isTraffic) && phase === "lesson";
  if (isSignboard) return <SignV1 p={p} item={item} label={`${phaseIndex + 1} / ${phaseItems.length}`} isTraffic={isTraffic} f={localFrame} tail={tail} />;
  return <CardV1 p={p} item={item} index={index} phase={phase} label={`${phaseIndex + 1} / ${phaseItems.length}`} shown={shown} localFrame={localFrame} tail={tail} />;
};

// ── 招牌 / 交通标志页 V1（2026-11 ChatGPT 稿）：底图只有背景 + 立杆 + 标志图形，
// 牌面用 CSS 画（金属边框 + 反光膜点阵 + 螺丝），下方说明卡与 CardV1 同一家族。
const SIGN_STYLE: Record<string, {fill: string; ink: string; rim: string}> = {
  green: {fill: "#1F7A4C", ink: "#FFFFFF", rim: "#E9F2EC"},
  red: {fill: "#FBFBF8", ink: "#B3262B", rim: "#C62F33"},
  yellow: {fill: "#F6C428", ink: "#1A1C1E", rim: "#C62F33"},
};
// 实拍招牌（2026-11-11 起）：条目带 photoSrc 时不画金属牌，放用户拍的真实照片；拆词条放在中文卡下面。
const SignPhoto: React.FC<{p: ThaiLearningCardsProps; item: ThaiLearningItem; label: string; f: number; tail: number}> = ({p, item, label, f, tail}) => {
  const gold = p.accent2 ?? "#F6BC58";
  const brk = item.breakdown ?? [];
  const now = f / 30 + item.start;
  const activeIdx = brk.findIndex((_, i) => item.wordTimings?.[i] && now >= item.wordTimings[i].start && now < item.wordTimings[i].end);
  const activeTip = activeIdx >= 0 && brk[activeIdx].tip ? brk[activeIdx] : null;
  // 讲单个词时（2026-11-11 用户：「词显示得大一点」），中间大字换成这个词本身，谐音与中文也跟着换成这个词的
  const focus = activeIdx >= 0 ? brk[activeIdx] : null;
  const shown = focus?.thai ?? item.thai;
  const base = shown.replace(/[\u0E31\u0E34-\u0E3A\u0E47-\u0E4E]/g, "").length;
  const size = focus ? Math.max(90, Math.min(170, Math.floor(940 / Math.max(base * .62, 1)))) : Math.max(58, Math.min(112, Math.floor(900 / Math.max(base * .62, 1))));
  const popF = focus ? f - Math.round((item.wordTimings![activeIdx].start - item.start) * 30) : 99;
  const pop = interpolate(popF, [0, 8], [0.82, 1], {...clamp, easing: EASE});
  return <AbsoluteFill>
    <Background p={p} item={{...item, imageSrc: undefined}} />
    <div style={{position: "absolute", top: 60, left: 48, height: 74, padding: "0 30px", borderRadius: 37, background: "#FFF7F4", boxShadow: "0 8px 20px #10182726", display: "flex", alignItems: "center", fontFamily: ZH, fontSize: 29, fontWeight: 700, color: "#2A2733"}}>{p.seriesName}</div>
    <div style={{position: "absolute", top: 62, right: 48, width: 132, height: 68, borderRadius: 34, background: "#282638", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: ZH, fontSize: 29, fontWeight: 600, color: "#FFF"}}>{label}</div>
    <div style={{position: "absolute", left: 56, right: 56, top: 300, height: 386, padding: 14, borderRadius: 30, background: "#FFFDF8", boxShadow: "0 30px 60px rgba(0,0,0,.45)", transform: "rotate(-1.2deg)", ...enterA(f, 0, 12, 22)}}>
      <div style={{position: "relative", width: "100%", height: "100%", borderRadius: 20, overflow: "hidden"}}>
        <Img src={staticFile(item.photoSrc!)} style={{width: "100%", height: "100%", objectFit: "cover", transform: `scale(${1.02 + f * 0.0004})`}} />
      </div>
      <div style={{position: "absolute", right: 30, top: -22, padding: "8px 22px", borderRadius: 20, background: gold, fontFamily: ZH, fontSize: 28, fontWeight: 800, color: "#1C2430", transform: "rotate(3deg)"}}>实拍</div>
    </div>
    <div style={{position: "absolute", left: 40, right: 40, top: 720, height: 170, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: TH, fontWeight: 900, fontSize: size, lineHeight: 1.45, color: focus ? gold : "#FFF8EE", whiteSpace: "nowrap", textShadow: "0 6px 24px rgba(0,0,0,.45)", ...enterA(f, 4, 12, 16)}}><span style={{display: "inline-block", transform: `scale(${pop})`}}>{shown}</span></div>
    <div style={{position: "absolute", left: 64, right: 64, top: 910, height: 300, borderRadius: 44, background: "#FFF9F7", borderTop: `8px solid ${gold}`, boxShadow: "0 28px 70px rgba(0,0,0,.34)", opacity: tail}}>
      <div style={{position: "absolute", left: 44, right: 44, top: 30, fontFamily: ZH, fontSize: 32, fontWeight: 700, color: p.accent, whiteSpace: "nowrap"}}>{activeTip ? `💡 ${activeTip.tip}` : (item.photoCaption ?? "招牌上这样写")}</div>
      <div style={{position: "absolute", left: 0, right: 0, top: 86, display: "flex", justifyContent: "center", ...enterA(f, 8, 12, 14)}}>
        <div style={{height: 72, padding: "0 36px", borderRadius: 36, background: "linear-gradient(90deg, #F3E8F1, #EAD8EE)", display: "flex", alignItems: "center", fontFamily: ZH, fontSize: 32, fontWeight: 500, color: "#505260", whiteSpace: "nowrap"}}>谐音 · {focus?.homophone ?? item.homophone}</div>
      </div>
      <div style={{position: "absolute", left: 0, right: 0, top: 176, display: "flex", justifyContent: "center", opacity: interpolate(f, [14, 26], [0, 1], {...clamp, easing: EASE})}}>
        <div style={{height: 100, minWidth: 420, padding: "0 46px", borderRadius: 50, background: "linear-gradient(180deg, #FFF9F0, #FFF0D9)", border: `2px solid ${gold}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: ZH, fontSize: (focus?.chinese ?? item.chinese).length > 8 ? 52 : 60, fontWeight: 700, letterSpacing: 2, color: "#102430"}}>{focus?.chinese ?? item.chinese}</div>
      </div>
    </div>
    {brk.length ? <div style={{position: "absolute", left: 60, right: 60, top: 1240, display: "grid", gridTemplateColumns: `repeat(${Math.min(brk.length, 4)}, minmax(0, 1fr))`, gap: 12, ...enterA(f, 22, 14, 18)}}>
      {brk.map((w, i) => {
        const on = item.wordTimings?.[i] && f / 30 + item.start >= item.wordTimings[i].start && f / 30 + item.start < item.wordTimings[i].end;
        return <div key={i} style={{borderRadius: 24, background: on ? gold : "rgba(16,24,39,.72)", border: `2px solid ${on ? gold : "rgba(255,255,255,.22)"}`, padding: "16px 6px", textAlign: "center"}}>
          <div style={{fontFamily: TH, fontSize: w.thai.length > 8 ? 38 : 48, fontWeight: 800, lineHeight: 1.4, color: on ? "#102430" : "#FFF7EC"}}>{w.thai}</div>
          {w.homophone ? <div style={{fontFamily: ZH, fontSize: 27, fontWeight: 500, marginTop: 2, color: on ? "#3A3020" : "#C9BBD0"}}>{w.homophone}</div> : null}
          <div style={{fontFamily: ZH, fontSize: 31, fontWeight: 700, marginTop: 4, color: on ? "#102430" : "#E9DCEB"}}>{w.chinese}</div>
        </div>;
      })}
    </div> : null}
  </AbsoluteFill>;
};

// 整张海报：图按原比例放进 y 250–1170，下方 1200–1380 一条说明带；boxes 是原图像素坐标 [x,y,w,h]
const PosterFrame: React.FC<{p: ThaiLearningCardsProps; v: PosterView; active?: number; f: number; band: React.ReactNode}> = ({p, v, active, f, band}) => {
  const gold = p.accent2 ?? "#F6BC58";
  const boxW = 968, boxH = 920;
  const k = Math.min(boxW / v.w, boxH / v.h);
  const dw = v.w * k, dh = v.h * k, ox = 56 + (boxW - dw) / 2, oy = 250 + (boxH - dh) / 2;
  const boxes = v.boxes ?? [];
  const uniq = boxes.map((b, i) => ({b, i})).filter(({b}, i) => boxes.findIndex((c) => c.join() === b.join()) === i);
  return <AbsoluteFill style={{background: "#0B1118"}}>
    <Img src={staticFile(v.src)} style={{position: "absolute", inset: -60, width: "calc(100% + 120px)", height: "calc(100% + 120px)", objectFit: "cover", filter: "blur(28px) brightness(.42) saturate(1.1)"}} />
    <div style={{position: "absolute", top: 60, left: 48, height: 74, padding: "0 30px", borderRadius: 37, background: "#FFF7F4", display: "flex", alignItems: "center", fontFamily: ZH, fontSize: 29, fontWeight: 700, color: "#2A2733"}}>{p.seriesName}</div>
    <div style={{position: "absolute", top: 62, right: 48, height: 68, padding: "0 28px", borderRadius: 34, background: gold, display: "flex", alignItems: "center", fontFamily: ZH, fontSize: 30, fontWeight: 800, color: "#1C2430"}}>{v.label}</div>
    <div style={{position: "absolute", left: ox - 10, top: oy - 10, width: dw + 20, height: dh + 20, borderRadius: 18, background: "#FFFDF8", boxShadow: "0 30px 70px rgba(0,0,0,.55)", ...enterA(f, 0, 12, 18)}} />
    <Img src={staticFile(v.src)} style={{position: "absolute", left: ox, top: oy, width: dw, height: dh, borderRadius: 10, ...enterA(f, 0, 12, 18)}} />
    {uniq.map(({b, i}, n) => {
      const on = active === undefined ? f >= 10 + n * 6 : boxes[active]?.join() === b.join();
      const nums = boxes.map((c, j) => c.join() === b.join() ? j + 1 : 0).filter(Boolean).join("·");
      return <div key={n} style={{position: "absolute", left: ox + b[0] * k, top: oy + b[1] * k, width: b[2] * k, height: b[3] * k, borderRadius: 10,
        border: `${on ? 6 : 3}px solid ${on ? gold : "rgba(255,255,255,.55)"}`, boxShadow: on ? `0 0 0 4px rgba(0,0,0,.35), 0 0 34px ${gold}` : "none",
        background: active !== undefined && !on ? "rgba(10,14,20,.28)" : "transparent", opacity: active === undefined ? interpolate(f, [10 + n * 6, 16 + n * 6], [0, 1], clamp) : 1}}>
        <div style={{position: "absolute", left: -6, top: -40, minWidth: 40, height: 40, padding: "0 10px", borderRadius: 20, background: on ? gold : "#2A2733", color: on ? "#1C2430" : "#FFF", fontFamily: ZH, fontSize: 24, fontWeight: 800, display: "flex", alignItems: "center", justifyContent: "center"}}>{nums}</div>
      </div>;
    })}
    <div style={{position: "absolute", left: 56, right: 56, top: 1200, height: 180, borderRadius: 36, background: "#FFF9F2", borderTop: `8px solid ${gold}`, boxShadow: "0 24px 60px rgba(0,0,0,.4)", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center"}}>{band}</div>
  </AbsoluteFill>;
};

const PosterOverview: React.FC<{p: ThaiLearningCardsProps}> = ({p}) => {
  const f = useCurrentFrame() - Math.round(p.overview!.start * 30);
  return <PosterFrame p={p} v={p.overview!} f={f} band={<div style={{fontFamily: ZH, fontSize: 52, fontWeight: 800, color: "#102430"}}>{p.overview!.caption ?? "先看整张"}</div>} />;
};

const PosterReview: React.FC<{p: ThaiLearningCardsProps}> = ({p}) => {
  const frame = useCurrentFrame();
  const r = p.posterReview!;
  const t = frame / 30;
  const i = Math.max(0, r.steps.findIndex((s) => t >= s.start && t < s.end));
  const step = t < (r.steps[0]?.start ?? 0) ? null : r.steps[i];
  const base = (step?.thai ?? "").replace(/[\u0E31\u0E34-\u0E3A\u0E47-\u0E4E]/g, "").length;
  const v = {...r, boxes: r.steps.map((s) => s.box)};
  return <PosterFrame p={p} v={v} active={step ? i : -1} f={frame - Math.round(r.start * 30)} band={step ? <>
    <div style={{fontFamily: TH, fontSize: Math.max(44, Math.min(70, Math.floor(820 / Math.max(base * .62, 1)))), fontWeight: 900, lineHeight: 1.35, color: "#102430", whiteSpace: "nowrap"}}>{step.thai}</div>
    <div style={{fontFamily: ZH, fontSize: 36, fontWeight: 700, color: p.accent}}>{step.chinese}{r.follow === false ? "" : "　·　跟读"}</div>
  </> : <div style={{fontFamily: ZH, fontSize: 52, fontWeight: 800, color: "#102430"}}>{r.caption ?? "对着整张再读一遍"}</div>} />;
};

const SignV1: React.FC<{p: ThaiLearningCardsProps; item: ThaiLearningItem; label: string; isTraffic: boolean; f: number; tail: number}> = ({p, item, label, isTraffic, f, tail}) => {
  if (item.photoSrc) return <SignPhoto p={p} item={item} label={label} f={f} tail={tail} />;
  const kind = item.imageSrc?.match(/sign_([a-z_]+)\.png$/)?.[1];
  const st = (kind ? SIGN_STYLE[kind] : undefined) ?? {fill: "#F4F5F2", ink: "#121619", rim: "#FFFFFF"};
  const gold = p.accent2 ?? "#F6BC58";
  const base = item.thai.replace(/[\u0E31\u0E34-\u0E3A\u0E47-\u0E4E]/g, "").length;
  const size = Math.max(70, Math.min(160, Math.floor(860 / Math.max(base * .62, 1))));
  const plateTop = kind && kind in SIGN_STYLE ? 640 : 660;
  const screwEl = (top: number) => <div style={{position: "absolute", left: "50%", top, width: 26, height: 26, marginLeft: -13, borderRadius: "50%", background: "radial-gradient(circle at 35% 35%, #F2F4F6, #9AA0A6 70%)", boxShadow: "0 1px 2px rgba(0,0,0,.4)"}} />;
  return <AbsoluteFill>
    <Background p={p} item={item} />
    <div style={{position: "absolute", top: 60, left: 48, height: 74, padding: "0 30px", borderRadius: 37, background: "#FFF7F4", boxShadow: "0 8px 20px #10182726", display: "flex", alignItems: "center", fontFamily: ZH, fontSize: 29, fontWeight: 700, color: "#2A2733"}}>{p.seriesName}</div>
    <div style={{position: "absolute", top: 62, right: 48, width: 132, height: 68, borderRadius: 34, background: "#282638", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: ZH, fontSize: 29, fontWeight: 600, color: "#FFF"}}>{label}</div>
    <div style={{position: "absolute", left: 70, right: 70, top: plateTop, height: 360, borderRadius: 46, padding: 14,
      background: "linear-gradient(180deg, #F3F5F7 0%, #A9B0B7 45%, #E4E8EB 70%, #8D949B 100%)", boxShadow: "0 30px 60px rgba(0,0,0,.45), 0 0 0 2px rgba(255,255,255,.25)",
      ...enterA(f, 0, 12, 22)}}>
      <div style={{position: "relative", width: "100%", height: "100%", borderRadius: 34, background: st.fill, border: `8px solid ${st.rim}`, overflow: "hidden",
        backgroundImage: `radial-gradient(rgba(255,255,255,.22) 1.5px, transparent 1.6px), linear-gradient(160deg, rgba(255,255,255,.28), transparent 45%)`, backgroundSize: "9px 9px, 100% 100%"}}>
        {screwEl(12)}{screwEl(296)}
        <div style={{position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: TH, fontWeight: 900, fontSize: size, lineHeight: 1.5, color: st.ink, whiteSpace: "nowrap"}}>{item.thai}</div>
      </div>
    </div>
    <div style={{position: "absolute", left: 64, right: 64, top: 1110, height: 330, borderRadius: 44, background: "#FFF9F7", borderTop: `8px solid ${gold}`, boxShadow: "0 28px 70px rgba(0,0,0,.34)", opacity: tail}}>
      <div style={{position: "absolute", left: 44, top: 34, fontFamily: ZH, fontSize: 34, fontWeight: 700, color: p.accent}}>{isTraffic ? "路牌上这样写" : "招牌上这样写"}</div>
      <div style={{position: "absolute", left: 0, right: 0, top: 96, display: "flex", justifyContent: "center", ...enterA(f, 8, 12, 14)}}>
        <div style={{height: 76, padding: "0 40px", borderRadius: 38, background: "linear-gradient(90deg, #F3E8F1, #EAD8EE)", display: "flex", alignItems: "center", fontFamily: ZH, fontSize: 34, fontWeight: 500, color: "#505260"}}>谐音 · {item.homophone}</div>
      </div>
      <div style={{position: "absolute", left: 0, right: 0, top: 192, display: "flex", justifyContent: "center", opacity: interpolate(f, [14, 26], [0, 1], {...clamp, easing: EASE})}}>
        <div style={{height: 112, minWidth: 420, padding: "0 50px", borderRadius: 56, background: "linear-gradient(180deg, #FFF9F0, #FFF0D9)", border: `2px solid ${gold}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: ZH, fontSize: 64, fontWeight: 700, letterSpacing: 2, color: "#102430"}}>{item.chinese}</div>
      </div>
    </div>
  </AbsoluteFill>;
};

// ── 正文卡片页 V1（2026-11 由 ChatGPT 出稿「Language Card V1.0」落地）────────────
// 三层卡片（金色背板 + 紫色背板 + 暖白主卡）、外语 88px 自动缩放、谐音/中文胶囊、
// 卡片下半是按这一句内容换的插画区（有 breakdown / grid 的系列在这里放拆解）。
const EASE = Easing.bezier(0.22, 1, 0.36, 1);
const enterA = (f: number, start: number, dur: number, dy = 20) => {
  const k = interpolate(f, [start, start + dur], [0, 1], {...clamp, easing: EASE});
  return {opacity: k, transform: `translateY(${(1 - k) * dy}px)`};
};
const ICONS: [RegExp, string][] = [
  [/煎|炸|切/, "🍳 🔪 🔥"], [/钥匙|锁/, "🔑 🚪 🏠"], [/门|入口|出口/, "🚪 🔑 🏠"], [/书包|书|本子|笔|尺子/, "📚 ✏️ 📏"],
  [/勺子|叉子|筷子|盘子|碗|锅/, "🥢 🥄 🍽️"], [/床|桌子|椅子|窗户/, "🛏️ 🪑 🪟"], [/电梯|楼/, "🛗 🏢 🔼"],
  [/狗/, "🐕 🦴 🏠"], [/马/, "🐎 🌾 🏇"], [/螺|椰浆|河粉|法包|煎饼|布丁|奶咖|吸管|糖|苦|尝|胃口/, "🍜 🥖 🍮"],
  [/摩托|汽车|摩的|车厢|卧铺|站|换线|打表/, "🏍️ 🚗 🚕"], [/寄|包裹|追踪|行李|托运/, "📦 🧳 ✉️"],
  [/消息|喂|回电|信号|没电|停电/, "📱 💬 🔋"], [/着火|消防|救援/, "🚒 🔥 🆘"], [/护士/, "👩‍⚕️ 🏥 💊"],
  [/老板|店主|店员|前台|上司/, "🧑‍💼 🏪 🛎️"], [/公斤|公里|米|半|倍|分之|分钟|次/, "📏 ⚖️ ⏱️"], [/拍/, "📷 🖼️ ✨"],
  [/担心|放弃|努力|相信|原谅|轻松|平静|放下|随它/, "💪 🌿 ✨"], [/无聊|没劲|懒|腻|烦|躺/, "😪 🛋️ 💤"],
  [/在一起|对象|只有你|愿意/, "💕 💍 🌹"], [/名字|全名|阮|陈|黎|范|黄|Minh|Hùng|Dũng|Phúc|James|Mike|Mark|Grace|Film|Mint|Cake|Wine/, "🏷️ 👋 😊"],
  [/年/, "📅 🎆 ⏳"], [/按摩/, "💆 🌿 🧴"], [/袋子/, "🛍️ ♻️ 🧾"], [/颜色/, "🎨 👕 ✨"], [/导游/, "🧭 🗺️ 🚩"], [/结账|算错/, "🧾 💰 🧮"],
  [/纪念|周年|生日|礼物/, "🎂 🎁 🎉"], [/蟹|虾|鱼|海鲜|贝/, "🦀 🦐 🐟"], [/鸡|猪|牛|肉|烤/, "🍗 🔥 🍖"],
  [/水电|电费|水费/, "💡 💧 🧾"], [/家具|房|租|住/, "🛋️ 🔑 🏠"], [/酒店|入住|退房/, "🏨 🔑 🧳"], [/票|车站|火车|地铁|巴士|公交/, "🚆 🧳 🗺️"],
  [/机场|飞机|航班|登机/, "✈️ 🧳 🛂"], [/出租|打车|司机/, "🚕 📍 🗺️"], [/路|走|左|右|直|在哪|哪里|地址/, "🧭 📍 🗺️"], [/多少钱|价|贵|便宜|打折|买|付|钱|现金|刷卡|扫码/, "💰 🛍️ 🏷️"],
  [/吃|饭|菜|点|餐|饿|好吃|辣|甜|酸|咸|面|汤|饭店|厨/, "🍜 🥢 🌶️"], [/喝|水|茶|咖啡|啤酒|饮料|冰/, "🧋 🧊 🥤"], [/水果|榴莲|芒果|椰子|西瓜/, "🥭 🥥 🍉"], [/医|药|病|疼|痛|发烧|救命|急/, "🏥 💊 🩹"],
  [/警察|报警|丢|偷|护照/, "👮 🛂 ❗"], [/爱|喜欢|想你|亲爱|宝贝|约会|老婆|老公|情/, "💕 🌹 💌"], [/谢谢|你好|再见|对不起|没关系|欢迎/, "🙏 😊 👋"], [/朋友|家人|妈|爸|哥|姐|弟|妹|老师|孩子/, "👨‍👩‍👧 🏡 💬"],
  [/天气|热|冷|雨|晴|风/, "🌤️ 🌧️ 🌡️"], [/时间|点钟|几点|今天|明天|昨天|早上|晚上|星期|月/, "⏰ 📅 ☀️"], [/睡|累|休息|困/, "😴 🛏️ 🌙"], [/工作|上班|公司|会议/, "💼 🏢 📊"],
  [/学|说|听|懂|语言|中文|泰语|越南语|会/, "📚 🗣️ 👂"], [/手机|电话|网络|WiFi|充电|密码/, "📱 📶 🔋"], [/洗|厕所|卫生间|毛巾/, "🚻 🧴 🧻"], [/大|小|多|少|长|短|快|慢|高|低|新|旧/, "⚖️ 📏 ✨"],
  [/[0-9]/, "🔢 🧮 ✋"], [/开心|高兴|笑|哭|生气|怕/, "😄 😢 😠"], [/海|岛|山|寺|庙|景/, "🏝️ ⛰️ 🛕"], [/衣|鞋|穿|试/, "👕 👟 🛍️"],
];
const SERIES_ICONS: [RegExp, string][] = [
  [/美食/, "🍜 🥢 🌶️"], [/情侣/, "💕 🌹 💌"], [/数数/, "🔢 🧮 ✋"], [/听力/, "🎧 👂 🔊"], [/反义/, "⚖️ ↔️ ✨"], [/称呼|名字|小名|英文名/, "👋 🏷️ 😊"],
  [/紧急/, "🚑 🆘 📞"], [/旅游/, "🧳 🗺️ ✈️"], [/动词/, "🏃 ✋ 👀"], [/趣味|搞笑/, "😄 🎉 💡"], [/对话/, "💬 ☕ 😊"], [/口头禅|禅意/, "💬 🌿 ✨"],
];
const iconsFor = (item: ThaiLearningItem, series: string): string[] => {
  const own = (item as {icons?: string[]}).icons;
  if (own?.length) return own;
  const hit = ICONS.find(([re]) => re.test(item.chinese)) ?? SERIES_ICONS.find(([re]) => re.test(series));
  return (hit?.[1] ?? "💬 🗣️ ✨").split(" ");
};

const CardV1: React.FC<{p: ThaiLearningCardsProps; item: ThaiLearningItem; index: number; phase: string; label: string;
  shown: ThaiLearningItem[]; localFrame: number; tail: number}> = ({p, item, index, phase, label, shown, localFrame: f, tail}) => {
  const isVi = p.seriesName.includes("越南语");
  const accent = p.accent;
  const gold = p.accent2 ?? "#F6BC58";
  const out = interpolate(tail, [0, 1], [8, 0]);
  const len = item.thai.length;
  const ems = /[\u0E00-\u0E7F]/.test(item.thai)
    ? item.thai.replace(/[\u0E31\u0E34-\u0E3A\u0E47-\u0E4E]/g, "").length * 0.6   // 泰文：上下标不占宽
    : item.thai.length * 0.56;                                                      // 越南文：拉丁字母平均宽
  const thSize = Math.max(60, Math.min(112, Math.floor(880 / Math.max(ems, 1))));
  const twoLine = thSize <= 60 && ems > 15;
  const icons = iconsFor(item, p.seriesName);
  const float = Math.sin(f / 30 * Math.PI) * 3;
  const hasBreak = !!item.breakdown?.length;
  const isGrid = p.mode === "grid";
  return <AbsoluteFill>
    <AbsoluteFill style={{background: `linear-gradient(155deg, ${accent} 0%, ${accent}CC 22%, #343453 58%, #173A4B 85%, #0C202C 100%)`, overflow: "hidden"}}>
      <div style={{position: "absolute", left: -160, top: 100, width: 550, height: 550, borderRadius: "50%", background: "#D86FA1", filter: "blur(180px)", opacity: .17}} />
      <div style={{position: "absolute", right: -200, bottom: 250, width: 620, height: 620, borderRadius: "50%", background: "#087C8A", filter: "blur(180px)", opacity: .13}} />
      <svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{position: "absolute", inset: 0}}>
        <path d="M 280 -180 C 440 220 820 280 1010 -80" fill="none" stroke="#E6B8D9" strokeWidth={2} opacity={.25} />
        <path d="M 750 220 C 960 150 1160 280 1190 510" fill="none" stroke="#D2A8DE" strokeWidth={2} opacity={.12} />
        <path d="M -120 1750 C 210 1550 460 1660 620 1940" fill="none" stroke="#A4A2CE" strokeWidth={2} opacity={.13} />
      </svg>
    </AbsoluteFill>
    <div style={{position: "absolute", top: 60, left: 48, height: 74, padding: "0 30px", borderRadius: 37, background: "#FFF7F4", border: "1px solid #FFFFFF", boxShadow: "0 8px 20px #10182726", display: "flex", alignItems: "center", fontFamily: ZH, fontSize: 29, fontWeight: 700, color: "#2A2733", letterSpacing: 1}}>{p.seriesName}</div>
    <div style={{position: "absolute", top: 62, right: 48, width: 132, height: 68, borderRadius: 34, background: "#282638", boxShadow: "0 8px 18px #0A152A33", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: ZH, fontSize: 29, fontWeight: 600, color: "#FFF"}}>{label}</div>
    <div style={{position: "absolute", left: 42, top: 327, width: 980, height: 1060, borderRadius: 72, background: `linear-gradient(135deg, #FFE49C, ${gold})`, transform: "rotate(1.5deg)", boxShadow: "0 16px 30px #10182720"}} />
    <div style={{position: "absolute", left: 76, top: 346, width: 966, height: 1060, borderRadius: 72, background: `linear-gradient(145deg, #D9BCEB, ${accent}99)`, transform: "rotate(-1.2deg)", boxShadow: "0 18px 34px #10182724"}} />
    <div style={{position: "absolute", left: 58, top: 350, width: 964, height: 1020, borderRadius: 68, background: "#FFF9F7", border: "2px solid #FFFFFF", boxShadow: "0 24px 65px #0717234D", overflow: "hidden"}}>
      <div style={{opacity: tail, transform: `translateY(${-out}px)`}}>
        <div style={{position: "absolute", left: 58, top: 40, fontFamily: ZH, fontSize: 37, fontWeight: 700, letterSpacing: 1, color: accent}}>{phase === "analysis" ? "常用词分析" : (isVi ? "越南语先念" : "泰语先念")}</div>
        <div style={{position: "absolute", left: 58, top: 116, width: 90, height: 7, borderRadius: 4, background: gold}} />
        <div style={{position: "absolute", left: 30, right: 30, top: 150, height: 200, display: "flex", alignItems: "center", justifyContent: "center", ...enterA(f, 0, 12, 22)}}>
          <div style={{fontFamily: TH, fontSize: twoLine ? 64 : thSize, fontWeight: 800, lineHeight: twoLine ? 1.4 : 1.65, color: "#102430", textAlign: "center", whiteSpace: twoLine ? "normal" : "nowrap"}}>{item.thai}</div>
        </div>
        <div style={{position: "absolute", left: 80, right: 80, top: 360, height: 2, background: "#DCC7DC"}} />
        <div style={{position: "absolute", left: 0, right: 0, top: 398, display: "flex", justifyContent: "center", ...enterA(f, 8, 12, 14)}}>
          <div style={{minWidth: 520, maxWidth: 860, height: 90, padding: "0 40px", borderRadius: 45, background: "linear-gradient(90deg, #F3E8F1, #EAD8EE)", boxShadow: "0 5px 14px #99739D14", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: ZH, fontSize: item.homophone.length > 16 ? 30 : 36, fontWeight: 500, letterSpacing: .5, color: "#505260", whiteSpace: "nowrap"}}>谐音 · {item.homophone}</div>
        </div>
        <div style={{position: "absolute", left: 0, right: 0, top: 524, display: "flex", justifyContent: "center", opacity: interpolate(f, [14, 26], [0, 1], {...clamp, easing: EASE}), transform: `scale(${interpolate(f, [14, 26], [.96, 1], {...clamp, easing: EASE})})`}}>
          <div style={{minWidth: 560, maxWidth: 880, minHeight: 140, padding: "10px 48px", borderRadius: 70, background: "linear-gradient(180deg, #FFF9F0, #FFF0D9)", border: `2px solid ${gold}`, boxShadow: "0 8px 20px #AD81351A", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: ZH, fontSize: item.chinese.length > 10 ? 54 : 70, fontWeight: 700, letterSpacing: 2, lineHeight: 1.3, color: "#102430", textAlign: "center"}}>{item.chinese}</div>
        </div>
        <div style={{position: "absolute", left: 80, top: 702, width: 804, height: 275}}>
          {item.photoSrc ? <div style={{position: "absolute", left: -10, right: -10, top: -6, height: 300, borderRadius: 34, overflow: "hidden", boxShadow: "0 10px 26px #10182730", ...enterA(f, 14, 16, 18)}}>
            <Img src={staticFile(item.photoSrc)} style={{width: "100%", height: "100%", objectFit: "cover", transform: `scale(${1.04 + f * 0.0004})`}} />
          </div> : hasBreak ? <div style={{display: "grid", gridTemplateColumns: `repeat(${Math.min(item.breakdown!.length, 4)}, minmax(0, 1fr))`, gap: 14, paddingTop: 30, ...enterA(f, 16, 18, 24)}}>
            {item.breakdown!.map((w, i) => {
              const on = item.wordTimings?.[i] && f / 30 + item.start >= item.wordTimings[i].start && f / 30 + item.start < item.wordTimings[i].end;
              return <div key={i} style={{borderRadius: 26, background: on ? "#FFE49C" : "#F4ECF5", border: `2px solid ${on ? gold : "#E6D6EA"}`, padding: "22px 8px", textAlign: "center"}}>
                <div style={{fontFamily: TH, fontSize: w.thai.length > 8 ? 34 : 42, fontWeight: 800, color: "#102430", lineHeight: 1.45}}>{w.thai}</div>
                <div style={{fontFamily: ZH, fontSize: 28, color: "#505260", marginTop: 6}}>{w.chinese}</div>
              </div>;
            })}
          </div> : isGrid ? <div style={{display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, paddingTop: 10, ...enterA(f, 16, 18, 24)}}>
            {shown.slice(-4).map((x, i, arr) => <div key={i} style={{height: 76, borderRadius: 22, padding: "0 20px", background: i === arr.length - 1 ? "#FFE49C" : "#F4ECF5", display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8}}>
              <span style={{fontFamily: TH, fontSize: x.thai.length > 12 ? 26 : 32, fontWeight: 800, color: "#102430"}}>{x.thai}</span>
              <span style={{fontFamily: ZH, fontSize: 22, color: "#505260"}}>{x.chinese}</span>
            </div>)}
          </div> : <>
            <svg width={804} height={275} style={{position: "absolute", inset: 0}}>
              <path d="M 0 210 C 160 170 300 230 430 205 C 560 180 690 220 804 195 L 804 275 L 0 275 Z" fill={`${accent}14`} />
              <ellipse cx={402} cy={246} rx={295} ry={16} fill="#2A273312" />
            </svg>
            {icons[1] ? <div style={{position: "absolute", left: 70, top: 120, fontSize: 104, transform: `rotate(-8deg) translateY(${-float}px)`, opacity: interpolate(f, [20, 34], [0, 1], clamp)}}>{icons[1]}</div> : null}
            <div style={{position: "absolute", left: 0, right: 0, top: 18, textAlign: "center", fontSize: 190, lineHeight: 1, ...enterA(f, 16, 18, -24), rotate: "-5deg", translate: `0 ${float}px`}}>{icons[0]}</div>
            {icons[2] ? <div style={{position: "absolute", right: 70, top: 60, fontSize: 104, transform: `rotate(8deg) translateY(${-float}px)`, opacity: interpolate(f, [20, 34], [0, 1], clamp)}}>{icons[2]}</div> : null}
          </>}
          {item.note ? <div style={{position: "absolute", left: 0, right: 0, bottom: -40, fontFamily: ZH, fontSize: 30, color: "#505260", textAlign: "center", lineHeight: 1.4}}>{item.note}</div> : null}
        </div>
      </div>
    </div>
    {item.photoSrc && hasBreak ? <div style={{position: "absolute", left: 70, right: 70, top: 1412, display: "grid", gridTemplateColumns: `repeat(${Math.min(item.breakdown!.length, 4)}, minmax(0, 1fr))`, gap: 12, ...enterA(f, 22, 14, 18)}}>
      {item.breakdown!.map((w, i) => {
        const on = item.wordTimings?.[i] && f / 30 + item.start >= item.wordTimings[i].start && f / 30 + item.start < item.wordTimings[i].end;
        return <div key={i} style={{borderRadius: 24, background: on ? gold : "rgba(16,24,39,.72)", border: `2px solid ${on ? gold : "rgba(255,255,255,.22)"}`, padding: "16px 6px", textAlign: "center"}}>
          <div style={{fontFamily: TH, fontSize: w.thai.length > 8 ? 34 : 42, fontWeight: 800, lineHeight: 1.4, color: on ? "#102430" : "#FFF7EC"}}>{w.thai}</div>
          <div style={{fontFamily: ZH, fontSize: 28, fontWeight: 600, marginTop: 4, color: on ? "#102430" : "#E9DCEB"}}>{w.chinese}</div>
        </div>;
      })}
    </div> : null}
    {item.pair ? <div style={{position: "absolute", left: 90, right: 90, top: 1418, borderRadius: 34, background: "rgba(16,24,39,.72)", border: `2px solid ${gold}`, padding: "20px 34px", display: "flex", alignItems: "center", gap: 26, ...enterA(f, 26, 14, 20)}}>
      {item.pair.icon ? <div style={{fontSize: 92, lineHeight: 1}}>{item.pair.icon}</div> : null}
      <div style={{flex: 1, minWidth: 0}}>
        <div style={{fontFamily: ZH, fontSize: 50, fontWeight: 800, color: "#FFF7EC", lineHeight: 1.3}}>配<span style={{color: gold}}>{item.pair.dish}</span></div>
        <div style={{fontFamily: ZH, fontSize: 36, fontWeight: 600, color: "#E9DCEB", lineHeight: 1.35, marginTop: 4}}>{item.pair.made}</div>
      </div>
    </div> : null}
  </AbsoluteFill>;
};

const Outro: React.FC<{p: ThaiLearningCardsProps}> = ({p}) => {
  const isVietnamese = p.seriesName.includes("越南语");
  const brand = isVietnamese ? "越南语千词" : "泰语千词";
  const country = isVietnamese ? "越南" : "泰国";
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame: frame - Math.round(p.outroStart * fps), fps, config: {damping: 18, stiffness: 110}});
  return <AbsoluteFill>
    <Background p={p} />
    <AbsoluteFill style={{background: "radial-gradient(circle at 50% 32%, rgba(255,211,111,.16), transparent 34%), linear-gradient(180deg, rgba(5,13,19,.14), rgba(5,13,19,.68))"}} />
    <div style={{position: "absolute", left: 70, right: 70, top: 395, opacity: enter, transform: `translateY(${(1-enter)*30}px)`, textAlign: "center"}}>
      <div style={{width: 250, height: 250, margin: "0 auto", borderRadius: 58, overflow: "hidden", boxShadow: "0 30px 80px rgba(0,0,0,.38), 0 0 0 3px rgba(255,211,111,.48)"}}>
        <Img src={staticFile(p.appIconSrc ?? "app/app_icon.png")} style={{width: "100%", height: "100%", objectFit: "cover"}} />
      </div>
      <div style={{fontFamily: ZH_SERIF, fontSize: 88, color: "#FFD36F", letterSpacing: 7, marginTop: 54}}>{brand}</div>
      <div style={{fontFamily: ZH, fontSize: 40, fontWeight: 800, color: "#FFF8E9", marginTop: 28}}>在{country}生活，够用了</div>
      <div style={{width: 230, height: 3, margin: "44px auto 0", background: "linear-gradient(90deg, transparent, #FFD36F, transparent)"}} />
      <div style={{fontFamily: ZH, fontSize: 27, color: "rgba(255,255,255,.76)", marginTop: 36}}>收藏这一集 · 下次直接开口</div>
    </div>
  </AbsoluteFill>;
};

const Recap: React.FC<{p: ThaiLearningCardsProps}> = ({p}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const words = p.recap?.words ?? [];
  return <AbsoluteFill>
    <Background p={p} />
    <Header p={p} label="最后复习" />
    <div style={{position: "absolute", left: 68, right: 68, top: 455, padding: "42px 42px 48px", borderRadius: 40, background: "rgba(255,255,255,.96)", borderLeft: `11px solid ${p.accent2 ?? "#F5C45A"}`, boxShadow: "0 30px 90px rgba(0,0,0,.30)"}}>
      <div style={{fontFamily: ZH, color: p.accent, fontSize: 26, fontWeight: 900, letterSpacing: 2}}>核心词复习</div>
      <div style={{fontFamily: ZH_SERIF, color: "#23343B", fontSize: 52, marginTop: 19, textAlign: "center"}}>这四个词，再听一遍</div>
      <div style={{display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 32}}>
        {words.map((word, index) => <div key={`${word.thai}-${index}`} style={{borderRadius: 22, padding: "22px 16px", textAlign: "center", background: t >= word.start && t < word.end ? (p.accent2 ?? "#F5C45A") : "#E8F3F0", border: "1px solid #CFDED9"}}>
          <div style={{fontFamily: TH, color: "#183B38", fontSize: 49, fontWeight: 800, lineHeight: 1.2}}>{word.thai}</div>
          <div style={{fontFamily: ZH, color: "#42655F", fontSize: 29, marginTop: 11}}>{word.chinese}</div>
        </div>)}
      </div>
    </div>
  </AbsoluteFill>;
};

export const ThaiLearningCards: React.FC<ThaiLearningCardsProps> = (p) => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  const index = p.items.findIndex((item) => t >= item.start && t < item.end);
  const speaking = (p.speechRanges ?? p.items.map((i) => ({start: i.start, end: i.end}))).some((r) => t >= r.start - .1 && t <= r.end + .1);
  const musicBase = (speaking ? .032 : .075) * (p.musicGain ?? 1);
  const musicVolume = musicBase * interpolate(t, [0, 1, p.durationSeconds - 2.2, p.durationSeconds], [0, 1, 1, 0], clamp);
  let scene: React.ReactNode;
  if (t < p.coverEnd) scene = p.coverImageSrc ? <CoverPhoto p={p} /> : <Cover p={p} />;
  else if (t >= p.outroStart) scene = <Outro p={p} />;
  else if (p.overview && t >= p.overview.start && t < p.overview.end) scene = <PosterOverview p={p} />;
  else if (p.posterReview && t >= p.posterReview.start && t < p.posterReview.end) scene = <PosterReview p={p} />;
  else if (p.recap && t >= p.recap.start && t < p.recap.end) scene = <Recap p={p} />;
  else if (index >= 0) scene = <MainCard p={p} item={p.items[index]} index={index} />;
  else {
    const fallback = p.items[Math.max(0, p.items.findIndex((item) => item.start > t) - 1)] ?? p.items[0];
    scene = fallback ? <MainCard p={p} item={fallback} index={Math.max(0, p.items.indexOf(fallback))} /> : <Cover p={p} />;
  }
  return <AbsoluteFill style={{background: "#071016"}}>
    {scene}
    <Audio src={staticFile(p.musicSrc)} volume={musicVolume} loop />
    <Audio src={staticFile(p.narrationSrc)} />
    <div style={{position: "absolute", left: 48, right: 48, bottom: 34, height: 4, borderRadius: 4, background: "rgba(255,255,255,.24)", overflow: "hidden"}}>
      <div style={{width: `${Math.min(100, t / p.durationSeconds * 100)}%`, height: "100%", background: `linear-gradient(90deg, ${p.accent}, ${p.accent2 ?? "#F5C45A"})`}} />
    </div>
  </AbsoluteFill>;
};
