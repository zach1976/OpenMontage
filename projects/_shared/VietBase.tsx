import React from "react";
import { AbsoluteFill, continueRender, delayRender, interpolate, staticFile, useCurrentFrame } from "remotion";

// ---------------------------------------------------------------------------
// 越南语千词 · 越南名字系列 —— 共用的**引擎知识**，不是共用的创意组件。
//
// 这里只放：字体加载、系列身份色（朱漆描金，与已发布的越南语千词各集一致）、
// 品牌行、片尾屏。每一集的**版式结构与动作语言必须各自手写**，
// 见 CLAUDE.md「同一系列每集必须换视觉语言」。
// ---------------------------------------------------------------------------

const handle = delayRender("viet-fonts", { timeoutInMilliseconds: 240000 });
Promise.all([
  new FontFace("VietBold", `url(${staticFile("fonts/BeVietnamPro-Bold.ttf")})`).load(),
  new FontFace("VietSemi", `url(${staticFile("fonts/BeVietnamPro-SemiBold.ttf")})`).load(),
  new FontFace("SerifSC", `url(${staticFile("fonts/NotoSerifSC-Bold.otf")})`).load(),
])
  .then((f) => { f.forEach((x) => (document.fonts as FontFaceSet).add(x)); continueRender(handle); })
  .catch(() => continueRender(handle));

export const VI = "VietBold, sans-serif";
export const VI_S = "VietSemi, sans-serif";
export const ZH = "SerifSC, serif";

// 朱漆描金 —— 越南语千词的系列身份，五集都不变
export const LACQUER_D = "#5E1C18";
export const LACQUER = "#9E2B25";
export const LACQUER_L = "#B8382F";
export const GOLD = "#C9A24B";
export const GOLD_SOFT = "#E0C69C";
export const CREAM = "#F5EFE6";
export const INK = "#3A261C";
export const INK_SOFT = "#7A6254";

export const BrandLine: React.FC<{ label?: string; onDark?: boolean }> = ({ label, onDark = true }) => (
  <>
    <div style={{ position: "absolute", top: 128, width: "100%", textAlign: "center",
                  fontFamily: ZH, fontSize: 26, letterSpacing: 2,
                  color: onDark ? "rgba(245,239,230,0.82)" : INK_SOFT }}>
      越南语千词 app · 在越南生活够用了
    </div>
    {label ? (
      <div style={{ position: "absolute", top: 192, width: "100%", textAlign: "center",
                    fontFamily: ZH, fontSize: 38, letterSpacing: 8,
                    color: onDark ? GOLD_SOFT : LACQUER }}>
        {label}
      </div>
    ) : null}
  </>
);

/** 片尾：五集统一，系列身份在这里收口 */
export const VietOutro: React.FC<{
  outro: { line1: string; line2: string; cta: string; tags: string[] };
}> = ({ outro }) => {
  const frame = useCurrentFrame();
  const at = (d: number) =>
    interpolate(frame, [d, d + 14], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: LACQUER_D }}>
      <AbsoluteFill style={{ background: `radial-gradient(118% 62% at 50% 40%, ${LACQUER} 0%, ${LACQUER_D} 68%, #431310 100%)` }} />
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 8, background: GOLD }} />
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 8, background: GOLD }} />
      <BrandLine />
      <div style={{ position: "absolute", top: 452, left: (1080 - 236) / 2, width: 236, height: 236,
                    borderRadius: 52, overflow: "hidden", border: `3px solid rgba(201,162,75,0.6)`,
                    boxShadow: "0 16px 44px rgba(0,0,0,0.5)", opacity: at(0) }}>
        <img src={staticFile("app/app_icon.png")} style={{ width: "100%", height: "100%" }} />
      </div>
      <div style={{ position: "absolute", top: 748, width: "100%", textAlign: "center", fontFamily: ZH,
                    fontSize: 66, color: CREAM, opacity: at(0) }}>{outro.line1}</div>
      <div style={{ position: "absolute", top: 858, width: "100%", textAlign: "center", fontFamily: ZH,
                    fontSize: 104, color: GOLD, opacity: at(12),
                    textShadow: "0 6px 22px rgba(0,0,0,0.45)" }}>{outro.line2}</div>
      <div style={{ position: "absolute", top: 1042, width: "100%", display: "flex",
                    justifyContent: "center", opacity: at(26) }}>
        <div style={{ padding: "18px 52px", border: `3px solid ${GOLD}`, color: GOLD_SOFT,
                      fontFamily: ZH, fontSize: 42 }}>{outro.cta}</div>
      </div>
      <div style={{ position: "absolute", top: 1218, width: "100%", textAlign: "center", fontFamily: ZH,
                    fontSize: 32, color: "rgba(245,239,230,0.7)", opacity: at(26), letterSpacing: 2 }}>
        {outro.tags.join("  ")}
      </div>
    </AbsoluteFill>
  );
};
