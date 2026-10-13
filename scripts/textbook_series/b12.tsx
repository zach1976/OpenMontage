// 12 高低辅音：一架跷跷板。同一个音，高辅音坐在高的一头、低辅音坐在低的一头 ——
// 先念高的，再念低的，板子就往被念的那头压下去。"成对"是坐在同一块板上看出来的。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, BookPeek, End, ZH, TH, cl, ease, sceneOf, calcMeta} from "./Common";

type P={hi:string;lo:string;snd:string};
export type SceneProps=BaseProps&{data:{pairs:P[]}};
const MOSS="#2d4a3e",LEAF="#9ccc65",CREAM="#f4f1de",CORAL="#e07a5f",DIM="rgba(244,241,222,.5)";

const Tile:React.FC<{ch:string;c:string;size:number;label:string}>=({ch,c,size,label})=><div style={{width:size,height:size,borderRadius:size*.18,background:c,display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",boxShadow:"0 14px 30px rgba(0,0,0,.25)"}}>
  <div style={{fontFamily:TH,fontSize:size*.58,lineHeight:1.25,color:"#fff"}}>{ch}</div>
  <div style={{fontFamily:ZH,fontWeight:900,fontSize:size*.13,color:"#fff",opacity:.9}}>{label}</div>
</div>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:MOSS}}>
  <Brand color={LEAF}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:CREAM,border:`2px solid ${LEAF}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 低辅音</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:CREAM,letterSpacing:6}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:LEAF,letterSpacing:6}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:1300,left:0,right:0,display:"flex",justifyContent:"center",gap:24}}>{p.data.pairs.map(x=><div key={x.hi} style={{display:"flex",flexDirection:"column",gap:6}}><Tile ch={x.hi} c={CORAL} size={92} label=""/><Tile ch={x.lo} c="#3d7a5c" size={92} label=""/></div>)}</div>
</AbsoluteFill>;

const Pairs:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const s=sceneOf(p,"pairs");const i=[4,3,2,1,0].find(k=>t>=m[`hi${k}`]);const x=i!==undefined?p.data.pairs[i]:undefined;
  const loOn=i!==undefined&&t>=m[`lo${i}_a`];const tilt=i===undefined?0:interpolate(t,[m[`hi${i}`],m[`hi${i}`]+0.3],[0,-12],cl)+(loOn?interpolate(t,[m[`lo${i}_a`],m[`lo${i}_a`]+0.3],[0,24],cl):0);
  return <AbsoluteFill style={{background:MOSS}}>
  <Brand color={LEAF}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:60,color:CREAM}}>{x?<>同一个音 <span style={{color:LEAF,fontFamily:"Helvetica, sans-serif"}}>{x.snd}</span></>:"高的一头 · 低的一头"}</div>
  {x&&<div style={{position:"absolute",top:780,left:90,width:900,height:40,transform:`rotate(${tilt}deg)`,transformOrigin:"50% 50%"}}>
    <div style={{position:"absolute",left:0,right:0,top:12,height:20,borderRadius:10,background:"#c9a26b"}}/>
    <div style={{position:"absolute",left:30,top:-270}}><Tile ch={x.hi} c={CORAL} size={260} label="高辅音"/></div>
    <div style={{position:"absolute",right:30,top:-270}}><Tile ch={x.lo} c="#3d7a5c" size={260} label="低辅音"/></div>
  </div>}
  <div style={{position:"absolute",top:820,left:490,width:0,height:0,borderLeft:"50px solid transparent",borderRight:"50px solid transparent",borderBottom:"90px solid #c9a26b"}}/>
  {x&&<div style={{position:"absolute",top:960,left:0,right:0,display:"flex",justifyContent:"center",gap:80,fontFamily:ZH,fontWeight:900,fontSize:50}}>
    <span style={{color:loOn?DIM:CORAL}}>{x.hi} 第五声 ↗</span><span style={{color:loOn?LEAF:DIM}}>{x.lo} 第一声 →</span></div>}
  {i!==undefined&&loOn&&<div style={{position:"absolute",top:1070,left:190,width:700}}><FollowBar t={t} m={m} k={`lo${i}`} fg={LEAF} track="rgba(244,241,222,.15)" muted={DIM} label={`${i+1} / 5`}/></div>}
  <div style={{position:"absolute",top:1220,left:110,right:110,display:"flex",justifyContent:"space-between",opacity:ease(t,s.start,s.start+0.4)}}>{p.data.pairs.map((q,k)=><div key={k} style={{fontFamily:TH,fontSize:56,lineHeight:1.4,color:i!==undefined&&k<=i?CREAM:DIM}}>{q.hi}·{q.lo}</div>)}</div>
</AbsoluteFill>;};

const Rule:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const a=ease(t,p.marks.rule,p.marks.rule+0.4);return <AbsoluteFill style={{background:CREAM}}>
  <Brand color={MOSS}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:84,color:MOSS}}>书上原话</div>
  <div style={{position:"absolute",top:490,left:0,right:0,display:"flex",justifyContent:"center",opacity:a}}><BookPeek name="row" w={900}/></div>
  <div style={{position:"absolute",top:680,left:0,right:0,display:"flex",justifyContent:"center",opacity:ease(t,p.marks.rule+0.8,p.marks.rule+1.2)}}><BookPeek name="pairs" w={920}/></div>
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:MOSS}}>
  <Brand color={LEAF}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:CREAM}}>第 <span style={{color:LEAF}}>1</span> 册 · 第 <span style={{color:LEAF}}>5</span> 课</div>
  <div style={{position:"absolute",top:500+(1-up)*60,left:0,right:0,display:"flex",justifyContent:"center",opacity:up}}><BookPeek name="lesson" w={780} rot={1.5} shadow="0 30px 80px rgba(0,0,0,.45)"/></div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:MOSS}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("pairs")} t={t}><Pairs p={p} t={t}/></Layer>
    <Layer s={S("rule")} t={t}><Rule p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, #3d6b57 0%, ${MOSS} 75%)`} accent={LEAF}/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
