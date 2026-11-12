// 越 14 自我介绍：一段聊天记录。初次见面就是一来一回 —— 左边对方、右边自己，
// 每念一句，冒出一个气泡；讲完，整段对话就是一次完整的自我介绍。
import React from "react";
import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, End, ZH, VI, VI_SERIES, SeriesCtx, ease, sceneOf, calcMeta} from "./Common";

type It={vi:string;zh:string;side:"l"|"r"};
export type SceneProps=BaseProps&{data:{items:It[]}};
const BG="#ece5dd",ME="#d9fdd3",THEM="#ffffff",INK="#111b21",GREEN="#008069",MUTE="rgba(17,27,33,.45)";

const Bubble:React.FC<{x:It;on:boolean;a:number}>=({x,on,a})=><div style={{display:"flex",justifyContent:x.side==="r"?"flex-end":"flex-start",opacity:a,transform:`translateY(${(1-a)*24}px)`}}>
  <div style={{maxWidth:880,padding:"24px 34px",borderRadius:x.side==="r"?"28px 6px 28px 28px":"6px 28px 28px 28px",background:x.side==="r"?ME:THEM,boxShadow:on?`0 0 0 5px ${GREEN}`:"0 3px 8px rgba(0,0,0,.08)"}}>
    <div style={{fontFamily:VI,fontSize:x.vi.length>18?60:72,color:INK,lineHeight:1.25}}>{x.vi}</div>
    <div style={{fontFamily:ZH,fontWeight:700,fontSize:40,color:GREEN,marginTop:6}}>{x.zh}</div></div></div>;

const Bar:React.FC=()=><div style={{position:"absolute",top:0,left:0,right:0,height:230,background:GREEN}}/>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:BG}}>
  <Bar/><Brand color={INK}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:INK,border:`2px solid ${GREEN}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 会话</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:INK}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:900,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:GREEN}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:1200,left:80,right:80}}><Bubble x={p.data.items[0]} on={false} a={1}/></div>
</AbsoluteFill>;

const Chat:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[4,3,2,1,0].find(k=>t>=m[`me${k}`]);
  return <AbsoluteFill style={{background:BG}}>
  <Bar/><Brand color={INK}/>
  <div style={{position:"absolute",top:340,left:70,right:70,display:"flex",flexDirection:"column",gap:22}}>
    {p.data.items.map((x,k)=>i!==undefined&&k<=i?<Bubble key={k} x={x} on={k===i} a={ease(t,m[`me${k}`],m[`me${k}`]+0.3)}/>:null)}
  </div>
  {i!==undefined&&<div style={{position:"absolute",top:1520,left:150,width:520}}><FollowBar t={t} m={m} k={`me${i}`} fg={GREEN} track="rgba(0,0,0,.08)" muted={MUTE} label={`${i+1} / 5`}/></div>}
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:BG}}>
  <Bar/><Brand color={INK}/>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:80,color:INK}}>每一课都有<span style={{color:GREEN}}>会话</span></div>
  <div style={{position:"absolute",top:520+(1-up)*60,left:0,right:0,display:"flex",justifyContent:"center",opacity:up}}>
    <div style={{width:720,height:653,borderRadius:28,overflow:"hidden",boxShadow:"0 24px 60px rgba(0,0,0,.25)"}}><Img src={staticFile("img/books.png")} style={{width:"100%",height:"100%",objectFit:"cover"}}/></div></div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <SeriesCtx.Provider value={VI_SERIES}><AbsoluteFill style={{background:BG}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("chat")} t={t}><Chat p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, #1a8a72 0%, #005c4b 75%)`} accent={ME}/></Layer>
  </AbsoluteFill></SeriesCtx.Provider>;};
export const calculateMetadata=calcMeta as any;
