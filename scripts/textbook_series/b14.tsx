// 14 家庭：一棵家谱树 + 一张 2×2 小矩阵。哥哥姐姐弟弟妹妹不是四个词，
// 是 พี่/น้อง（年长/年幼）× ชาย/สาว（男/女）拼出来的 —— 矩阵当场把这件事摆出来。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, BookPeek, End, ZH, TH, ease, sceneOf, calcMeta} from "./Common";

type M={th:string;zh:string;a:string;b:string};
export type SceneProps=BaseProps&{data:{members:M[]}};
const PEACH="#fff1e6",TERRA="#c8553d",TEAL="#2a7f84",INK="#3b2418",GRAY="#9c8577";

const Node:React.FC<{m:M;on:boolean;seen:boolean;w:number}>=({m,on,seen,w})=><div style={{width:w,height:190,borderRadius:28,background:on?TERRA:"#fff",border:`4px solid ${seen?TERRA:"rgba(200,85,61,.2)"}`,boxShadow:on?"0 18px 40px rgba(200,85,61,.35)":"0 6px 16px rgba(59,36,24,.06)",display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",opacity:seen?1:.45,transform:`scale(${on?1.06:1})`}}>
  <div style={{fontFamily:TH,fontSize:58,lineHeight:1.4,color:on?"#fff":INK}}>{m.a?<><span style={{color:on?"#ffd9c9":TERRA}}>{m.a}</span><span style={{color:on?"#c9f2f0":TEAL}}>{m.b}</span></>:m.th}</div>
  <div style={{fontFamily:ZH,fontWeight:900,fontSize:38,color:on?"#fff":GRAY}}>{m.zh}</div>
</div>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:PEACH}}>
  <Brand color={TERRA}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:INK,border:`2px solid ${TERRA}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 家庭</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:INK,letterSpacing:6}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:TERRA,letterSpacing:4}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:1320,left:0,right:0,display:"flex",justifyContent:"center",gap:30,fontFamily:TH,fontSize:80,lineHeight:1.4}}><span style={{color:TERRA}}>พี่ · น้อง</span><span style={{color:INK}}>×</span><span style={{color:TEAL}}>ชาย · สาว</span></div>
</AbsoluteFill>;

const Tree:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[5,4,3,2,1,0].find(k=>t>=m[`f${k}`])??0;const M=p.data.members;const cur=M[i];
  const seen=(k:number)=>t>=m[`f${k}`];const kids=[2,3,4,5];
  return <AbsoluteFill style={{background:PEACH}}>
  <Brand color={TERRA}/>
  <div style={{position:"absolute",top:340,left:120,display:"flex",gap:120}}>{[0,1].map(k=><Node key={k} m={M[k]} on={k===i} seen={seen(k)} w={300}/>)}</div>
  <svg style={{position:"absolute",left:0,top:0}} width={1080} height={1920}><path d="M540 535 V 600 M150 600 H 930 M150 600 V 640 M410 600 V 640 M670 600 V 640 M930 600 V 640" stroke={TERRA} strokeWidth={5} fill="none" opacity={.5}/></svg>
  <div style={{position:"absolute",top:640,left:40,right:40,display:"flex",justifyContent:"space-between"}}>{kids.map(k=><Node key={k} m={M[k]} on={k===i} seen={seen(k)} w={230}/>)}</div>
  {cur.a&&<div style={{position:"absolute",top:900,left:150,width:780,opacity:ease(t,m[`f${i}`],m[`f${i}`]+0.3)}}>
    <div style={{display:"grid",gridTemplateColumns:"140px 1fr 1fr",gap:12,fontFamily:ZH,fontWeight:900,fontSize:36,textAlign:"center"}}>
      <div/><div style={{color:TEAL}}>ชาย 男</div><div style={{color:TEAL}}>สาว 女</div>
      {[["พี่","年长"],["น้อง","年幼"]].map(([a,g])=><React.Fragment key={a}>
        <div style={{color:TERRA,alignSelf:"center"}}>{a}<br/><span style={{fontSize:28}}>{g}</span></div>
        {["ชาย","สาว"].map(b=>{const hit=cur.a===a&&cur.b===b;const z=M.find(x=>x.a===a&&x.b===b)!;return <div key={b} style={{height:110,borderRadius:18,background:hit?TERRA:"#fff",color:hit?"#fff":INK,display:"flex",alignItems:"center",justifyContent:"center",fontSize:48,boxShadow:"0 4px 12px rgba(59,36,24,.08)"}}>{z.zh}</div>;})}
      </React.Fragment>)}
    </div>
  </div>}
  {!cur.a&&<div style={{position:"absolute",top:960,left:0,right:0,textAlign:"center",fontFamily:TH,fontSize:200,lineHeight:1.3,color:INK,opacity:ease(t,m[`f${i}`],m[`f${i}`]+0.3)}}>{cur.th}</div>}
  <div style={{position:"absolute",top:1250,left:190,width:700}}><FollowBar t={t} m={m} k={`f${i}`} fg={TERRA} track="rgba(200,85,61,.14)" muted={GRAY} label={`${i+1} / 6`}/></div>
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:PEACH}}>
  <Brand color={TERRA}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:INK}}>第 <span style={{color:TERRA}}>2</span> 册 · 第 <span style={{color:TERRA}}>2</span> 课</div>
  <div style={{position:"absolute",top:500+(1-up)*60,left:0,right:0,display:"flex",justifyContent:"center",opacity:up}}><BookPeek name="vocab" w={920} rot={-1.5}/></div>
  <div style={{position:"absolute",top:1000,left:0,right:0,display:"flex",justifyContent:"center",gap:20,opacity:ease(t,s.start+0.9,s.start+1.3)}}>{["分类词汇一整页","附原声"].map(x=><div key={x} style={{fontFamily:ZH,fontWeight:900,fontSize:44,color:"#fff",background:TERRA,borderRadius:18,padding:"10px 28px"}}>{x}</div>)}</div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:PEACH}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("tree")} t={t}><Tree p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, ${TERRA} 0%, #7a2e1f 75%)`} accent="#ffd9c9"/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
