// 11 高辅音：十只热气球。书上说高辅音单念发第五声（往上扬），所以每念一个，
// 那只气球就升上去 —— 念完十个，天上一排气球。第二遍跟读把当前那只拉近放大。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, BookPeek, End, ZH, TH, ease, sceneOf, calcMeta} from "./Common";

export type SceneProps=BaseProps&{data:{letters:string[]}};
const DUSK1="#ffb37a",DUSK2="#ff6f61",PLUM="#5b2a86",CREAM="#fff6ec",INK="#3a1c4a";
const COLORS=["#ff6f61","#ffd166","#06d6a0","#118ab2","#ef476f","#f78c6b","#7b2cbf","#4cc9f0","#f15bb5","#00bb9f"];
const BG=`linear-gradient(180deg, ${PLUM} 0%, ${DUSK2} 55%, ${DUSK1} 100%)`;

const Balloon:React.FC<{ch:string;c:string;size:number}>=({ch,c,size})=><div style={{width:size,height:size*1.35,position:"relative"}}>
  <div style={{position:"absolute",left:0,top:0,width:size,height:size*1.1,borderRadius:"50% 50% 46% 46%",background:`radial-gradient(circle at 35% 30%, #ffffff55 0%, ${c} 40%)`,display:"flex",alignItems:"center",justifyContent:"center",fontFamily:TH,fontSize:size*0.55,lineHeight:1.3,color:"#fff",textShadow:"0 3px 8px rgba(0,0,0,.25)"}}>{ch}</div>
  <div style={{position:"absolute",left:size*0.38,top:size*1.12,width:size*0.24,height:size*0.2,borderRadius:6,background:"#8a5a2b"}}/>
</div>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:BG}}>
  <Brand color={CREAM}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:CREAM,border:`2px solid ${CREAM}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 高辅音</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:160,color:CREAM,letterSpacing:4,textShadow:"0 6px 24px rgba(0,0,0,.25)"}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:160,color:"#ffd166",letterSpacing:4,textShadow:"0 6px 24px rgba(0,0,0,.25)"}}>一共<span>10</span>个</div>
  <div style={{position:"absolute",top:1300,left:40,right:40,display:"flex",justifyContent:"space-between"}}>{p.data.letters.map((ch,k)=><Balloon key={k} ch={ch} c={COLORS[k]} size={88}/>)}</div>
</AbsoluteFill>;

const Rise:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const pass2=t>=m.again;
  const i1=[...Array(10).keys()].reverse().find(k=>t>=m[`p${k}`]);const i2=[...Array(10).keys()].reverse().find(k=>t>=m[`h${k}_a`]);
  return <AbsoluteFill style={{background:BG}}>
  <Brand color={CREAM}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:60,color:"#ffd166"}}>{pass2?"跟着读":"听书里的原声"}</div>
  {p.data.letters.map((ch,k)=>{const up=i1!==undefined&&k<=i1?ease(t,m[`p${k}`],m[`p${k}`]+0.6):0;const x=60+(k%5)*196,y0=1300,y1=500+Math.floor(k/5)*260;const y=y0+(y1-y0)*up;
    return <div key={k} style={{position:"absolute",left:x,top:y+Math.sin(t*2+k)*6,opacity:pass2?(k===i2?0:.35):1}}><Balloon ch={ch} c={COLORS[k]} size={150}/></div>;})}
  {pass2&&i2!==undefined&&<>
    <div style={{position:"absolute",top:470,left:0,right:0,display:"flex",justifyContent:"center",transform:`scale(${0.9+0.1*ease(t,m[`h${i2}_a`],m[`h${i2}_a`]+0.25)})`}}><Balloon ch={p.data.letters[i2]} c={COLORS[i2]} size={420}/></div>
    <div style={{position:"absolute",top:1120,left:190,width:700}}><FollowBar t={t} m={m} k={`h${i2}`} fg="#ffd166" track="rgba(255,246,236,.2)" muted="rgba(255,246,236,.75)" label={`${i2+1} / 10`}/></div>
  </>}
</AbsoluteFill>;};

const Rule:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const a=ease(t,p.marks.rule,p.marks.rule+0.4);return <AbsoluteFill style={{background:CREAM}}>
  <Brand color={PLUM}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:84,color:INK}}>书上原话</div>
  <div style={{position:"absolute",top:500,left:0,right:0,display:"flex",justifyContent:"center",opacity:a}}><BookPeek name="row" w={900}/></div>
  <div style={{position:"absolute",top:700,left:0,right:0,display:"flex",justifyContent:"center",opacity:ease(t,p.marks.rule+0.8,p.marks.rule+1.2)}}><BookPeek name="rule" w={940}/></div>
  <div style={{position:"absolute",top:960,left:0,right:0,display:"flex",justifyContent:"center",gap:40,fontFamily:ZH,fontWeight:900,fontSize:56,opacity:ease(t,p.marks.rule+1.6,p.marks.rule+2)}}>
    <div style={{background:"#118ab2",color:"#fff",borderRadius:20,padding:"14px 30px"}}>中辅音 → 第一声</div>
    <div style={{background:DUSK2,color:"#fff",borderRadius:20,padding:"14px 30px"}}>高辅音 → 第五声</div>
  </div>
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:BG}}>
  <Brand color={CREAM}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:CREAM}}>第 <span style={{color:"#ffd166"}}>1</span> 册 · 第 <span style={{color:"#ffd166"}}>4</span> 课</div>
  <div style={{position:"absolute",top:500+(1-up)*60,left:0,right:0,display:"flex",justifyContent:"center",opacity:up}}><BookPeek name="lesson" w={780} rot={-2} shadow="0 30px 80px rgba(0,0,0,.4)"/></div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:PLUM}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("rise")} t={t}><Rise p={p} t={t}/></Layer>
    <Layer s={S("rule")} t={t}><Rule p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={BG} accent="#ffd166"/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
