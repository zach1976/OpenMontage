// 15 星期几：一张台历。下面一排七格星期，每格用泰国习惯的"星期色"（一黄二粉三绿四橙五蓝六紫日红），
// 句子说到哪几天，哪几格就亮起来 —— 上课的五天、休息的两天一眼分开。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, BookPeek, End, ZH, TH, ease, sceneOf, calcMeta} from "./Common";

type Line={th:string;zh:string;days:number[]};
export type SceneProps=BaseProps&{data:{lines:Line[];week:[string,string][]}};
const PAPER="#fbfaf7",RED="#d7263d",INK="#1f2430",GRAY="#9097a3";
const DAY=["#f4c430","#f78fb3","#3bb273","#f28c28","#3a7bd5","#8e5ad8","#e23d3d"];
const thSize=(s:string)=>s.length>24?60:s.length>16?70:86;

const Week:React.FC<{w:[string,string][];lit:number[];top:number;small?:boolean}>=({w,lit,top,small})=><div style={{position:"absolute",top,left:40,right:40,display:"flex",gap:10}}>
  {w.map(([th,zh],k)=>{const on=lit.includes(k);return <div key={k} style={{flex:1,height:small?120:220,borderRadius:18,background:on?DAY[k]:"#fff",border:`4px solid ${DAY[k]}`,opacity:on||!lit.length?1:.35,display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",transform:`translateY(${on?-10:0}px)`}}>
    <div style={{fontFamily:ZH,fontWeight:900,fontSize:small?34:52,color:on?"#fff":INK}}>{zh}</div>
    {!small&&<div style={{fontFamily:TH,fontSize:30,lineHeight:1.5,color:on?"#fff":GRAY}}>{th}</div>}
  </div>;})}
</div>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:PAPER}}>
  <div style={{position:"absolute",top:0,left:0,right:0,height:250,background:RED}}/>
  <Brand color={RED}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:INK,border:`2px solid ${RED}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 年月日</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:160,color:INK,letterSpacing:4}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:160,color:RED,letterSpacing:6}}>{p.cover[1]}</div>
  <Week w={p.data.week} lit={[0,1,2,3,4,5,6]} top={1300} small/>
</AbsoluteFill>;

const Cal:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[3,2,1,0].find(k=>t>=m[`w${k}`])??0;const l=p.data.lines[i];const a=ease(t,m[`w${i}`],m[`w${i}`]+0.35);
  return <AbsoluteFill style={{background:PAPER}}>
  <div style={{position:"absolute",top:0,left:0,right:0,height:250,background:RED}}/>
  <Brand color="#fff" top={200}/>
  <div style={{position:"absolute",top:330,left:70,right:70,height:420,borderRadius:30,background:"#fff",boxShadow:"0 20px 50px rgba(31,36,48,.12)",display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",opacity:a,transform:`translateY(${(1-a)*30}px)`}}>
    <div style={{fontFamily:ZH,fontWeight:900,fontSize:84,color:RED}}>{l.zh}</div>
    <div style={{fontFamily:TH,fontSize:thSize(l.th),lineHeight:1.5,color:INK,padding:"0 30px",textAlign:"center"}}>{l.th}</div>
  </div>
  <Week w={p.data.week} lit={l.days} top={820}/>
  <div style={{position:"absolute",top:1110,left:190,width:700}}><FollowBar t={t} m={m} k={`w${i}`} fg={RED} track="rgba(215,38,61,.12)" muted={GRAY} label={`${i+1} / 4`}/></div>
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:PAPER}}>
  <div style={{position:"absolute",top:0,left:0,right:0,height:250,background:RED}}/>
  <Brand color="#fff" top={200}/>
  <div style={{position:"absolute",top:330,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:INK}}>第 <span style={{color:RED}}>2</span> 册 · 第 <span style={{color:RED}}>3</span> 课</div>
  <div style={{position:"absolute",top:490+(1-up)*60,left:0,right:0,display:"flex",justifyContent:"center",opacity:up}}><BookPeek name="dlg" w={820} rot={-1.5}/></div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:PAPER}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("cal")} t={t}><Cal p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, ${RED} 0%, #7d1020 75%)`} accent="#ffe08a"/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
