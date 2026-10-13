// 越 06 打车：俯视街区地图，一个小车点沿路线走。每个词走一段路 ——
// 直走往上、左转拐左、右转拐右、到十字路口亮一圈、最后停在红色停车牌前。词就是路线本身。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, Books, End, ZH, VI, VI_SERIES, SeriesCtx, ease, sceneOf, calcMeta, cl} from "./Common";

type It={vi:string;zh:string;sign:string};
export type SceneProps=BaseProps&{data:{items:It[]}};
const NIGHT="#1b2430",ROAD="#3a4757",LINE="#f4d35e",TAXI="#ffd000",PAPER="#f7f3e8",GRAY="#8c99a8";
const P:[number,number][]=[[450,500],[450,350],[230,350],[230,170],[600,170],[760,170]];

const Sign:React.FC<{s:string;size:number;c:string}>=({s,size,c})=>{const r=size/2;
  if(s==="stop")return <svg width={size} height={size}><polygon points={[0,1,2,3,4,5,6,7].map(k=>{const a=Math.PI/8+k*Math.PI/4;return `${r+Math.cos(a)*r*.96},${r+Math.sin(a)*r*.96}`}).join(" ")} fill="#d62828"/><text x={r} y={r} textAnchor="middle" dominantBaseline="central" fontFamily={ZH} fontWeight={900} fontSize={size*.36} fill="#fff">停</text></svg>;
  if(s==="cross")return <svg width={size} height={size}><rect x={r-size*.12} y={4} width={size*.24} height={size-8} rx={8} fill={c}/><rect x={4} y={r-size*.12} width={size-8} height={size*.24} rx={8} fill={c}/></svg>;
  const rot={up:0,left:-90,right:90}[s as "up"]??0;
  return <svg width={size} height={size} style={{transform:`rotate(${rot}deg)`}}><path d={`M${r} ${size*.08} L${size*.86} ${size*.5} L${size*.62} ${size*.5} L${size*.62} ${size*.92} L${size*.38} ${size*.92} L${size*.38} ${size*.5} L${size*.14} ${size*.5} Z`} fill={c}/></svg>;};

const Map:React.FC<{t:number;m:Record<string,number>;i:number|undefined}>=({t,m,i})=>{
  let x=P[0][0],y=P[0][1];
  if(i!==undefined){const k=i;const pr=interpolate(t,[m[`d${k}_a`],m[`d${k}_f`]],[0,1],cl);const [x0,y0]=P[k],[x1,y1]=P[k+1];x=x0+(x1-x0)*pr;y=y0+(y1-y0)*pr;}
  const done=i===undefined?0:i;
  return <svg width={900} height={560} viewBox="0 0 900 560">
    {[110,230,450,600,760].map(v=><rect key={"v"+v} x={v-26} y={0} width={52} height={560} fill={ROAD}/>)}
    {[170,350,500].map(h=><rect key={"h"+h} x={0} y={h-26} width={900} height={52} fill={ROAD}/>)}
    {[[60,40],[290,40],[500,40],[650,40],[290,215],[500,215],[650,215],[60,215],[60,395],[290,395],[500,395],[650,395]].map(([a,b],k)=><rect key={k} x={a+14} y={b+14} width={a===60?0:110} height={100} rx={10} fill="rgba(255,255,255,.05)"/>)}
    <polyline points={P.slice(0,done+1).map(q=>q.join(",")).join(" ")+` ${x},${y}`} fill="none" stroke={LINE} strokeWidth={12} strokeLinecap="round" strokeLinejoin="round"/>
    <polyline points={P.map(q=>q.join(",")).join(" ")} fill="none" stroke={LINE} strokeOpacity={.22} strokeWidth={6} strokeDasharray="14 14"/>
    {i!==undefined&&i>=3&&<circle cx={600} cy={170} r={54} fill="none" stroke={LINE} strokeWidth={6} opacity={.8}/>}
    <rect x={740} y={110} width={6} height={60} fill="#ccc"/><circle cx={743} cy={100} r={20} fill="#d62828"/>
    <circle cx={x} cy={y} r={26} fill={TAXI} stroke="#111" strokeWidth={5}/>
  </svg>;};

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:NIGHT}}>
  <Brand color={TAXI}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:PAPER,border:`2px solid ${TAXI}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 交通</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:PAPER,letterSpacing:4}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:TAXI,letterSpacing:4}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:1320,left:0,right:0,display:"flex",justifyContent:"center",gap:30}}>{p.data.items.map((x,k)=><div key={k} style={{width:110,height:110,borderRadius:20,background:"rgba(255,255,255,.08)",display:"flex",alignItems:"center",justifyContent:"center"}}><Sign s={x.sign} size={80} c={TAXI}/></div>)}</div>
</AbsoluteFill>;

const Route:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[4,3,2,1,0].find(k=>t>=m[`d${k}`]);const x=i!==undefined?p.data.items[i]:undefined;const a=i!==undefined?ease(t,m[`d${i}`],m[`d${i}`]+0.35):0;
  return <AbsoluteFill style={{background:NIGHT}}>
  <Brand color={TAXI}/>
  <div style={{position:"absolute",top:330,left:90,borderRadius:28,overflow:"hidden",background:"#141b24"}}><Map t={t} m={m} i={i}/></div>
  {x&&<div style={{position:"absolute",top:930,left:90,right:90,height:250,borderRadius:28,background:PAPER,display:"flex",alignItems:"center",gap:36,padding:"0 44px",opacity:a,transform:`translateY(${(1-a)*30}px)`}}>
    <Sign s={x.sign} size={150} c={NIGHT}/>
    <div><div style={{fontFamily:VI,fontSize:96,lineHeight:1.3,color:NIGHT}}>{x.vi}</div><div style={{fontFamily:ZH,fontWeight:900,fontSize:56,color:"#b08900"}}>{x.zh}</div></div>
  </div>}
  {i!==undefined&&<div style={{position:"absolute",top:1230,left:190,width:700}}><FollowBar t={t} m={m} k={`d${i}`} fg={TAXI} track="rgba(255,255,255,.14)" muted={GRAY} label={`${i+1} / 5`}/></div>}
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:NIGHT}}>
  <Brand color={TAXI}/>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:PAPER}}>会话 · 生词 · <span style={{color:TAXI}}>语法</span></div>
  <div style={{position:"absolute",top:520+(1-up)*60,left:110,opacity:up,transform:"rotate(2deg)"}}><Books w={860} radius={14} shadow="0 30px 70px rgba(0,0,0,.55)"/></div>
  <div style={{position:"absolute",top:1340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:48,color:TAXI,opacity:ease(t,s.start+0.9,s.start+1.3)}}>基础越南语 · 共 4 册</div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <SeriesCtx.Provider value={VI_SERIES}><AbsoluteFill style={{background:NIGHT}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("route")} t={t}><Route p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, #2d3b4d 0%, ${NIGHT} 75%)`} accent={TAXI}/></Layer>
  </AbsoluteFill></SeriesCtx.Provider>;};
export const calculateMetadata=calcMeta as any;
