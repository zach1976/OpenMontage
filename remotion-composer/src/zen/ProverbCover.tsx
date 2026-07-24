import React from "react";
import { AbsoluteFill, Img, staticFile, continueRender, delayRender } from "remotion";

const handle = delayRender("proverb-cover-fonts", { timeoutInMilliseconds: 120000 });
Promise.all([
  new FontFace("SarabunBold", `url(${staticFile("zen/fonts/Sarabun-Bold.ttf")})`).load(),
  new FontFace("NotoSerifSCBold", `url(${staticFile("zen/fonts/NotoSerifSC-Bold-subset.woff2")})`).load(),
]).then((fonts) => { fonts.forEach((f) => (document.fonts as FontFaceSet).add(f)); continueRender(handle); }).catch(() => continueRender(handle));

const THAI = "SarabunBold, sans-serif";
const ZH = "NotoSerifSCBold, serif";
const GOLD = "#E4C06B";
const CREAM = "#F3ECDD";

export const ProverbCover: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#0a1420" }}>
    <Img src={staticFile("zen/scenes/cover_proverb_bg.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
    <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(4,8,14,0.6) 0%, rgba(4,8,14,0.35) 40%, rgba(4,8,14,0.8) 100%)" }} />
    <AbsoluteFill style={{ background: "radial-gradient(70% 44% at 50% 46%, rgba(4,8,14,0.45) 0%, rgba(4,8,14,0) 72%)" }} />
    <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 8, background: GOLD }} />
    <div style={{ position: "absolute", top: 150, left: 0, right: 0, textAlign: "center", fontFamily: ZH, fontSize: 40, letterSpacing: 8, color: "rgba(243,236,221,0.7)", textShadow: "0 2px 12px rgba(0,0,0,0.7)" }}>
      泰国谚语 · 每天学一句
    </div>
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      <div style={{ textAlign: "center", padding: "0 70px" }}>
        <div style={{ fontFamily: ZH, fontSize: 82, lineHeight: 1.4, color: CREAM, textShadow: "0 3px 24px rgba(0,0,0,0.8)" }}>
          近朱者赤
          <div>近墨者黑</div>
        </div>
        <div style={{ width: 90, height: 3, background: GOLD, opacity: 0.6, margin: "56px auto" }} />
        <div style={{ fontFamily: THAI, fontSize: 44, color: GOLD, lineHeight: 1.5, textShadow: "0 3px 20px rgba(0,0,0,0.7)" }}>
          คบคนพาล  พาลพาไปหาผิด
        </div>
        <div style={{ fontFamily: THAI, fontSize: 44, color: GOLD, lineHeight: 1.5, marginTop: 6, textShadow: "0 3px 20px rgba(0,0,0,0.7)" }}>
          คบบัณฑิต  บัณฑิตพาไปหาผล
        </div>
      </div>
    </AbsoluteFill>
    <div style={{ position: "absolute", bottom: 128, left: 0, right: 0, display: "flex", justifyContent: "center", alignItems: "center", gap: 22 }}>
      <Img src={staticFile("zen/app/app_icon.png")} style={{ width: 72, height: 72, borderRadius: 16 }} />
      <div style={{ fontFamily: ZH, fontSize: 46, color: CREAM, letterSpacing: 2, textShadow: "0 2px 12px rgba(0,0,0,0.8)" }}>泰语千词</div>
    </div>
    <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 8, background: GOLD }} />
  </AbsoluteFill>
);
