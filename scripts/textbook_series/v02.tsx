// 越 02 汉越词：宣纸上盖章。每个越南语音节头上压一枚朱印，印里是它对应的汉字 ——
// điện 電 / thoại 話。音节和汉字一一对上，"藏着的中文"是盖出来给人看的。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, Books, End, ZH, VI, VI_SERIES, SeriesCtx, cl, ease, sceneOf, calcMeta} from "./Common";

type Word={vi:string;han:string[];syl:string[];zh:string};
export type SceneProps=BaseProps&{data:{words:Word[]}};

const RICE="#f5ecd7",CINNABAR="#b8322a",INK="#231d17",GRAY="#8b7f6c";
const SERIF="Songti SC, STSong, Noto Serif SC, serif";

const Seal:React.FC<{ch:string;size:number;press:number}>=({ch,size,press})=><div style={{width:size,height:size,borderRadius:size*.08,background:CINNABAR,color:RICE,display:"flex",alignItems:"center",justifyContent:"center",fontFamily:SERIF,fontWeight:900,fontSize:size*.68,opacity:press,transform:`scale(${1.35-0.35*press}) rotate(${(1-press)*-8}deg)`,boxShadow:`inset 0 0 0 ${size*.05}px ${RICE}, inset 0 0 0 ${size*.07}px ${CINNABAR}`}}>{ch}</div>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:RICE}}>
  <Brand color={CINNABAR}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:INK,border:`2px solid ${CINNABAR}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 汉越词</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:INK,letterSpacing:6}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:CINNABAR,letterSpacing:6}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:1320,left:0,right:0,display:"flex",justifyContent:"center",gap:60}}>{p.data.words.slice(0,2).map(w=><div key={w.vi} style={{display:"flex",flexDirection:"column",alignItems:"center",gap:10}}><div style={{display:"flex",gap:8}}>{w.han.map(h=><Seal key={h} ch={h} size={80} press={1}/>)}</div><div style={{fontFamily:VI,fontSize:44,color:INK}}>{w.vi}</div></div>)}</div>
</AbsoluteFill>;

const Seals:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[3,2,1,0].find(k=>t>=m[`h${k}`])??0;const w=p.data.words[i];
  const a=ease(t,m[`h${i}`],m[`h${i}`]+0.3);
  return <AbsoluteFill style={{background:RICE}}>
  <Brand color={CINNABAR}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:60,color:GRAY}}>听越南语，猜中文</div>
  <div style={{position:"absolute",top:500,left:0,right:0,display:"flex",justifyContent:"center",gap:60}}>
    {w.syl.map((s,k)=>{const press=interpolate(t,[m[`h${i}_a`]+k*0.25,m[`h${i}_a`]+k*0.25+0.18],[0,1],cl);return <div key={k} style={{display:"flex",flexDirection:"column",alignItems:"center",gap:30,opacity:a}}>
      <Seal ch={w.han[k]} size={250} press={press}/>
      <div style={{fontFamily:VI,fontSize:110,lineHeight:1.3,color:INK}}>{s}</div>
    </div>;})}
  </div>
  <div style={{position:"absolute",top:1030,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:84,color:CINNABAR,opacity:ease(t,m[`h${i}_b`],m[`h${i}_b`]+0.3)}}>= {w.zh}</div>
  <div style={{position:"absolute",top:1190,left:190,width:700}}><FollowBar t={t} m={m} k={`h${i}`} fg={CINNABAR} track="rgba(184,50,42,.14)" muted={GRAY} label={`${i+1} / 4`}/></div>
  <div style={{position:"absolute",top:1330,left:0,right:0,display:"flex",justifyContent:"center",gap:26}}>{p.data.words.map((x,k)=><div key={k} style={{display:"flex",gap:4,opacity:k<=i?1:.25}}>{x.han.map(h=><Seal key={h} ch={h} size={66} press={1}/>)}</div>)}</div>
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:RICE}}>
  <Brand color={CINNABAR}/>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:INK}}>四册约 <span style={{color:CINNABAR}}>4000</span> 词</div>
  <div style={{position:"absolute",top:520+(1-up)*60,left:110,opacity:up}}><Books w={860} radius={8} shadow="0 26px 60px rgba(35,29,23,.22)"/></div>
  <div style={{position:"absolute",top:1320,right:100,opacity:ease(t,s.start+0.9,s.start+1.2)}}><Seal ch="教" size={130} press={ease(t,s.start+0.9,s.start+1.2)}/></div>
  <div style={{position:"absolute",top:1350,left:110,fontFamily:ZH,fontWeight:900,fontSize:44,color:INK,opacity:ease(t,s.start+0.9,s.start+1.3)}}>解放军外国语学院<br/>越南语专业编写</div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <SeriesCtx.Provider value={VI_SERIES}><AbsoluteFill style={{background:RICE}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("seals")} t={t}><Seals p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, #c94a3f 0%, #7d1d17 75%)`} accent={RICE}/></Layer>
  </AbsoluteFill></SeriesCtx.Provider>;};
export const calculateMetadata=calcMeta as any;
