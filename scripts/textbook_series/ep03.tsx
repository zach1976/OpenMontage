// 03 第一天 5 句：落地第一天的打卡清单 —— 当前这句放成一组对话气泡，底下的清单逐条打勾。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, Books, End, ZH, TH, ease, sceneOf, calcMeta} from "./Common";

type Line={th:string;zh:string;tag:string};
export type SceneProps=BaseProps&{data:{lines:Line[]}};

const MINT="#eef6f0",GREEN="#0e5e47",MANGO="#ffbe2e",INK="#17322a",GRAY="#7d8c85";
const thSize=(s:string)=>s.length>18?78:s.length>14?90:s.length>10?104:122;

const Tick:React.FC<{on:boolean;size:number;dark?:boolean}>=({on,size,dark})=><div style={{width:size,height:size,borderRadius:size*.22,border:`${size*.08}px solid ${dark?"#fff":GREEN}`,background:on?MANGO:"transparent",display:"flex",alignItems:"center",justifyContent:"center"}}>
  {on&&<svg width={size*.7} height={size*.7} viewBox="0 0 24 24"><path d="M4 12.5 L10 18 L20 6" stroke={GREEN} strokeWidth={3.6} fill="none" strokeLinecap="round" strokeLinejoin="round"/></svg>}
</div>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:`linear-gradient(180deg, #0b4d3a 0%, ${GREEN} 55%, #0b4d3a 100%)`,overflow:"hidden"}}>
  <svg style={{position:"absolute",right:-120,top:120,opacity:.09}} width="700" height="700" viewBox="0 0 100 100"><path d="M50 95 C 52 70 50 45 48 30 M48 30 C 30 20 15 25 5 35 M48 30 C 40 12 25 5 12 8 M48 30 C 60 10 78 6 92 12 M48 30 C 68 22 85 28 96 40 M48 30 C 52 18 50 8 46 2" stroke="#fff" strokeWidth={3} fill="none" strokeLinecap="round"/></svg>
  <Brand color={MANGO}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:"#fff",border:"2px solid rgba(255,190,46,.7)",borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 会话</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:"#fff",letterSpacing:4}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:"#fff",letterSpacing:4}}>这<span style={{color:MANGO}}>5</span>句够用</div>
  <div style={{position:"absolute",top:1320,left:0,right:0,display:"flex",justifyContent:"center",gap:26}}>{p.data.lines.map((l,i)=><div key={i} style={{display:"flex",flexDirection:"column",alignItems:"center",gap:10}}><Tick on={false} size={70} dark/><div style={{fontFamily:ZH,fontSize:30,color:"rgba(255,255,255,.8)"}}>{l.tag}</div></div>)}</div>
</AbsoluteFill>;

const Chat:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[4,3,2,1,0].find(k=>t>=m[`s${k}`])??0;const l=p.data.lines[i];
  const a=ease(t,m[`s${i}`],m[`s${i}`]+0.35),b=ease(t,m[`s${i}_a`]-0.1,m[`s${i}_a`]+0.25);
  return <AbsoluteFill style={{background:MINT}}>
  <Brand color={GREEN}/>
  <div style={{position:"absolute",top:340,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{background:GREEN,color:"#fff",fontFamily:ZH,fontWeight:900,fontSize:50,borderRadius:50,padding:"10px 40px"}}>{i+1} · {l.tag}</div></div>
  <div style={{position:"absolute",top:500,left:80,maxWidth:760,opacity:a,transform:`translateY(${(1-a)*30}px)`}}>
    <div style={{background:"#fff",borderRadius:"40px 40px 40px 10px",padding:"30px 44px",fontFamily:ZH,fontWeight:900,fontSize:84,color:INK,boxShadow:"0 14px 40px rgba(14,94,71,.1)"}}>{l.zh}</div>
  </div>
  <div style={{position:"absolute",top:740,right:70,left:120,display:"flex",justifyContent:"flex-end",opacity:b,transform:`translateY(${(1-b)*30}px)`}}>
    <div style={{background:GREEN,borderRadius:"40px 40px 10px 40px",padding:"26px 44px",fontFamily:TH,fontSize:thSize(l.th),lineHeight:1.5,color:"#fff",boxShadow:"0 18px 44px rgba(14,94,71,.25)"}}>{l.th}</div>
  </div>
  {l.th.endsWith("ครับ")&&<div style={{position:"absolute",top:1010,right:80,fontFamily:ZH,fontSize:36,color:GRAY,opacity:b}}>女生把 <span style={{fontFamily:TH}}>ครับ</span> 换成 <span style={{fontFamily:TH,color:GREEN}}>ค่ะ</span></div>}
  <div style={{position:"absolute",top:1110,left:190,width:700}}><FollowBar t={t} m={m} k={`s${i}`} fg={GREEN} track="rgba(14,94,71,.14)" muted={GRAY}/></div>
  <div style={{position:"absolute",top:1290,left:80,right:80,display:"flex",justifyContent:"space-between"}}>{p.data.lines.map((x,k)=>{const done=t>=m[`s${k}_e`]-0.05;const cur=k===i;return <div key={k} style={{display:"flex",flexDirection:"column",alignItems:"center",gap:10,opacity:cur||done?1:.4}}>
    <Tick on={done} size={cur?96:80}/><div style={{fontFamily:ZH,fontSize:32,fontWeight:cur?900:600,color:cur?GREEN:INK}}>{x.tag}</div></div>;})}</div>
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);const tag=ease(t,s.start+0.9,s.start+1.2);
  return <AbsoluteFill style={{background:MINT}}>
  <Brand color={GREEN}/>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:INK}}>日常会话在第 <span style={{color:GREEN}}>2</span> 册</div>
  <div style={{position:"absolute",top:510,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:700,fontSize:52,color:GRAY}}>中泰对照着练</div>
  <div style={{position:"absolute",top:660+(1-up)*60,left:110,opacity:up}}><Books w={860} shadow="0 26px 60px rgba(14,94,71,.22)"/></div>
  <div style={{position:"absolute",top:640,left:60,transform:`rotate(-8deg) scale(${tag})`,background:MANGO,color:GREEN,fontFamily:ZH,fontWeight:900,fontSize:46,padding:"12px 28px",borderRadius:"30px 30px 30px 8px"}}>附音频</div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:MINT}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("chat")} t={t}><Chat p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`linear-gradient(180deg, #0b4d3a 0%, ${GREEN} 60%, #0b4d3a 100%)`} accent={MANGO}/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
