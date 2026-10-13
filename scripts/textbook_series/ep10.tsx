// 10 吃饭：一张小票从打印口往下吐。说一句、打一行；说到"买单"，盖上红章。
// 一顿饭从坐下到结账，就是这张小票的长度。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, Books, End, ZH, TH, ease, sceneOf, calcMeta} from "./Common";

type Line={th:string;zh:string};
export type SceneProps=BaseProps&{data:{lines:Line[]}};

const ESP="#2a1d16",ESP2="#3c2a20",RCPT="#fffaf0",TOMATO="#e2452f",INK="#2b2420",GRAY="#9a8f84",CREAM="#f6e6cf";
const MONO="Menlo, SF Mono, monospace";
const thSize=(s:string)=>s.length>16?60:s.length>12?68:72;
const ROW=168,TOP=470;

const Zig:React.FC<{w:number;flip?:boolean}>=({w,flip})=><svg width={w} height={24} viewBox={`0 0 ${w} 24`} style={{display:"block",transform:flip?"scaleY(-1)":undefined}}><path d={`M0 0 ${Array.from({length:Math.ceil(w/24)}).map((_,i)=>`L${i*24+12} 22 L${i*24+24} 0`).join(" ")} L${w} 0 Z`} fill={RCPT}/></svg>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:`radial-gradient(ellipse at 50% 45%, ${ESP2} 0%, ${ESP} 75%)`}}>
  <Brand color={CREAM}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:CREAM,border:`2px solid ${TOMATO}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 点菜</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:CREAM,letterSpacing:6}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:CREAM,letterSpacing:4}}>点菜到<span style={{color:TOMATO}}>买单</span></div>
  <div style={{position:"absolute",top:1300,left:290,width:500}}>
    <div style={{background:RCPT,padding:"18px 30px",fontFamily:MONO,fontSize:28,color:INK,lineHeight:1.7}}>
      {p.data.lines.map((l,i)=><div key={i} style={{display:"flex",justifyContent:"space-between"}}><span>{String(i+1).padStart(2,"0")} {l.zh}</span><span>✓</span></div>)}
    </div><Zig w={500}/>
  </div>
</AbsoluteFill>;

const Receipt:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[4,3,2,1,0].find(k=>t>=m[`d${k}`])??0;const paid=ease(t,m.d4_a,m.d4_a+0.35);
  const shown=(k:number)=>ease(t,m[`d${k}`],m[`d${k}`]+0.4);
  const len=p.data.lines.reduce((a,_,k)=>a+ROW*shown(k),0);
  return <AbsoluteFill style={{background:`radial-gradient(ellipse at 50% 35%, ${ESP2} 0%, ${ESP} 75%)`}}>
  <Brand color={CREAM}/>
  <div style={{position:"absolute",top:340,left:130,right:130,height:40,borderRadius:20,background:"#120c09",boxShadow:"inset 0 6px 12px rgba(0,0,0,.6)"}}/>
  <div style={{position:"absolute",top:360,left:160,width:760,overflow:"hidden",height:110+len+30}}>
    <div style={{background:RCPT,padding:"40px 40px 10px",height:110+len,boxSizing:"border-box"}}>
      <div style={{display:"flex",justifyContent:"space-between",fontFamily:MONO,fontSize:30,color:GRAY,borderBottom:`3px dashed ${GRAY}`,paddingBottom:14}}><span>ร้านอาหาร</span><span>餐厅</span></div>
      {p.data.lines.map((l,k)=>{const s=shown(k);if(s<=0)return null;const cur=k===i;return <div key={k} style={{height:ROW*s,overflow:"hidden",borderBottom:`2px dotted ${GRAY}55`}}>
        <div style={{paddingTop:16,display:"flex",alignItems:"baseline",gap:18}}>
          <span style={{fontFamily:MONO,fontSize:32,color:cur?TOMATO:GRAY}}>{String(k+1).padStart(2,"0")}</span>
          <span style={{fontFamily:ZH,fontWeight:900,fontSize:46,color:cur?TOMATO:INK}}>{l.zh}</span>
        </div>
        <div style={{fontFamily:TH,fontSize:thSize(l.th),lineHeight:1.45,color:cur?INK:"#6d655e",paddingLeft:58}}>{l.th}</div>
      </div>;})}
    </div>
    <Zig w={760}/>
  </div>
  {paid>0&&<div style={{position:"absolute",top:360+110+len-30,right:110,transform:`rotate(-14deg) scale(${1.6-0.6*paid})`,opacity:paid,border:`8px solid ${TOMATO}`,color:TOMATO,borderRadius:20,padding:"6px 26px",fontFamily:ZH,fontWeight:900,fontSize:64}}>已买单</div>}
  <div style={{position:"absolute",top:1450,left:190,width:700}}><FollowBar t={t} m={m} k={`d${i}`} fg={TOMATO} track="rgba(246,230,207,.14)" muted={CREAM} label={`${i+1} / 5`}/></div>
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:`radial-gradient(ellipse at 50% 40%, ${ESP2} 0%, ${ESP} 75%)`}}>
  <Brand color={CREAM}/>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:CREAM}}>日常会话 · 前两册</div>
  <div style={{position:"absolute",top:520+(1-up)*60,left:110,opacity:up}}><Books w={860} shadow="0 30px 80px rgba(0,0,0,.6)"/></div>
  <div style={{position:"absolute",top:1340,left:0,right:0,display:"flex",justifyContent:"center",gap:20,opacity:ease(t,s.start+0.9,s.start+1.3)}}>{["大学泰语专业教材","附音频"].map(x=><div key={x} style={{fontFamily:ZH,fontWeight:900,fontSize:44,color:RCPT,background:TOMATO,borderRadius:18,padding:"10px 28px"}}>{x}</div>)}</div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:ESP}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("receipt")} t={t}><Receipt p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, ${ESP2} 0%, ${ESP} 75%)`} accent={CREAM}/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
