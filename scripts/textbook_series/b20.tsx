// 20 季节：一只年轮转盘。泰国这一圈只分三段（热/雨/凉），转盘真的就切成三块；
// 最后一句"中国四个"，转盘重新切成四块（春夏秋冬）—— 三和四的差别是切出来给人看的。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, BookPeek, End, ZH, TH, ease, sceneOf, calcMeta} from "./Common";

type Line={th:string;zh:string;lit:number[]};
type Seg=[string,string,string];
export type SceneProps=BaseProps&{data:{lines:Line[];thai:Seg[];china:Seg[]}};
const SAND="#fff7ea",INK="#2b2118",GRAY="#9a8b78",SUN="#ff7b2e";
const thSize=(s:string)=>s.length>22?62:s.length>14?74:88;

const Wheel:React.FC<{segs:Seg[];lit:number[];size:number;spin:number}>=({segs,lit,size,spin})=>{const r=size/2,n=segs.length;
  return <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{transform:`rotate(${spin}deg)`}}>
    {segs.map(([th,zh,c],k)=>{const a0=(k/n)*2*Math.PI-Math.PI/2,a1=((k+1)/n)*2*Math.PI-Math.PI/2;const on=!lit.length||lit.includes(k);
      const x0=r+Math.cos(a0)*(r-6),y0=r+Math.sin(a0)*(r-6),x1=r+Math.cos(a1)*(r-6),y1=r+Math.sin(a1)*(r-6);const am=(a0+a1)/2;
      return <g key={k} opacity={on?1:.25}><path d={`M${r} ${r} L${x0} ${y0} A${r-6} ${r-6} 0 0 1 ${x1} ${y1} Z`} fill={c} stroke={SAND} strokeWidth={8}/>
        <text x={r+Math.cos(am)*r*0.58} y={r+Math.sin(am)*r*0.58} textAnchor="middle" dominantBaseline="middle" fontFamily={ZH} fontWeight={900} fontSize={size*0.09} fill="#fff" transform={`rotate(${-spin} ${r+Math.cos(am)*r*0.58} ${r+Math.sin(am)*r*0.58})`}>{zh}</text></g>;})}
    <circle cx={r} cy={r} r={r*0.18} fill={SAND}/>
  </svg>;};

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:SAND}}>
  <Brand color={SUN}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:INK,border:`2px solid ${SUN}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 季节</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:INK,letterSpacing:6}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:140,color:SUN,letterSpacing:4}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:1260,left:0,right:0,display:"flex",justifyContent:"center"}}><Wheel segs={p.data.thai} lit={[]} size={220} spin={0}/></div>
</AbsoluteFill>;

const WheelScene:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[3,2,1,0].find(k=>t>=m[`q${k}`])??0;const l=p.data.lines[i];const china=i===3;
  const a=ease(t,m[`q${i}`],m[`q${i}`]+0.35);const spin=(t-sceneOf(p,"wheel").start)*6;
  return <AbsoluteFill style={{background:SAND}}>
  <Brand color={SUN}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:56,color:china?"#c0392b":SUN}}>{china?"中国 · 四季":"泰国 · 三季"}</div>
  <div style={{position:"absolute",top:440,left:0,right:0,display:"flex",justifyContent:"center",opacity:china?ease(t,m.q3,m.q3+0.5):1}}><Wheel segs={china?p.data.china:p.data.thai} lit={l.lit} size={540} spin={spin}/></div>
  <div style={{position:"absolute",top:1010,left:60,right:60,textAlign:"center",opacity:a}}>
    <div style={{fontFamily:ZH,fontWeight:900,fontSize:70,color:INK}}>{l.zh}</div>
    <div style={{fontFamily:TH,fontSize:thSize(l.th),lineHeight:1.5,color:SUN}}>{l.th}</div>
  </div>
  <div style={{position:"absolute",top:1290,left:190,width:700}}><FollowBar t={t} m={m} k={`q${i}`} fg={SUN} track="rgba(255,123,46,.14)" muted={GRAY} label={`${i+1} / 4`}/></div>
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:SAND}}>
  <Brand color={SUN}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:INK}}>第 <span style={{color:SUN}}>2</span> 册 · 第 <span style={{color:SUN}}>12</span> 课</div>
  <div style={{position:"absolute",top:500+(1-up)*60,left:0,right:0,display:"flex",justifyContent:"center",opacity:up}}><BookPeek name="dlg" w={880} rot={1.5}/></div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:SAND}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("wheel")} t={t}><WheelScene p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, ${SUN} 0%, #a8431a 75%)`} accent="#fff1c9"/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
