// 系列身份与引擎：品牌行 / 场景淡入淡出 / 音轨 / 片尾（小黄车 + 学泰文字母）。
// 各集的创意组件不放这里 —— 每集在自己的 Composition.tsx 里从零写。
import React from "react";
import {AbsoluteFill, Audio, Img, Sequence, staticFile, interpolate, CalculateMetadataFunction} from "remotion";

export type SceneT={id:string;start:number;end:number;label:string;text:string};
export type BaseProps={fps:number;totalFrames:number;totalSeconds:number;num:string;cover:[string,string];marks:Record<string,number>;scenes:SceneT[];audio:{file:string;at:number}[];bgm:{file:string;volume:number}};

export const ZH="PingFang SC, Noto Sans CJK SC, sans-serif",TH="ThaiBold, Thonburi, sans-serif";
export const cl={extrapolateLeft:"clamp",extrapolateRight:"clamp"} as const;
export const ease=(t:number,a:number,b:number)=>{const x=interpolate(t,[a,b],[0,1],cl);return 1-Math.pow(1-x,3);};
export const sceneOf=(p:BaseProps,id:string)=>p.scenes.find(x=>x.id===id)!;

// 账号身份：泰语号用默认值；越南语号在各集 Scene 外层用 SeriesCtx.Provider 覆盖
export type Series={brand:string;app:string;appSub:string;icon:string;app2:string;app2Sub:string;icon2:string};
export const SeriesCtx=React.createContext<Series>({brand:"泰语千词 · 跟着教材学",app:"学泰文字母",appSub:"44 个辅音 跟着练",icon:"app/alpha_icon.png",app2:"泰语千词",app2Sub:"1000 个常用词 背单词",icon2:"app/qianci_icon.png"});
export const VI="VietBold, Helvetica Neue, sans-serif";
export const VI_SERIES:Series={brand:"越南语千词 · 跟着教材学",app:"学越南语字母",appSub:"29 个字母 跟着练",icon:"app/viet_alpha_icon.png",app2:"越南语千词",app2Sub:"1000 个常用词 背单词",icon2:"app/viet_qianci_icon.png"};

export const Brand:React.FC<{color:string;top?:number}>=({color,top=270})=>{const c=React.useContext(SeriesCtx);return <div style={{position:"absolute",top,left:0,right:0,textAlign:"center",fontFamily:ZH,fontSize:40,fontWeight:800,letterSpacing:4,color}}>{c.brand}</div>;};

export const Layer:React.FC<{s:SceneT;t:number;first?:boolean;children:React.ReactNode}>=({s,t,first,children})=>{
  if(t<s.start-0.01||t>=s.end+0.3)return null;
  const o=Math.min(first?1:interpolate(t,[s.start,s.start+0.27],[0,1],cl),interpolate(t,[s.end,s.end+0.27],[1,0],cl));
  // 2026-11 美化（ChatGPT 稿）：正文场景放到「书桌上的一页教材」里。封面（第一帧）与片尾不套。
  if(s.id==="cover"||s.id==="end")return <AbsoluteFill style={{opacity:o}}>{children}</AbsoluteFill>;
  return <AbsoluteFill style={{opacity:o}}><Desk snap={s.id!=="book"}>{children}</Desk></AbsoluteFill>;
};

/* ── 书桌外壳：桌面 + 垫底教材 + 纸（=原场景缩 0.9）+ 长尾夹 + 铅笔 + 叶影 ──
   纸的颜色就是这一集原来的背景色，所以各集的配色与对比度不变（深色集自然是深色纸）。 */
export const DeskCtx=React.createContext<{desk:string;deskDark:string;book:string}>({desk:"#9A8670",deskDark:"#5B4B3E",book:"#8E3B34"});
const PX=54,PY=112,PW=972,PH=1728,K=0.9;
const Clip:React.FC=()=><svg width="112" height="95" viewBox="0 0 112 95" style={{position:"absolute",left:PX+70,top:PY-52,transform:"rotate(-3deg)",filter:"drop-shadow(4px 7px 4px #2D211C55)"}}>
  <path d="M27 43 V18 C27 -4 85 -4 85 18 V43" fill="none" stroke="#D7AB64" strokeWidth="8"/>
  <rect x="8" y="40" width="96" height="45" rx="4" fill="#BA8C49" stroke="#765225" strokeWidth="3"/>
  <path d="M14 47 H98" stroke="#FBE1A3" strokeWidth="4" opacity=".75"/></svg>;
const Pencil:React.FC=()=><div style={{position:"absolute",left:-40,top:1835,width:360,height:26,transform:"rotate(-12deg)",transformOrigin:"left center",filter:"drop-shadow(4px 7px 6px #30211D55)"}}>
  <div style={{position:"absolute",left:0,top:0,width:0,height:0,borderTop:"13px solid transparent",borderBottom:"13px solid transparent",borderRight:"40px solid #DDBD8B"}}/>
  <div style={{position:"absolute",left:0,top:9,width:0,height:0,borderTop:"4px solid transparent",borderBottom:"4px solid transparent",borderRight:"13px solid #33302F"}}/>
  <div style={{position:"absolute",left:40,top:0,width:320,height:26,borderRadius:3,background:"linear-gradient(180deg,#C75D51 0%,#A84540 45%,#7F302E 100%)"}}/></div>;
const Leaf:React.FC=()=><svg width="380" height="400" viewBox="0 0 380 400" style={{position:"absolute",right:-60,top:-30,opacity:.2,filter:"blur(16px)"}}>
  <path d="M330 -20 C270 110 180 160 105 240" stroke="#2E3B26" strokeWidth="13" fill="none"/>
  <path d="M258 80 Q160 25 162 -45 Q245 -5 258 80Z" fill="#2E3B26"/><path d="M210 142 Q95 90 106 20 Q193 54 210 142Z" fill="#2E3B26"/>
  <path d="M160 210 Q50 190 40 120 Q130 130 160 210Z" fill="#2E3B26"/></svg>;
/* 教材贴片：纸面右下角一张拍立得 + 胶带（规格「下半屏填法 A：教材截图贴片」，也给带货加一道曝光） */
const BookSnap:React.FC=()=><div style={{position:"absolute",left:700,top:1548,width:262,padding:"12px 12px 0",background:"#FFFDF8",transform:"rotate(5deg)",boxShadow:"0 14px 30px #2D211C55"}}>
  <Img src={staticFile("img/books.png")} style={{display:"block",width:238,height:206,objectFit:"cover"}}/>
  <div style={{fontFamily:ZH,fontSize:26,fontWeight:800,color:"#6B4A3A",textAlign:"center",padding:"10px 0 12px",letterSpacing:4}}>配套教材</div>
  <div style={{position:"absolute",left:66,top:-16,width:130,height:32,background:"#E7C78E",opacity:.7,transform:"rotate(-4deg)",boxShadow:"0 3px 5px #6A4B2926"}}/>
</div>;
export const Desk:React.FC<{children:React.ReactNode;snap?:boolean}>=({children,snap})=>{const d=React.useContext(DeskCtx);return <AbsoluteFill style={{background:`radial-gradient(ellipse at 24% 10%, rgba(255,240,215,.35) 0%, transparent 55%), linear-gradient(145deg, ${d.desk} 0%, ${d.deskDark} 100%)`,overflow:"hidden"}}>
  {/* 垫底教材：封皮 + 书页边 */}
  <div style={{position:"absolute",left:PX-30,top:PY+40,width:PW+40,height:PH,borderRadius:30,background:d.book,transform:"rotate(2deg)",boxShadow:"0 22px 35px #20191655"}}/>
  <div style={{position:"absolute",left:PX-8,top:PY+18,width:PW+12,height:PH,borderRadius:32,background:"repeating-linear-gradient(90deg,#EFE4D0 0 6px,#E2D3BA 6px 7px)",transform:"rotate(.8deg)",boxShadow:"0 6px 12px #20191633"}}/>
  {/* 纸：原场景按 0.9 缩放 */}
  <div style={{position:"absolute",left:PX,top:PY,width:PW,height:PH,borderRadius:36,overflow:"hidden",transform:"rotate(-.4deg)",boxShadow:"0 30px 75px #34201955, 0 8px 18px #3420192F"}}>
    <div style={{position:"absolute",left:0,top:0,width:1080,height:1920,transform:`scale(${K})`,transformOrigin:"0 0"}}>{children}</div>
    <svg width={PW} height={PH} style={{position:"absolute",inset:0,opacity:.05,mixBlendMode:"multiply",pointerEvents:"none"}}><filter id="paperNoise"><feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" seed="7" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter><rect width="100%" height="100%" filter="url(#paperNoise)"/></svg>
    <div style={{position:"absolute",inset:0,borderRadius:36,boxShadow:"inset 0 2px 4px #FFFFFFA6, inset 0 0 0 1px rgba(0,0,0,.06)",pointerEvents:"none"}}/>
  </div>
  {snap?<BookSnap/>:null}<Clip/><Pencil/><Leaf/>
</AbsoluteFill>;};

export const Track:React.FC<{p:BaseProps}>=({p})=><>
  <style>{`@font-face{font-family:ThaiBold;src:url("${staticFile("fonts/Sarabun-Bold.ttf")}")}@font-face{font-family:VietBold;src:url("${staticFile("fonts/BeVietnamPro-Bold.ttf")}")}`}</style>
  <Audio src={staticFile(`audio/${p.bgm.file}`)} volume={p.bgm.volume}/>
  {p.audio.map((a,i)=><Sequence key={i} from={Math.round(a.at*p.fps)}><Audio src={staticFile(`audio/${a.file}`)}/></Sequence>)}
</>;

/* 跟读状态条：听 → 你来读 */
export const FollowBar:React.FC<{t:number;m:Record<string,number>;k:string;fg:string;track:string;muted:string;label?:string}>=({t,m,k,fg,track,muted,label})=>{
  const f=m[`${k}_f`],e=m[`${k}_e`];const listening=t<f;const prog=interpolate(t,[f,e],[0,1],cl);
  return <div><div style={{display:"flex",justifyContent:"space-between",fontFamily:ZH,fontWeight:800,fontSize:44,color:listening?muted:fg}}><span>{listening?"听两遍":"你来读"}</span><span style={{color:muted}}>{label}</span></div>
  <div style={{marginTop:12,height:12,borderRadius:8,background:track}}><div style={{height:12,borderRadius:8,width:`${prog*100}%`,background:fg}}/></div></div>;
};

/* 教材合照卡 */
export const Books:React.FC<{w:number;radius?:number;shadow?:string}>=({w,radius=26,shadow="0 26px 70px rgba(0,0,0,.25)"})=><div style={{width:w,height:w*816/900,borderRadius:radius,overflow:"hidden",background:"#fff",boxShadow:shadow}}><Img src={staticFile("img/books.png")} style={{width:"100%",height:"100%",objectFit:"cover"}}/></div>;

/* 片尾：系列不变的部分，只换底色 */
export const End:React.FC<{p:BaseProps;t:number;bg:string;accent:string}>=({p,t,bg,accent})=>{const c=React.useContext(SeriesCtx);const s=sceneOf(p,"end");const bob=Math.sin((t-s.start)*6)*14;const app=ease(t,p.marks.outro-0.2,p.marks.outro+0.3);return <AbsoluteFill style={{background:bg}}>
  <Brand color={accent}/>
  <div style={{position:"absolute",top:380,left:230}}><Books w={620}/></div>
  <div style={{position:"absolute",top:1000,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:96,color:"#fff"}}>点左下角<span style={{color:"#ffd34d"}}>小黄车</span></div>
  <div style={{position:"absolute",top:1150,left:60,right:60,display:"flex",justifyContent:"center",gap:26,opacity:app,transform:`translateY(${(1-app)*30}px)`}}>
    {[[c.icon2,c.app2,c.app2Sub],[c.icon,c.app,c.appSub]].map(([ic,name,sub])=><div key={name} style={{flex:1,display:"flex",alignItems:"center",gap:18,background:"rgba(255,255,255,.1)",borderRadius:28,padding:"16px 20px"}}>
      <Img src={staticFile(ic)} style={{width:112,height:112,borderRadius:26,border:`3px solid ${accent}`}}/>
      <div style={{fontFamily:ZH,color:"#fff"}}><div style={{fontSize:44,fontWeight:900}}>{name}</div><div style={{fontSize:28,color:accent}}>{sub}</div></div>
    </div>)}
  </div>
  <svg style={{position:"absolute",left:120,top:1360+bob}} width="220" height="200" viewBox="0 0 220 200"><path d="M200 10 Q 120 40 50 150" stroke="#ffd34d" strokeWidth="14" fill="none" strokeLinecap="round"/><path d="M28 112 L 44 170 L 98 150" stroke="#ffd34d" strokeWidth="14" fill="none" strokeLinecap="round" strokeLinejoin="round"/></svg>
</AbsoluteFill>;};

export const calcMeta:CalculateMetadataFunction<BaseProps>=async({props})=>({durationInFrames:props.totalFrames,fps:props.fps,width:1080,height:1920});

/* 书页裁图（书本素材版用）：白底细框 + 投影，图在 public/book/<name>.png */
export const BookPeek:React.FC<{name:string;w?:number;h?:number;rot?:number;shadow?:string}>=({name,w,h,rot=0,shadow="0 14px 36px rgba(0,0,0,.18)"})=>
  <div style={{display:"inline-block",background:"#fff",padding:10,borderRadius:8,boxShadow:shadow,transform:`rotate(${rot}deg)`}}>
    <Img src={staticFile(`book/${name}.png`)} style={{display:"block",...(w?{width:w}:{}),...(h?{height:h}:{}),...(w&&h?{objectFit:"contain"}:{})}}/>
  </div>;
