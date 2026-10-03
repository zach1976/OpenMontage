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

const clamp = {extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const};
const TH = '"Sarabun", "Noto Sans Thai", sans-serif';
const ZH = '"PingFang SC", "Noto Sans CJK SC", sans-serif';
const ZH_SERIF = '"STKaiti", "Kaiti SC", "Songti SC", serif';

export type ThaiLearningItem = {
  thai: string;
  homophone: string;
  chinese: string;
  breakdown?: {thai: string; chinese: string}[];
  wordTimings?: {start: number; end: number}[];
  note?: string;
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
  appIconSrc?: string;
  mode?: "grid" | "cards" | "food";
  items: ThaiLearningItem[];
  recap?: {start: number; end: number; words: {thai: string; chinese: string; start: number; end: number}[]} | null;
  speechRanges?: {start: number; end: number}[];
};

const Background: React.FC<{p: ThaiLearningCardsProps; item?: ThaiLearningItem}> = ({p, item}) => {
  const frame = useCurrentFrame();
  const zoom = interpolate(frame, [0, p.durationSeconds * 30], [1.02, 1.09], clamp);
  const src = item?.imageSrc ?? p.backgroundSrc;
  return <AbsoluteFill style={{background: `linear-gradient(155deg, ${p.accent} 0%, #101B25 62%, #071016 100%)`, overflow: "hidden"}}>
    {src ? <Img src={staticFile(src)} style={{position: "absolute", inset: -18, width: "calc(100% + 36px)", height: "calc(100% + 36px)", objectFit: "cover", transform: `scale(${zoom})`, filter: "saturate(1.05) contrast(1.03)"}} /> : null}
    <AbsoluteFill style={{background: src ? "linear-gradient(180deg, rgba(5,13,19,.20), rgba(5,13,19,.48) 58%, rgba(5,13,19,.86))" : "radial-gradient(circle at 80% 8%, rgba(255,255,255,.15), transparent 34%)"}} />
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
  const isThaiParcel = p.seriesName.includes("泰语千词 · 场景短句") && p.episode === "NO.21";
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

const Cover: React.FC<{p: ThaiLearningCardsProps}> = ({p}) => {
  const languageBrand = p.seriesName.includes("越南语") ? "越南语千词" : "泰语千词";
  const targetLanguage = p.seriesName.includes("越南语") ? "越南语" : "泰语";
  const country = p.seriesName.includes("越南语") ? "越南" : "泰国";
  const isFood = p.seriesName.includes("泰国美食");
  const isAddress = p.seriesName.includes("怎么称呼");
  const isThaiParcel = p.seriesName.includes("泰语千词 · 场景短句") && p.episode === "NO.21";
  const unit = isFood ? "个美食词" : "句实用表达";
  const episodeNumber = p.episode.replace(/[^0-9]/g, "") || p.episode;
  const episodeIndex = Math.max(0, Number(episodeNumber) - 1);
  const seriesOffset = p.seriesName.includes("紧急应急") ? 2 : isFood ? 4 : 0;
  const variant = (episodeIndex + seriesOffset) % 6;
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
      <div style={{position: "absolute", right: 52, bottom: 150, fontFamily: ZH, fontSize: 80, fontWeight: 950, color: gold, transform: "rotate(-90deg)", transformOrigin: "right bottom", letterSpacing: 5}}>NO.{episodeNumber}</div>
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
  const isSignboard = p.seriesName.includes("招牌识字") && phase === "lesson";
  if (isSignboard) return <AbsoluteFill>
    <Background p={p} item={item} />
    <AbsoluteFill style={{background: "linear-gradient(180deg, rgba(5,13,19,.28), transparent 20%, transparent 61%, rgba(5,13,19,.86) 82%, rgba(5,13,19,.96))"}} />
    <Header p={p} label={`${phaseIndex + 1} / ${phaseItems.length}`} />
    <div style={{position: "absolute", left: 80, right: 80, top: 600, textAlign: "center", opacity: progress, transform: `translateY(${(1-progress)*20}px)`}}>
      <div style={{fontFamily: TH, color: "#161B1E", fontSize: item.thai.length > 13 ? 68 : 82, lineHeight: 1.18, fontWeight: 900, textShadow: "0 2px 1px rgba(255,255,255,.28)"}}>{item.thai}</div>
    </div>
    <div style={{position: "absolute", left: 76, right: 76, bottom: 190, padding: "34px 38px 36px", borderRadius: 30, background: "rgba(250,247,239,.96)", borderTop: `8px solid ${p.accent2 ?? "#F5C45A"}`, boxShadow: "0 28px 70px rgba(0,0,0,.34)", opacity: progress}}>
      <div style={{fontFamily: ZH, color: p.accent, fontSize: 24, fontWeight: 950, letterSpacing: 4}}>真实招牌这样写</div>
      <div style={{fontFamily: ZH, color: "#647075", fontSize: 28, marginTop: 18, textAlign: "center"}}>谐音 · {item.homophone}</div>
      <div style={{fontFamily: ZH_SERIF, color: "#1D2B32", fontSize: 56, lineHeight: 1.2, marginTop: 14, textAlign: "center", fontWeight: 800}}>{item.chinese}</div>
    </div>
  </AbsoluteFill>;
  return <AbsoluteFill>
    <Background p={p} item={item} />
    <Header p={p} label={`${phaseIndex + 1} / ${phaseItems.length}`} />
    <div style={{position: "absolute", left: 68, right: 68, top: 455, minHeight: 500, padding: "40px 42px 38px", borderRadius: 40, background: "rgba(255,255,255,.95)", borderLeft: `11px solid ${p.accent2 ?? "#F5C45A"}`, boxShadow: "0 30px 90px rgba(0,0,0,.30)", opacity: progress, transform: `translateY(${(1-progress)*26}px)`}}>
      <div style={{fontFamily: ZH, color: p.accent, fontSize: 25, letterSpacing: 3, fontWeight: 900}}>{phase === "analysis" ? "常用词分析" : (p.seriesName.includes("越南语") ? "越南语先念" : "泰语先念")}</div>
      <div style={{fontFamily: TH, color: "#18262D", fontSize: item.thai.length > 22 ? 60 : 78, lineHeight: 1.18, fontWeight: 800, marginTop: 18, textAlign: "center"}}>{item.thai}</div>
      <div style={{height: 2, background: "#E5E2D8", margin: "30px 0 22px"}} />
      <div style={{fontFamily: ZH, color: "#6B777B", fontSize: 26, textAlign: "center"}}>谐音 · {item.homophone}</div>
      <div style={{fontFamily: ZH_SERIF, color: "#26343B", fontSize: 50, lineHeight: 1.25, marginTop: 22, textAlign: "center"}}>{item.chinese}</div>
      {item.breakdown?.length ? <div style={{marginTop: 25}}>
        <div style={{display: "grid", gridTemplateColumns: `repeat(${Math.min(item.breakdown.length, 4)}, minmax(0, 1fr))`, gap: 10}}>
          {item.breakdown.map((word, i) => <div key={`${word.thai}-${i}`} style={{borderRadius: 16, background: item.wordTimings?.[i] && frame / fps >= item.wordTimings[i].start && frame / fps < item.wordTimings[i].end ? (p.accent2 ?? "#F5C45A") : "#E8F3F0", padding: "13px 7px 14px", textAlign: "center", border: "1px solid #CFDED9"}}>
            <div style={{fontFamily: TH, color: "#183B38", fontSize: word.thai.length > 8 ? 26 : 31, fontWeight: 800, lineHeight: 1.2}}>{word.thai}</div>
            <div style={{fontFamily: ZH, color: "#42655F", fontSize: 23, marginTop: 7, lineHeight: 1.25}}>{word.chinese}</div>
          </div>)}
        </div>
      </div> : null}
      {item.note ? <div style={{fontFamily: ZH, color: "#68757A", fontSize: 25, lineHeight: 1.45, marginTop: 24, textAlign: "center"}}>{item.note}</div> : null}
    </div>
    {p.mode === "grid" ? <div style={{position: "absolute", left: 62, right: 62, top: 1090, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10}}>
      {shown.map((x, i) => <div key={`${x.thai}-${i}`} style={{height: 86, borderRadius: 18, padding: "10px 16px", background: i === index ? (p.accent2 ?? "#F5C45A") : "rgba(255,255,255,.84)", color: "#18262D", display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10, boxShadow: "0 8px 22px rgba(0,0,0,.12)"}}>
        <span style={{fontFamily: TH, fontSize: x.thai.length > 13 ? 25 : 30, fontWeight: 800}}>{x.thai}</span>
        <span style={{fontFamily: ZH, fontSize: 20, color: "#4F5D62"}}>{x.chinese}</span>
      </div>)}
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
  const musicBase = speaking ? .032 : .075;
  const musicVolume = musicBase * interpolate(t, [0, 1, p.durationSeconds - 2.2, p.durationSeconds], [0, 1, 1, 0], clamp);
  let scene: React.ReactNode;
  if (t < p.coverEnd) scene = <Cover p={p} />;
  else if (t >= p.outroStart) scene = <Outro p={p} />;
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
