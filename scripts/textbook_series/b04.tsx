// 书本素材版 04：版式沿用原 04（梅紫 + 蜜桃、四级台阶），每一级换成那一册自己的书页和原声 ——
// 第 4 级的原声是书自己报名字："基础泰语 第 4 册 第 1 课"。
import React from "react";
import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, Books, End, ZH, TH, cl, ease, sceneOf, calcMeta} from "./Common";

type Step={book:number;skill:string;th:string;zh:string;crop:string};
export type SceneProps=BaseProps&{data:{steps:Step[]}};

const PLUM="#2e1740",PLUM2="#4a2563",PEACH="#ff9e6d",CREAM="#fff1e4",DIM="rgba(255,241,228,.45)";
const BG=`linear-gradient(180deg, ${PLUM} 0%, ${PLUM2} 70%, #6b3466 100%)`;
const thSize=(s:string)=>s.length>24?54:s.length>12?72:s.length>4?92:120;

// 台阶几何：左下 → 右上
const SX=110,SW=215,BASE=1400,RISE=88;
const stepTop=(i:number)=>BASE-RISE*(i+1);

const Stairs:React.FC<{lit:number;pos:number;t:number;labels?:Step[]}>=({lit,pos,labels})=><>
  {[0,1,2,3].map(i=>{const on=i<=lit;return <div key={i} style={{position:"absolute",left:SX+i*SW,top:stepTop(i),width:SW-10,height:BASE-stepTop(i)+40,borderRadius:"18px 18px 0 0",background:on?PEACH:"rgba(255,241,228,.1)",boxShadow:i===lit?"0 0 60px rgba(255,158,109,.55)":"none"}}>
    <div style={{textAlign:"center",marginTop:14,fontFamily:ZH,fontWeight:900,fontSize:46,color:on?PLUM:DIM}}>{i+1}</div>
    {labels&&<div style={{textAlign:"center",fontFamily:ZH,fontWeight:800,fontSize:36,color:on?PLUM:DIM}}>{labels[i].skill}</div>}
  </div>;})}
  {pos>=0&&(()=>{const x=SX+pos*SW+(SW-10)/2-28,y=stepTop(pos)-70;return <div style={{position:"absolute",left:x,top:y,width:56,height:56,borderRadius:30,background:CREAM,boxShadow:"0 0 30px rgba(255,241,228,.8)"}}/>;})()}
</>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:BG,overflow:"hidden"}}>
  <div style={{position:"absolute",left:740,top:170,width:260,height:260,borderRadius:200,background:"radial-gradient(circle, rgba(255,158,109,.5), transparent 70%)"}}/>
  <Brand color={PEACH}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:CREAM,border:"2px solid rgba(255,158,109,.7)",borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 全套</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:CREAM,letterSpacing:4}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:CREAM,letterSpacing:4}}>一路读到<span style={{color:PEACH}}>课文</span></div>
  <div style={{position:"absolute",top:1300,left:0,right:0,display:"flex",justifyContent:"center",alignItems:"flex-end",gap:12}}>{[0,1,2,3].map(i=><div key={i} style={{width:120,height:50+i*40,borderRadius:"12px 12px 0 0",background:PEACH,opacity:.55+i*.15,fontFamily:ZH,fontWeight:900,fontSize:34,color:PLUM,textAlign:"center",paddingTop:6}}>{i+1}</div>)}</div>
</AbsoluteFill>;

const Climb:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const s=sceneOf(p,"stairs");const i=[3,2,1,0].find(k=>t>=m[`k${k}`])??-1;const st=i>=0?p.data.steps[i]:undefined;
  const hop=i>=0?ease(t,m[`k${i}`],m[`k${i}`]+0.45):0;const pos=i<0?-1:i;const sample=i>=0?ease(t,m[`k${i}_a`]-0.15,m[`k${i}_a`]+0.2):0;
  return <AbsoluteFill style={{background:BG}}>
  <Brand color={PEACH}/>
  {st&&<>
    <div style={{position:"absolute",top:330,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:96,color:CREAM,opacity:hop}}>第 <span style={{color:PEACH}}>{st.book}</span> 册 · {st.skill}</div>
    <div style={{position:"absolute",top:470,left:80,right:80,height:330,display:"flex",alignItems:"center",justifyContent:"center",opacity:hop}}>
      <div style={{background:"#fff",padding:10,borderRadius:8,boxShadow:"0 20px 50px rgba(0,0,0,.4)",maxWidth:900,maxHeight:330,display:"flex"}}><Img src={staticFile(`book/${st.crop}.png`)} style={{maxWidth:880,maxHeight:310,objectFit:"contain",display:"block"}}/></div>
    </div>
    <div style={{position:"absolute",top:830,left:60,right:60,textAlign:"center",opacity:sample}}>
      <div style={{fontFamily:TH,fontSize:thSize(st.th),lineHeight:1.4,color:CREAM}}>{st.th}</div>
      <div style={{fontFamily:ZH,fontSize:44,fontWeight:800,color:PEACH}}>{st.zh}</div>
    </div>
  </>}
  <div style={{position:"absolute",inset:0,opacity:ease(t,s.start,s.start+0.4)}}><Stairs lit={i} pos={pos} t={t} labels={p.data.steps}/></div>
  {i>=0&&<div style={{position:"absolute",top:1470,left:190,width:700}}><FollowBar t={t} m={m} k={`k${i}`} fg={PEACH} track="rgba(255,241,228,.15)" muted={DIM} label={`${i+1} / 4`}/></div>}
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);
  return <AbsoluteFill style={{background:BG}}>
  <Brand color={PEACH}/>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:96,color:CREAM}}>1 → 4 册 · 一套走完</div>
  <div style={{position:"absolute",top:520+(1-up)*60,left:110,opacity:up}}><Books w={860} shadow="0 30px 80px rgba(0,0,0,.45)"/></div>
  <div style={{position:"absolute",top:1340,left:0,right:0,display:"flex",justifyContent:"center",gap:24,opacity:ease(t,s.start+0.9,s.start+1.3)}}>
    {["适用培训班学员","全套附音频"].map(x=><div key={x} style={{fontFamily:ZH,fontWeight:900,fontSize:44,color:PLUM,background:PEACH,borderRadius:40,padding:"10px 30px"}}>{x}</div>)}
  </div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:PLUM}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("stairs")} t={t}><Climb p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={BG} accent={PEACH}/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
