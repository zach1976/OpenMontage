// 越 12 家人：一棵家谱树。祖辈在顶、父母在中、自己和弟妹在底，
// 念到谁，谁那个节点亮起来、连线点亮 —— 讲完一家人都在树上。
import React from "react";
import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, End, ZH, VI, VI_SERIES, SeriesCtx, ease, sceneOf, calcMeta} from "./Common";

type It={vi:string;zh:string;x:number;y:number};
export type SceneProps=BaseProps&{data:{items:It[];me:{x:number;y:number}}};
const BG="#1f3b2d",LEAF="#9bd27a",WARM="#ffd166",PALE="#f1f5ec",DIM="rgba(241,245,236,.35)";

const Node:React.FC<{x:number;y:number;on:boolean;cur:boolean;label:string;sub?:string}>=({x,y,on,cur,label,sub})=><div style={{position:"absolute",left:x-110,top:y-70,width:220,height:140,borderRadius:70,background:cur?WARM:on?"rgba(155,210,122,.9)":"rgba(255,255,255,.08)",border:`4px solid ${cur?WARM:on?LEAF:"rgba(255,255,255,.2)"}`,display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",boxShadow:cur?`0 0 50px ${WARM}`:"none"}}>
  <div style={{fontFamily:VI,fontSize:label.length>7?36:46,color:on||cur?BG:PALE}}>{label}</div>
  {sub&&<div style={{fontFamily:ZH,fontWeight:800,fontSize:28,color:on||cur?BG:DIM}}>{sub}</div>}
</div>;

const Tree:React.FC<{p:SceneProps;cur:number;shift?:number}>=({p,cur,shift=0})=>{const me=p.data.me;return <div style={{position:"absolute",inset:0,top:shift}}>
  <svg width={1080} height={1920} style={{position:"absolute",inset:0}}>
    {p.data.items.map((x,k)=><line key={k} x1={me.x} y1={me.y} x2={x.x} y2={x.y} stroke={k<=cur?LEAF:"rgba(255,255,255,.15)"} strokeWidth={6}/>)}
  </svg>
  {p.data.items.map((x,k)=><Node key={k} x={x.x} y={x.y} on={k<cur} cur={k===cur} label={x.vi} sub={k<=cur?x.zh:undefined}/>)}
  <Node x={me.x} y={me.y} on cur={false} label="tôi" sub="我"/>
</div>;};

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:BG}}>
  <Brand color={LEAF}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:PALE,border:`2px solid ${LEAF}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 家人</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:PALE}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:900,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:WARM}}>{p.cover[1]}</div>
  <div style={{position:"absolute",inset:0,top:880,opacity:.35,transform:"scale(.7)",transformOrigin:"540px 0"}}><Tree p={p} cur={-1}/></div>
</AbsoluteFill>;

const Family:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[4,3,2,1,0].find(k=>t>=m[`fa${k}`]);
  return <AbsoluteFill style={{background:BG}}>
  <Brand color={LEAF}/>
  <Tree p={p} cur={i??-1}/>
  {i!==undefined&&<div style={{position:"absolute",top:1290,left:90,right:90,textAlign:"center",opacity:ease(t,m[`fa${i}`],m[`fa${i}`]+0.3)}}>
    <div style={{fontFamily:VI,fontSize:104,color:WARM}}>{p.data.items[i].vi}</div>
    <div style={{fontFamily:ZH,fontWeight:900,fontSize:64,color:PALE,marginTop:6}}>{p.data.items[i].zh}</div></div>}
  {i!==undefined&&<div style={{position:"absolute",top:1560,left:150,width:520}}><FollowBar t={t} m={m} k={`fa${i}`} fg={WARM} track="rgba(255,255,255,.12)" muted={DIM} label={`${i+1} / 5`}/></div>}
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:PALE}}>
  <Brand color={BG}/>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:84,color:BG}}>一课一个<span style={{color:"#3f8f4e"}}>生活场景</span></div>
  <div style={{position:"absolute",top:540+(1-up)*60,left:0,right:0,display:"flex",justifyContent:"center",opacity:up}}>
    <div style={{width:720,height:653,borderRadius:120,overflow:"hidden",boxShadow:"0 24px 60px rgba(0,0,0,.25)"}}><Img src={staticFile("img/books.png")} style={{width:"100%",height:"100%",objectFit:"cover"}}/></div></div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <SeriesCtx.Provider value={VI_SERIES}><AbsoluteFill style={{background:BG}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("tree")} t={t}><Family p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, #2f5a43 0%, ${BG} 75%)`} accent={WARM}/></Layer>
  </AbsoluteFill></SeriesCtx.Provider>;};
export const calculateMetadata=calcMeta as any;
