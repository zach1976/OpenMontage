// 越 04 按情景背：一张思维导图。中心是一个情景"餐厅"，词一个个作为叶子长出来、连上线 ——
// 这正是分类手册的组织方式：词不是孤零零的，是挂在情景上的。
import React from "react";
import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, Books, End, ZH, VI, VI_SERIES, SeriesCtx, ease, sceneOf, calcMeta} from "./Common";

type Word={vi:string;zh:string};
export type SceneProps=BaseProps&{data:{theme:string;words:Word[]}};

const RED="#c8102e",RED2="#9c0c23",GOLD="#d9b25f",WHITE="#fffaf3",INK="#3a1018",GRAY="#9b8a7e";
const CX=540,CY=900,R=355;
const pos=(k:number)=>{const a=(-90+k*72)*Math.PI/180;return [CX+R*Math.cos(a),CY+R*Math.sin(a)];};

const Medal:React.FC<{big:string;small:string;size:number}>=({big,small,size})=><div style={{width:size,height:size,borderRadius:size,border:`${size*.05}px solid ${GOLD}`,background:RED,display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",color:WHITE,fontFamily:ZH,fontWeight:900,lineHeight:1.1}}><div style={{fontSize:size*.26}}>{big}</div><div style={{fontSize:size*.17}}>{small}</div></div>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:`radial-gradient(ellipse at 50% 45%, ${RED} 0%, ${RED2} 75%)`}}>
  <Brand color={GOLD}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:WHITE,border:`2px solid ${GOLD}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 词汇</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:160,color:WHITE,letterSpacing:4}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:160,color:GOLD,letterSpacing:4}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:1310,left:0,right:0,display:"flex",justifyContent:"center",gap:30}}><Medal big="8000+" small="词汇" size={170}/><Medal big="8 大" small="主题" size={170}/><Medal big="32 个" small="情景" size={170}/></div>
</AbsoluteFill>;

const Node:React.FC<{t:number;at:number;label:string}>=({t,at,label})=>{const a=ease(t,at,at+0.4);return <div style={{position:"absolute",left:CX-150,top:CY-150,width:300,height:300,borderRadius:200,background:RED,border:`10px solid ${GOLD}`,color:WHITE,display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",transform:`scale(${a})`,boxShadow:"0 20px 60px rgba(200,16,46,.35)"}}>
  <div style={{fontFamily:ZH,fontSize:34,fontWeight:700,color:GOLD}}>情景</div><div style={{fontFamily:ZH,fontWeight:900,fontSize:96}}>{label}</div></div>;};

const Theme:React.FC<{p:SceneProps;t:number}>=({p,t})=><AbsoluteFill style={{background:WHITE}}>
  <Brand color={RED}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:72,color:INK}}>32 个情景之一</div>
  <Node t={t} at={p.marks.theme} label={p.data.theme}/>
</AbsoluteFill>;

const MindMap:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[4,3,2,1,0].find(k=>t>=m[`r${k}`])??0;
  return <AbsoluteFill style={{background:WHITE}}>
  <Brand color={RED}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:72,color:INK}}>在餐厅，一起记</div>
  <svg style={{position:"absolute",left:0,top:0}} width={1080} height={1920}>{p.data.words.map((_,k)=>{if(t<m[`r${k}`])return null;const g=ease(t,m[`r${k}`],m[`r${k}`]+0.4);const [x,y]=pos(k);return <line key={k} x1={CX} y1={CY} x2={CX+(x-CX)*g} y2={CY+(y-CY)*g} stroke={k===i?RED:GOLD} strokeWidth={k===i?10:6} strokeLinecap="round"/>;})}</svg>
  <Node t={t} at={-1} label={p.data.theme}/>
  {p.data.words.map((w,k)=>{if(t<m[`r${k}`])return null;const g=ease(t,m[`r${k}`]+0.2,m[`r${k}`]+0.5);const [x,y]=pos(k);const on=k===i;return <div key={k} style={{position:"absolute",left:x-160,top:y-85,width:320,height:170,borderRadius:26,background:on?RED:"#fff",border:`5px solid ${on?RED:GOLD}`,boxShadow:on?"0 18px 40px rgba(200,16,46,.3)":"0 8px 20px rgba(58,16,24,.08)",display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",transform:`scale(${g*(on?1.08:1)})`}}>
    <div style={{fontFamily:VI,fontSize:60,lineHeight:1.3,color:on?WHITE:INK}}>{w.vi}</div>
    <div style={{fontFamily:ZH,fontWeight:900,fontSize:38,color:on?GOLD:GRAY}}>{w.zh}</div>
  </div>;})}
  <div style={{position:"absolute",top:1350,left:190,width:700}}><FollowBar t={t} m={m} k={`r${i}`} fg={RED} track="rgba(200,16,46,.12)" muted={GRAY} label={`${i+1} / 5`}/></div>
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);const md=ease(t,s.start+1,s.start+1.4);return <AbsoluteFill style={{background:`radial-gradient(ellipse at 50% 40%, ${RED} 0%, ${RED2} 75%)`}}>
  <Brand color={GOLD}/>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:84,color:WHITE}}>常用词汇分类手册</div>
  <div style={{position:"absolute",top:500+(1-up)*60,left:300,opacity:up,width:480,height:548,borderRadius:12,overflow:"hidden",boxShadow:"0 30px 70px rgba(0,0,0,.4)"}}><Img src={staticFile("img/handbook.png")} style={{width:"100%",height:"100%",objectFit:"cover"}}/></div>
  <div style={{position:"absolute",top:1100,left:0,right:0,display:"flex",justifyContent:"center",gap:30,opacity:md,transform:`scale(${0.9+0.1*md})`}}><Medal big="8000+" small="词汇" size={180}/><Medal big="8 大" small="主题" size={180}/><Medal big="32 个" small="情景" size={180}/></div>
  <div style={{position:"absolute",top:1330,left:0,right:0,display:"flex",justifyContent:"center",opacity:ease(t,s.start+2,s.start+2.4)}}><div style={{background:WHITE,color:RED,fontFamily:ZH,fontWeight:900,fontSize:44,borderRadius:18,padding:"10px 30px"}}>配基础越南语 4 册</div></div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <SeriesCtx.Provider value={VI_SERIES}><AbsoluteFill style={{background:WHITE}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("theme")} t={t}><Theme p={p} t={t}/></Layer>
    <Layer s={S("map")} t={t}><MindMap p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, ${RED} 0%, ${RED2} 75%)`} accent={GOLD}/></Layer>
  </AbsoluteFill></SeriesCtx.Provider>;};
export const calculateMetadata=calcMeta as any;
