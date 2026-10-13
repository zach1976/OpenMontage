// 越 03 第一天五句：一叠明信片。每句一张从右边飞进来盖在上一张上面，邮戳写着用在哪；
// 第一天走完，手里就是五张寄出去的明信片。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, Books, End, ZH, VI, VI_SERIES, SeriesCtx, ease, sceneOf, calcMeta} from "./Common";

type Line={vi:string;zh:string;tag:string};
export type SceneProps=BaseProps&{data:{lines:Line[]}};

const SKY="#2f7fbf",SKY2="#1f5f96",SUN="#ffd23f",CARD="#fffdf6",INK="#1d2b3a",GRAY="#7f8b96";
const viSize=(s:string)=>s.length>18?78:s.length>10?96:124;

const Postcard:React.FC<{l:Line;rot:number;x:number;o:number;stamp:number;active:boolean}>=({l,rot,x,o,stamp,active})=><div style={{position:"absolute",top:470,left:80+x,width:920,height:560,background:CARD,borderRadius:18,transform:`rotate(${rot}deg)`,opacity:o,boxShadow:"0 24px 50px rgba(15,40,70,.3)",overflow:"hidden"}}>
  <div style={{position:"absolute",left:0,right:0,top:0,height:16,background:`repeating-linear-gradient(90deg, #e04a3f 0 40px, ${CARD} 40px 60px, ${SKY} 60px 100px, ${CARD} 100px 120px)`}}/>
  <div style={{position:"absolute",right:40,top:50,width:150,height:170,border:`4px dashed ${SKY}`,borderRadius:10,display:"flex",alignItems:"center",justifyContent:"center",fontFamily:ZH,fontWeight:900,fontSize:40,color:SKY,transform:`rotate(${8-8*stamp}deg) scale(${1.4-0.4*stamp})`,opacity:stamp}}>{l.tag}</div>
  <div style={{position:"absolute",left:60,top:90,fontFamily:ZH,fontWeight:900,fontSize:92,color:active?INK:GRAY}}>{l.zh}</div>
  <div style={{position:"absolute",left:60,right:60,top:300,fontFamily:VI,fontSize:viSize(l.vi),lineHeight:1.35,color:active?SKY2:GRAY}}>{l.vi}</div>
  <div style={{position:"absolute",left:60,right:60,bottom:60,height:3,background:"rgba(29,43,58,.12)"}}/>
</div>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:`linear-gradient(180deg, ${SKY2} 0%, ${SKY} 100%)`}}>
  <Brand color={SUN}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:"#fff",border:`2px solid ${SUN}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 会话</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:"#fff",letterSpacing:4}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:"#fff",letterSpacing:4}}>先学这<span style={{color:SUN}}>5</span>句</div>
  <div style={{position:"absolute",top:1330,left:0,right:0,display:"flex",justifyContent:"center",gap:18}}>{p.data.lines.map((l,i)=><div key={i} style={{background:CARD,borderRadius:8,padding:"8px 16px",transform:`rotate(${(i-2)*4}deg)`,fontFamily:VI,fontSize:34,color:SKY2,boxShadow:"0 8px 18px rgba(0,0,0,.2)"}}>{l.vi.split(" ").slice(0,2).join(" ")}</div>)}</div>
</AbsoluteFill>;

const Street:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[4,3,2,1,0].find(k=>t>=m[`s${k}`])??0;
  return <AbsoluteFill style={{background:`linear-gradient(180deg, ${SKY2} 0%, ${SKY} 100%)`}}>
  <Brand color={SUN}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:60,color:SUN}}>第一天 · {i+1} / 5</div>
  {p.data.lines.map((l,k)=>{if(k>i)return null;const a=ease(t,m[`s${k}`],m[`s${k}`]+0.45);const st=ease(t,m[`s${k}_a`],m[`s${k}_a`]+0.25);const back=i-k;
    return <Postcard key={k} l={l} rot={back?(k%2?3:-3)-back:(1-a)*10} x={back?-back*10:(1-a)*700} o={back>2?0:1} stamp={st} active={back===0}/>;})}
  <div style={{position:"absolute",top:1140,left:190,width:700}}><FollowBar t={t} m={m} k={`s${i}`} fg={SUN} track="rgba(255,255,255,.18)" muted="rgba(255,255,255,.7)"/></div>
  <div style={{position:"absolute",top:1290,left:80,right:80,display:"flex",justifyContent:"space-between"}}>{p.data.lines.map((l,k)=><div key={k} style={{width:160,height:110,borderRadius:10,background:k<i||(k===i&&t>=m[`s${k}_e`]-0.05)?SUN:"rgba(255,255,255,.15)",display:"flex",alignItems:"center",justifyContent:"center",fontFamily:ZH,fontWeight:900,fontSize:34,color:k<=i?INK:"rgba(255,255,255,.6)"}}>{l.tag}</div>)}</div>
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:`linear-gradient(180deg, ${SKY2} 0%, ${SKY} 100%)`}}>
  <Brand color={SUN}/>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:"#fff"}}>每课都有会话</div>
  <div style={{position:"absolute",top:520+(1-up)*60,left:110,opacity:up,transform:"rotate(-2deg)"}}><Books w={860} radius={14} shadow="0 30px 70px rgba(10,30,60,.45)"/></div>
  <div style={{position:"absolute",top:1340,left:0,right:0,display:"flex",justifyContent:"center",gap:20,opacity:ease(t,s.start+0.9,s.start+1.3)}}>{["会话 + 生词","共 4 册"].map(x=><div key={x} style={{fontFamily:ZH,fontWeight:900,fontSize:44,color:INK,background:SUN,borderRadius:18,padding:"10px 28px"}}>{x}</div>)}</div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <SeriesCtx.Provider value={VI_SERIES}><AbsoluteFill style={{background:SKY}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("street")} t={t}><Street p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`linear-gradient(180deg, ${SKY2} 0%, #164a78 100%)`} accent={SUN}/></Layer>
  </AbsoluteFill></SeriesCtx.Provider>;};
export const calculateMetadata=calcMeta as any;
