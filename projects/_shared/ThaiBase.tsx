import React from "react";
import { loadFonts, ZH_TITLE, ZH_UI } from "./CjkFonts";
import { AbsoluteFill, interpolate, staticFile, useCurrentFrame } from "remotion";

// ---------------------------------------------------------------------------
// 泰语千词 · 卡片式各集共用的**引擎知识**，不是共用的创意组件。
// 只放：字体加载、系列身份色、片尾屏。每一集的版式与动作语言各自手写。
// ---------------------------------------------------------------------------

loadFonts([["ThaiBold", "Sarabun-Bold.ttf"], ["ThaiReg", "Sarabun-Regular.ttf"], ["SerifSC", "NotoSerifSC-Bold.otf"]]);

export const TH = "ThaiBold, sans-serif";
export const TH_R = "ThaiReg, sans-serif";
export const ZH = ZH_TITLE;
export const ZH_S = ZH_UI;

// 描金 —— 泰语千词的系列身份，片尾恒定
export const GOLD = "#C9A24B";
export const GOLD_SOFT = "#E5CFA0";
export const CREAM = "#F1E8DC";

export const ThaiOutro: React.FC<{
  outro: { line1: string; line2: string; cta: string; tags: string[] };
}> = ({ outro }) => {
  const frame = useCurrentFrame();
  const at = (d: number) =>
    interpolate(frame, [d, d + 14], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: "#14100C" }}>
      <AbsoluteFill style={{ background: "radial-gradient(118% 62% at 50% 40%, #33261A 0%, #14100C 70%)" }} />
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 8, background: GOLD }} />
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 8, background: GOLD }} />
      <div style={{ position: "absolute", top: 128, width: "100%", textAlign: "center", fontFamily: ZH_S,
                    fontSize: 26, letterSpacing: 2, color: "rgba(241,232,220,0.8)" }}>
        泰语千词 app · 在泰国生活够用了
      </div>
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
                      fontFamily: ZH_S, fontSize: 42 }}>{outro.cta}</div>
      </div>
      <div style={{ position: "absolute", top: 1218, width: "100%", textAlign: "center", fontFamily: ZH_S,
                    fontSize: 32, color: "rgba(241,232,220,0.7)", opacity: at(26), letterSpacing: 2 }}>
        {outro.tags.join("  ")}
      </div>
    </AbsoluteFill>
  );
};
