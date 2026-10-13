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

export const Brand:React.FC<{color:string;top?:number}>=({color,top=270})=>{const c=React.useContext(SeriesCtx);return <div style={{position:"absolute",top,left:0,right:0,textAlign:"center",fontFamily:ZH,fontSize:32,fontWeight:700,letterSpacing:4,color}}>{c.brand}</div>;};

export const Layer:React.FC<{s:SceneT;t:number;first?:boolean;children:React.ReactNode}>=({s,t,first,children})=>{
  if(t<s.start-0.01||t>=s.end+0.3)return null;
  const o=Math.min(first?1:interpolate(t,[s.start,s.start+0.27],[0,1],cl),interpolate(t,[s.end,s.end+0.27],[1,0],cl));
  return <AbsoluteFill style={{opacity:o}}>{children}</AbsoluteFill>;
};

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
