// 越 05 数字：数钱。第一遍像点钞一样一张张发出去叠成一摞；第二遍拿起每一张跟读；
// 最后一张是 10.000 ₫ —— 越南语说"十个千"，数字一下子用到了真钱上。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, Books, End, ZH, VI, VI_SERIES, SeriesCtx, ease, sceneOf, calcMeta} from "./Common";

type Num={n:number;vi:string};
export type SceneProps=BaseProps&{data:{nums:Num[];use:{vi:string;zh:string;parts:[string,string][]}}};

const TEAL="#0f6e64",TEAL2="#0a4f48",MINT="#e7f3ee",CORAL="#ff7a59",INK="#123b36",GRAY="#7a958f";
const NUMF="SF Pro Display, Helvetica Neue, sans-serif";

const Bill:React.FC<{n:string;w:number;sub?:string}>=({n,w,sub})=>{const h=w*0.47;return <div style={{width:w,height:h,borderRadius:w*.03,background:`linear-gradient(135deg, #3fb39f 0%, ${TEAL} 60%, #0c5a52 100%)`,position:"relative",overflow:"hidden",boxShadow:"0 14px 34px rgba(10,60,55,.35)"}}>
  <div style={{position:"absolute",inset:w*.025,border:`${w*.006}px solid rgba(231,243,238,.55)`,borderRadius:w*.02}}/>
  <div style={{position:"absolute",right:-w*.08,top:-w*.08,width:w*.5,height:w*.5,borderRadius:w,background:"rgba(231,243,238,.12)"}}/>
  <div style={{position:"absolute",left:w*.07,top:h*.12,fontFamily:NUMF,fontWeight:800,fontSize:h*(n.length>3?.42:.62),color:MINT,lineHeight:1}}>{n}</div>
  {sub&&<div style={{position:"absolute",right:w*.07,bottom:h*.12,fontFamily:VI,fontSize:h*.2,color:MINT}}>{sub}</div>}
</div>;};

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:MINT}}>
  <Brand color={TEAL}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:INK,border:`2px solid ${CORAL}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 数字</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:160,color:INK,letterSpacing:4}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:160,color:TEAL,letterSpacing:4}}>1<span style={{color:INK}}>到</span>10</div>
  <div style={{position:"absolute",top:1300,left:0,right:0,height:260}}>{[0,1,2,3,4].map(k=><div key={k} style={{position:"absolute",left:310+k*28,top:k*-6,transform:`rotate(${-14+k*7}deg)`,transformOrigin:"50% 120%"}}><Bill n={String([1,2,3,5,10][k])} w={420}/></div>)}</div>
</AbsoluteFill>;

const Count:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const pass2=t>=m.again;
  const idx=pass2?[...Array(10).keys()].reverse().find(i=>t>=m[`n${i}_a`]):[...Array(10).keys()].reverse().find(i=>t>=m[`p${i}`]);
  const dealt=pass2?10:(idx===undefined?0:idx+1);
  return <AbsoluteFill style={{background:MINT}}>
  <Brand color={TEAL}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:64,color:pass2?CORAL:GRAY}}>{pass2?"跟我读":"先听一遍"}</div>
  {!pass2&&p.data.nums.map((x,k)=>{if(k>=dealt)return null;const d=ease(t,m[`p${k}`],m[`p${k}`]+0.25);return <div key={k} style={{position:"absolute",left:190+(1-d)*500,top:520-k*4,transform:`rotate(${(k%3-1)*4+(1-d)*20}deg)`,opacity:d}}><Bill n={String(x.n)} w={700} sub={x.vi}/></div>;})}
  {pass2&&idx!==undefined&&(()=>{const x=p.data.nums[idx];const d=ease(t,m[`n${idx}_a`]-0.05,m[`n${idx}_a`]+0.2);return <>
    <div style={{position:"absolute",left:190,top:520-(1-d)*40,opacity:d}}><Bill n={String(x.n)} w={700}/></div>
    <div style={{position:"absolute",top:900,left:0,right:0,textAlign:"center",fontFamily:VI,fontSize:150,lineHeight:1.3,color:INK}}>{x.vi}</div>
    <div style={{position:"absolute",top:1120,left:190,width:700}}><FollowBar t={t} m={m} k={`n${idx}`} fg={CORAL} track="rgba(15,110,100,.14)" muted={GRAY} label={`${idx+1} / 10`}/></div>
  </>;})()}
  {!pass2&&idx!==undefined&&<div style={{position:"absolute",top:960,left:0,right:0,textAlign:"center",fontFamily:VI,fontSize:120,lineHeight:1.3,color:INK}}>{p.data.nums[idx].vi}</div>}
  <div style={{position:"absolute",top:1280,left:110,right:110,display:"flex",justifyContent:"space-between"}}>{p.data.nums.map((x,k)=>{const on=idx!==undefined&&k<=idx;return <div key={k} style={{width:72,height:40,borderRadius:6,background:on?TEAL:"rgba(15,110,100,.12)",color:on?MINT:GRAY,display:"flex",alignItems:"center",justifyContent:"center",fontFamily:NUMF,fontWeight:800,fontSize:24}}>{x.n}</div>;})}</div>
</AbsoluteFill>;};

const Use:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"use");const u=p.data.use;const a=ease(t,s.start,s.start+0.5);return <AbsoluteFill style={{background:MINT}}>
  <Brand color={TEAL}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:84,color:INK}}>一万越南盾</div>
  <div style={{position:"absolute",top:500,left:140,opacity:a,transform:`rotate(${-4*a}deg)`}}><Bill n="10.000" w={800} sub="đồng"/></div>
  <div style={{position:"absolute",top:930,left:40,right:40,display:"flex",justifyContent:"center",gap:24}}>{u.parts.map(([w,g])=><div key={w} style={{textAlign:"center"}}><div style={{fontFamily:VI,fontSize:84,lineHeight:1.35,color:w==="mười"||w==="nghìn"?CORAL:INK}}>{w}</div><div style={{fontFamily:ZH,fontWeight:800,fontSize:38,color:GRAY}}>{g}</div></div>)}</div>
  <div style={{position:"absolute",top:1130,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:60,color:TEAL}}>十个千 = 一万</div>
  {p.marks.u_f&&<div style={{position:"absolute",top:1260,left:190,width:700}}><FollowBar t={t} m={p.marks} k="u" fg={CORAL} track="rgba(15,110,100,.14)" muted={GRAY}/></div>}
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:MINT}}>
  <Brand color={TEAL}/>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:88,color:INK}}>4 册 · 每册 15–16 课</div>
  <div style={{position:"absolute",top:520+(1-up)*60,left:110,opacity:up}}><Books w={860} shadow="0 26px 60px rgba(10,60,55,.25)"/></div>
  <div style={{position:"absolute",top:1340,left:0,right:0,display:"flex",justifyContent:"center",gap:20,opacity:ease(t,s.start+0.9,s.start+1.3)}}>{["基础越南语","词汇分类手册"].map(x=><div key={x} style={{fontFamily:ZH,fontWeight:900,fontSize:44,color:MINT,background:TEAL,borderRadius:18,padding:"10px 28px"}}>{x}</div>)}</div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <SeriesCtx.Provider value={VI_SERIES}><AbsoluteFill style={{background:MINT}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("count")} t={t}><Count p={p} t={t}/></Layer>
    <Layer s={S("use")} t={t}><Use p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, ${TEAL} 0%, ${TEAL2} 75%)`} accent={MINT}/></Layer>
  </AbsoluteFill></SeriesCtx.Provider>;};
export const calculateMetadata=calcMeta as any;
