// 07 打车：夜里的街道地图。每说一句，路线就往前画一段，粉色出租车沿着线开 ——
// 直走、左转、右转、停在酒店门口。画面就是这五句话的行车记录。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, Books, End, ZH, TH, cl, ease, sceneOf, calcMeta} from "./Common";

type Step={th:string;zh:string;kind:string};
export type SceneProps=BaseProps&{data:{steps:Step[]}};

const ASPH="#1c2027",ROAD="#2b313b",PINK="#ff4f9a",GREEN="#3ddc84",WHITE="#f3f4f6",DIM="rgba(243,244,246,.45)";
const thSize=(s:string)=>s.length>20?66:s.length>14?78:s.length>8?96:120;

// 路线：起点 → 直走 → 左转 → 右转(朝北) → 停在酒店
const PTS:[number,number][]=[[650,1370],[650,1150],[380,1150],[380,880],[380,790]];

const Streets:React.FC=()=><svg style={{position:"absolute",left:0,top:0}} width={1080} height={1920}>
  {[790,880,1150,1370].map(y=><line key={y} x1={60} x2={1020} y1={y} y2={y} stroke={ROAD} strokeWidth={46}/>)}
  {[380,650,880].map(x=><line key={x} x1={x} x2={x} y1={700} y2={1420} stroke={ROAD} strokeWidth={46}/>)}
</svg>;

const Car:React.FC<{x:number;y:number;rot:number}>=({x,y,rot})=><div style={{position:"absolute",left:x-42,top:y-62,width:84,height:124,transform:`rotate(${rot}deg)`}}>
  <div style={{position:"absolute",inset:0,borderRadius:22,background:PINK,boxShadow:`0 0 40px ${PINK}`}}/>
  <div style={{position:"absolute",left:12,right:12,top:20,height:30,borderRadius:8,background:"rgba(0,0,0,.35)"}}/>
  <div style={{position:"absolute",left:0,right:0,top:66,textAlign:"center",fontFamily:"Helvetica, sans-serif",fontWeight:900,fontSize:18,color:ASPH}}>TAXI</div>
</div>;

// 第 k 段路（k=1..4）在第 k 句时画出
const routeAt=(p:SceneProps,t:number)=>{const m=p.marks;let pts:[number,number][]=[PTS[0]];let rot=0;
  for(let k=1;k<=4;k++){const a=m[`t${k}`],b=m[`t${k}_a`]+0.8;if(t<a)break;const q=interpolate(t,[a,b],[0,1],cl);const [x0,y0]=PTS[k-1],[x1,y1]=PTS[k];
    pts=[...pts,[x0+(x1-x0)*q,y0+(y1-y0)*q]];rot=x1<x0?-90:0;if(q<1)break;}
  return {pts,rot};};

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:ASPH,overflow:"hidden"}}>
  <div style={{position:"absolute",inset:0,opacity:.35}}><Streets/></div>
  <Brand color={PINK}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:WHITE,border:`2px solid ${PINK}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 打车</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:WHITE,letterSpacing:6,textShadow:"0 6px 30px rgba(0,0,0,.6)"}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:PINK,letterSpacing:6,textShadow:"0 6px 30px rgba(0,0,0,.6)"}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:1330,left:0,right:0,display:"flex",justifyContent:"center",gap:20}}>{p.data.steps.slice(1,4).map(s=><div key={s.th} style={{fontFamily:TH,fontSize:56,lineHeight:1.45,color:WHITE,border:`3px solid ${GREEN}`,borderRadius:18,padding:"0 22px"}}>{s.th}</div>)}</div>
</AbsoluteFill>;

const Route:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[4,3,2,1,0].find(k=>t>=m[`t${k}`])??0;const st=p.data.steps[i];
  const {pts,rot}=routeAt(p,t);const tip=pts[pts.length-1];const a=ease(t,m[`t${i}`],m[`t${i}`]+0.3);const pin=ease(t,m.t4_a,m.t4_a+0.4);const show=ease(t,m.t0_a-0.1,m.t0_a+0.3);
  return <AbsoluteFill style={{background:ASPH}}>
  <Streets/>
  <Brand color={PINK}/>
  <svg style={{position:"absolute",left:0,top:0}} width={1080} height={1920}><polyline points={pts.map(q=>q.join(",")).join(" ")} fill="none" stroke={GREEN} strokeWidth={16} strokeLinecap="round" strokeLinejoin="round" style={{filter:`drop-shadow(0 0 12px ${GREEN})`}}/></svg>
  <div style={{position:"absolute",left:PTS[4][0]-44,top:PTS[4][1]-150,opacity:pin,transform:`translateY(${(1-pin)*-30}px)`}}>
    <svg width="88" height="110" viewBox="0 0 88 110"><path d="M44 106 C 20 70 4 56 4 40 A 40 40 0 0 1 84 40 C 84 56 68 70 44 106 Z" fill={GREEN}/><circle cx="44" cy="40" r="15" fill={ASPH}/></svg>
    <div style={{position:"absolute",left:100,top:20,whiteSpace:"nowrap",fontFamily:ZH,fontWeight:900,fontSize:44,color:GREEN}}>酒店</div>
  </div>
  <div style={{opacity:show}}><Car x={tip[0]} y={tip[1]} rot={rot}/></div>
  <div style={{position:"absolute",top:340,left:60,right:60,padding:"24px 40px",borderRadius:30,background:"rgba(28,32,39,.92)",border:`3px solid ${PINK}`,opacity:a}}>
    <div style={{fontFamily:ZH,fontWeight:900,fontSize:72,color:PINK}}>{st.zh}</div>
    <div style={{fontFamily:TH,fontSize:thSize(st.th),lineHeight:1.5,color:WHITE}}>{st.th}</div>
  </div>
  <div style={{position:"absolute",top:1470,left:190,width:700}}><FollowBar t={t} m={m} k={`t${i}`} fg={GREEN} track="rgba(243,244,246,.12)" muted={DIM} label={`${i+1} / 5`}/></div>
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:ASPH}}>
  <div style={{position:"absolute",inset:0,opacity:.25}}><Streets/></div>
  <Brand color={PINK}/>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:WHITE}}>日常会话 · 中泰对照</div>
  <div style={{position:"absolute",top:520+(1-up)*60,left:110,opacity:up}}><Books w={860} shadow="0 30px 80px rgba(0,0,0,.6)"/></div>
  <div style={{position:"absolute",top:1340,left:0,right:0,display:"flex",justifyContent:"center",gap:20,opacity:ease(t,s.start+0.9,s.start+1.3)}}>{["1–4 册","附音频"].map(x=><div key={x} style={{fontFamily:ZH,fontWeight:900,fontSize:46,color:ASPH,background:PINK,borderRadius:18,padding:"10px 30px"}}>{x}</div>)}</div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:ASPH}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("route")} t={t}><Route p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, #2c323d 0%, ${ASPH} 72%)`} accent={PINK}/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
