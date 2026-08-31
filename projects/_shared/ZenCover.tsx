import React from "react";

// ---------------------------------------------------------------------------
// 禅意封面家具 v2（引擎知识，各集一份拷贝；创意在于**怎么摆**，不在这个文件）
//
// v1 挨了两轮否：先是「有点平」，改成不对称 + 巨字 + 圆相 + 闲章之后仍然
// 「还是不行，需要继续美化」。满幅看才明白 v1 错在哪 —— 三件都是**几何**，不是**笔墨**：
//
//   · 圆相是等粗的圆 + 一个缺口 = 加载动画的圈，不是一笔写出来的破圆。
//   · 巨字是一整块均匀的灰，糊在下半幅，看着像脏，不像远景。
//   · 闲章是圆角矩形 + 投影 = 一个 app 图标按钮，不是一方刻出来的石章。
//   · 而且整幅**没有明暗层次**：罩子把画面压成一片中灰，这才是"平"的真正来源。
//
// v2 的四条：
//   1. 圆相改成**填充路径**，从起笔到收笔粗细连续变化，末端出锋 —— 真的像一笔。
//   2. 巨字换成**远山剪影**（程序化多层墨色山形）：意境靠远近，不靠水印。
//   3. 闲章改成**不规则刻边 + 斑驳**，微微旋转，边缘有缺口。
//   4. 加 `InkWash`：一团各向异性的淡墨，给画面做出亮区/暗区 —— 层次先于装饰。
// ---------------------------------------------------------------------------

/**
 * 圆相（enso）。用**填充路径**画：外缘半径恒定，内缘半径沿角度渐变，
 * 于是笔画从起笔的粗一路收到收笔的细，末端自然出锋。
 * **不能闭合** —— 闭合了就是个圈，不是圆相。
 */
export const Enso: React.FC<{
  color: string; cx: number; cy: number; r: number; op?: number;
  rot?: number; sweep?: number; w0?: number; w1?: number; wobble?: number;
}> = ({ color, cx, cy, r, op = 0.22, rot = -30, sweep = 305, w0 = 13, w1 = 2.6, wobble = 2.2 }) => {
  const R = 88, N = 96;
  const outer: string[] = [], inner: string[] = [];
  for (let i = 0; i <= N; i++) {
    const t = i / N;
    const a = ((rot + t * sweep) * Math.PI) / 180;
    // 笔锋：起笔略顿 → 中段稳 → 收笔提细；再叠一点手抖，边缘就不是数学曲线
    const w = w0 * (1 - t) + w1 * t + Math.sin(t * 7.3) * 0.7;
    const jitter = Math.sin(t * 11.4 + 1.2) * wobble;
    const ro = R + jitter + w / 2, ri = R + jitter - w / 2;
    outer.push(`${(100 + ro * Math.cos(a)).toFixed(2)},${(100 + ro * Math.sin(a)).toFixed(2)}`);
    inner.push(`${(100 + ri * Math.cos(a)).toFixed(2)},${(100 + ri * Math.sin(a)).toFixed(2)}`);
  }
  const d = `M${outer.join("L")}L${inner.reverse().join("L")}Z`;
  return (
    <svg viewBox="0 0 200 200" style={{ position: "absolute", left: cx - r, top: cy - r,
                                        width: r * 2, height: r * 2, opacity: op,
                                        pointerEvents: "none" }}>
      <path d={d} fill={color} />
    </svg>
  );
};

/**
 * 远山：程序化的多层墨色山形。越远越淡越高，越近越深越低 —— 层次就是这么来的。
 * 比"巨大的淡汉字"干净得多：水印是糊，山是远。
 */
export const InkRidge: React.FC<{
  y: number; layers?: { h: number; color: string; seed: number; op: number }[];
}> = ({ y, layers }) => {
  const L = layers ?? [
    { h: 210, color: "#16242B", seed: 1.7, op: 0.34 },
    { h: 150, color: "#0D1A20", seed: 3.1, op: 0.46 },
    { h: 96, color: "#060F13", seed: 5.9, op: 0.62 },
  ];
  return (
    <>
      {L.map((ly, k) => {
        const pts: string[] = [];
        for (let x = 0; x <= 1080; x += 30) {
          const u = x / 1080;
          const h = ly.h * (0.42 + 0.58 * (
            0.5 + 0.5 * Math.sin(u * 6.1 + ly.seed) * Math.cos(u * 2.7 + ly.seed * 1.9)));
          pts.push(`${x},${(ly.h - h).toFixed(1)}`);
        }
        return (
          <svg key={k} viewBox={`0 0 1080 ${ly.h}`} preserveAspectRatio="none"
               style={{ position: "absolute", left: 0, top: y + (L[0].h - ly.h),
                        width: 1080, height: ly.h, opacity: ly.op, pointerEvents: "none" }}>
            <path d={`M0,${ly.h}L${pts.join("L")}L1080,${ly.h}Z`} fill={ly.color} />
          </svg>
        );
      })}
    </>
  );
};

/** 淡墨：一团各向异性的墨晕。作用是给画面**做出亮区和暗区**，层次先于装饰 */
export const InkWash: React.FC<{
  x: number; y: number; w: number; h: number; color: string; op?: number; blur?: number;
}> = ({ x, y, w, h, color, op = 0.5, blur = 120 }) => (
  <div style={{ position: "absolute", left: x - w / 2, top: y - h / 2, width: w, height: h,
                borderRadius: "50%", background: `radial-gradient(closest-side, ${color} 0%, rgba(0,0,0,0) 72%)`,
                filter: `blur(${blur}px)`, opacity: op, pointerEvents: "none" }} />
);

/**
 * 闲章：刻出来的，不是画出来的。
 * 不规则外框 + 边缘缺口 + 斑驳 + 微微歪一点。圆角矩形加投影只会读成 app 图标。
 */
export const Seal: React.FC<{
  ch: string; font: string; x: number; y: number; size?: number; op?: number; rot?: number;
}> = ({ ch, font, x, y, size = 92, op = 0.9, rot = -2.2 }) => {
  const S = 100, e = 4;
  // 四条边各自带一点起伏，四角略微磨圆磨缺 —— 石头被刻过、被磕过
  const edge = (a: number, b: number, k: number) =>
    `${a.toFixed(1)},${b.toFixed(1)}`;
  const pts = [
    edge(e + 1.6, e), edge(38, e - 1.2), edge(68, e + 1.4), edge(S - e, e + 0.6),
    edge(S - e + 1.1, 36), edge(S - e - 1.3, 66), edge(S - e - 0.4, S - e),
    edge(70, S - e + 1.2), edge(36, S - e - 1.1), edge(e + 0.8, S - e - 0.5),
    edge(e - 1.2, 64), edge(e + 1.3, 34),
  ].join(" ");
  return (
    <div style={{ position: "absolute", left: x, top: y, width: size, height: size,
                  opacity: op, transform: `rotate(${rot}deg)`, pointerEvents: "none" }}>
      <svg viewBox="0 0 100 100" style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}>
        <polygon points={pts} fill="#A5372A" />
        {/* 斑驳：几处漏刻的浅色缺口，章面才不是一块平红 */}
        <circle cx="22" cy="27" r="6.5" fill="#000" opacity="0.13" />
        <circle cx="79" cy="70" r="8.5" fill="#000" opacity="0.10" />
        <circle cx="63" cy="18" r="4.2" fill="#FFF" opacity="0.07" />
        <rect x="4" y="52" width="5" height="13" fill="#000" opacity="0.16" />
      </svg>
      <div style={{ position: "absolute", inset: 0, display: "flex",
                    alignItems: "center", justifyContent: "center" }}>
        <span style={{ fontFamily: font, fontSize: Math.round(size * 0.52), color: "#F4E9DC",
                       lineHeight: 1, transform: "translateY(-1px)", opacity: 0.94 }}>
          {ch}
        </span>
      </div>
    </div>
  );
};

/** 一条线，且**只有一条**。对称的一对横线是把画面钉平的元凶 */
export const Rule: React.FC<{
  x: number; y: number; w: number; color: string; op?: number; align?: "left" | "right";
}> = ({ x, y, w, color, op = 1, align = "left" }) => (
  <div style={{ position: "absolute", left: x, top: y, width: w, height: 1, opacity: op,
                background: align === "left"
                  ? `linear-gradient(90deg, ${color} 0%, ${color} 58%, rgba(0,0,0,0) 100%)`
                  : `linear-gradient(90deg, rgba(0,0,0,0) 0%, ${color} 42%, ${color} 100%)` }} />
);
