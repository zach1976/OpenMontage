// 越 07 星期：一道七级台阶。越南语从星期一开始数"第二、第三……"，台阶上刻的就是那个序号，
// 小球每天往上跳一级；最高一级不是数字，是"主"—— 星期天单独叫主日。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, Books, End, ZH, VI, VI_SERIES, SeriesCtx, ease, sceneOf, calcMeta, cl} from "./Common";

type It={vi:string;zh:string;n:string};
export type SceneProps=BaseProps&{data:{items:It[]}};
const JADE="#0f5c4d",MINT="#c8f2e2",CORAL="#ff7a59",CREAM="#fffaf0",DIM="rgba(200,242,226,.35)";
const STEP_W=124,STEP_H=62,BASE=1060,X0=106;

const Stairs:React.FC<{t:number;m:Record<string,number>;i:number|undefined;items:It[]}>=({t,m,i,items})=>{
  const hop=i===undefined?0:interpolate(t,[m[`k${i}`],m[`k${i}`]+0.45],[0,1],cl);
  const bx=(k:number)=>X0+k*STEP_W+STEP_W/2,by=(k:number)=>BASE-(k+1)*STEP_H;
  const k=i??0,pk=Math.max(0,k-1);const x=i===undefined?bx(0):bx(pk)+(bx(k)-bx(pk))*hop;const y=(i===undefined?by(0):by(pk)+(by(k)-by(pk))*hop)-36-Math.sin(hop*Math.PI)*70;
  return <>{items.map((it,s)=>{const on=i!==undefined&&s<=i;const cur=s===i;return <div key={s} style={{position:"absolute",left:X0+s*STEP_W,top:BASE-(s+1)*STEP_H,width:STEP_W-6,height:(s+1)*STEP_H,background:cur?CORAL:on?MINT:"rgba(255,255,255,.08)",borderRadius:"10px 10px 0 0",display:"flex",justifyContent:"center"}}>
      <div style={{fontFamily:it.n==="主"?ZH:"Helvetica, sans-serif",fontWeight:900,fontSize:48,marginTop:6,color:cur?CREAM:on?JADE:DIM}}>{it.n}</div></div>;})}
    <div style={{position:"absolute",left:x-26,top:y,width:52,height:52,borderRadius:"50%",background:CREAM,boxShadow:"0 8px 18px rgba(0,0,0,.3)"}}/></>;};

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:JADE}}>
  <Brand color={MINT}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:CREAM,border:`2px solid ${CORAL}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 星期</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:140,color:CREAM,letterSpacing:4}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:CORAL,letterSpacing:6}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:1320,left:0,right:0,textAlign:"center",fontFamily:VI,fontSize:72,lineHeight:1.4,color:MINT}}>Thứ Hai</div>
</AbsoluteFill>;

const Week:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[6,5,4,3,2,1,0].find(k=>t>=m[`k${k}`]);const x=i!==undefined?p.data.items[i]:undefined;const a=i!==undefined?ease(t,m[`k${i}`],m[`k${i}`]+0.35):0;
  return <AbsoluteFill style={{background:JADE}}>
  <Brand color={MINT}/>
  <div style={{position:"absolute",top:330,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:64,color:CREAM,opacity:x?a:1}}>{x?<>{x.zh} = {x.n==="主"?<span style={{color:CORAL}}>主日</span>:<>第 <span style={{color:CORAL}}>{x.n}</span></>}</>:"从第二开始数"}</div>
  {x&&<div style={{position:"absolute",top:430,left:0,right:0,textAlign:"center",fontFamily:VI,fontSize:120,lineHeight:1.35,color:MINT,opacity:a}}>{x.vi}</div>}
  <Stairs t={t} m={m} i={i} items={p.data.items}/>
  {i!==undefined&&<div style={{position:"absolute",top:1105,left:190,width:700}}><FollowBar t={t} m={m} k={`k${i}`} fg={CORAL} track="rgba(255,255,255,.14)" muted={DIM} label={`${i+1} / 7`}/></div>}
  <div style={{position:"absolute",top:1245,left:80,right:80,display:"flex",flexWrap:"wrap",justifyContent:"center",gap:"12px 18px"}}>{p.data.items.map((q,k)=><div key={k} style={{fontFamily:VI,fontSize:38,lineHeight:1.4,color:i!==undefined&&k<=i?CREAM:DIM}}>{q.vi}</div>)}</div>
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:CREAM}}>
  <Brand color={JADE}/>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:84,color:JADE}}>国家级教学成果</div>
  <div style={{position:"absolute",top:470,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:60,color:CORAL}}>二等奖系列教材</div>
  <div style={{position:"absolute",top:600+(1-up)*60,left:110,opacity:up,transform:"rotate(-1.5deg)"}}><Books w={860} radius={14}/></div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <SeriesCtx.Provider value={VI_SERIES}><AbsoluteFill style={{background:JADE}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("week")} t={t}><Week p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, #17806b 0%, ${JADE} 75%)`} accent={CORAL}/></Layer>
  </AbsoluteFill></SeriesCtx.Provider>;};
export const calculateMetadata=calcMeta as any;
