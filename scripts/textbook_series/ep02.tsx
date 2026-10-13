// 02 声调：画面就是一张音高谱 —— 每个词的声调走势被画成一笔，读的时候一笔写出来。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, Books, End, ZH, TH, cl, ease, sceneOf, calcMeta} from "./Common";

type W={th:string;zh:string;tone:string;rom:string;curve:string};
export type SceneProps=BaseProps&{data:{trio:W[];pair:W[]}};

const IVORY="#fbf5ea",RED="#c3202f",INK="#24201e",GRAY="#8d857a",LINE="rgba(36,32,30,.12)";

// 音高 1（低）–5（高），viewBox 600×300
const PATHS:Record<string,string>={
  flat:"M30 150 C 200 150, 400 150, 570 150",
  high:"M30 100 C 200 95, 420 70, 570 45",
  rise:"M30 200 C 180 250, 360 240, 570 50",
  fall:"M30 70 C 220 55, 380 140, 570 250",
  low:"M30 200 C 200 210, 400 225, 570 240",
};

const Curve:React.FC<{kind:string;p:number;w:number;color:string;stroke?:number;staff?:boolean}>=({kind,p,w,color,stroke=16,staff})=>
  <svg width={w} height={w/2} viewBox="0 0 600 300">
    {staff&&[30,90,150,210,270].map(y=><line key={y} x1="0" x2="600" y1={y} y2={y} stroke={LINE} strokeWidth={3}/>)}
    <path d={PATHS[kind]} stroke={color} strokeWidth={stroke} fill="none" strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1-p}/>
  </svg>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:RED,overflow:"hidden"}}>
  <div style={{position:"absolute",inset:0,background:"radial-gradient(ellipse at 50% 45%, rgba(255,255,255,.12), transparent 65%)"}}/>
  <Brand color="#ffe1b0"/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:"#fff",border:"2px solid rgba(255,225,176,.7)",borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 声调</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:"#fff",letterSpacing:6}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:926,left:400}}><Curve kind="rise" p={1} w={280} color="#ffe1b0" stroke={16}/></div>
  <div style={{position:"absolute",top:1040,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:"#fff",letterSpacing:6}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:1330,left:0,right:0,display:"flex",justifyContent:"center",gap:70}}>{p.data.trio.map(w=><div key={w.th} style={{textAlign:"center",color:"#fff"}}><div style={{fontFamily:TH,fontSize:84,lineHeight:1.45}}>{w.th}</div><div style={{fontFamily:ZH,fontSize:40,fontWeight:800,color:"#ffe1b0"}}>{w.zh}</div></div>)}</div>
</AbsoluteFill>;

const Paper:React.FC<{children:React.ReactNode}>=({children})=><AbsoluteFill style={{background:IVORY}}><Brand color={RED}/>{children}</AbsoluteFill>;

const Tones:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"tones");const five=[["中平","flat"],["低","low"],["降","fall"],["高","high"],["升","rise"]];const on=new Set([0,3,4]);const hi=t>s.start+2.4;
  return <Paper>
  <div style={{position:"absolute",top:360,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:130,color:INK}}><span style={{color:RED}}>5</span> 个声调</div>
  <div style={{position:"absolute",top:560,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:700,fontSize:56,color:GRAY}}>今天先听三个</div>
  {five.map(([n,k],i)=>{const a=ease(t,s.start+0.5+i*0.3,s.start+1.1+i*0.3);const lit=hi&&on.has(i);return <div key={n} style={{position:"absolute",top:740+i*150,left:150,right:150,display:"flex",alignItems:"center",gap:40,opacity:hi&&!lit?.28:1}}>
    <div style={{width:150,fontFamily:ZH,fontWeight:900,fontSize:58,color:lit?RED:INK}}>{n}</div>
    <Curve kind={k} p={a} w={440} color={lit?RED:INK} stroke={18}/>
  </div>;})}
</Paper>;};

const Trio:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[2,1,0].find(k=>t>=m[`w${k}`])??0;const w=p.data.trio[i];const draw=ease(t,m[`w${i}_a`],m[`w${i}_a`]+0.7);
  return <Paper>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:800,fontSize:52,color:RED}}>{w.tone}</div>
  <div style={{position:"absolute",top:440,left:90}}><Curve kind={w.curve} p={draw} w={900} color={RED} stroke={20} staff/></div>
  <div style={{position:"absolute",top:930,left:0,right:0,textAlign:"center",fontFamily:TH,fontSize:250,lineHeight:1.35,color:INK}}>{w.th}</div>
  <div style={{position:"absolute",top:1250,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:84,color:RED}}>{w.zh}<span style={{fontSize:44,color:GRAY,fontWeight:600}}>　{w.rom}</span></div>
  <div style={{position:"absolute",top:1420,left:190,width:700}}><FollowBar t={t} m={m} k={`w${i}`} fg={RED} track="rgba(195,32,47,.14)" muted={GRAY} label={`${i+1} / 3`}/></div>
</Paper>;};

const Pair:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const s=sceneOf(p,"pair");const act=t>=m.p1_a?1:t>=m.p0_a?0:-1;
  return <Paper>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:100,color:INK}}>近 <span style={{color:RED}}>≠</span> 远</div>
  <div style={{position:"absolute",top:510,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:700,fontSize:52,color:GRAY}}>只差一个声调</div>
  {p.data.pair.map((w,i)=>{const on=act===i;const d=ease(t,s.start+0.4+i*0.4,s.start+1.2+i*0.4);return <div key={w.th} style={{position:"absolute",top:680+i*390,left:80,right:80,height:340,borderRadius:30,background:on?"#fff":"rgba(255,255,255,.5)",border:`4px solid ${on?RED:"transparent"}`,boxShadow:on?"0 20px 50px rgba(195,32,47,.15)":"none",display:"flex",alignItems:"center",padding:"0 50px",gap:30}}>
    <div style={{width:330}}><div style={{fontFamily:TH,fontSize:150,lineHeight:1.35,color:INK}}>{w.th}</div></div>
    <div style={{flex:1}}><Curve kind={w.curve} p={d} w={300} color={on?RED:INK} stroke={22}/><div style={{fontFamily:ZH,fontSize:64,fontWeight:900,color:on?RED:INK}}>{w.zh}<span style={{fontSize:38,color:GRAY,fontWeight:600}}>　{w.tone}</span></div></div>
  </div>;})}
  {act>=0&&<div style={{position:"absolute",top:1490,left:190,width:700}}><FollowBar t={t} m={m} k={`p${act}`} fg={RED} track="rgba(195,32,47,.14)" muted={GRAY} label={`${act+1} / 2`}/></div>}
</Paper>;};

const Quiz:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const reveal=t>=m.ans;const pulse=t>=m.q&&!reveal?1+0.08*Math.sin((t-m.q)*14):1;
  return <Paper>
  <div style={{position:"absolute",top:360,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:110,color:INK}}>听音选词</div>
  <div style={{position:"absolute",top:560,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{width:190,height:190,borderRadius:100,background:RED,color:"#fff",display:"flex",alignItems:"center",justifyContent:"center",fontFamily:ZH,fontWeight:900,fontSize:110,transform:`scale(${pulse})`}}>?</div></div>
  <div style={{position:"absolute",top:900,left:80,right:80,display:"flex",justifyContent:"space-between"}}>{p.data.trio.map((w,i)=>{const ok=reveal&&i===2;return <div key={w.th} style={{width:290,height:360,borderRadius:28,background:ok?RED:"#fff",boxShadow:"0 16px 40px rgba(36,32,30,.1)",opacity:reveal&&!ok?.35:1,display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",transform:`scale(${ok?1.06:1})`}}>
    <div style={{fontFamily:TH,fontSize:120,lineHeight:1.4,color:ok?"#fff":INK}}>{w.th}</div>
    <div style={{fontFamily:ZH,fontSize:54,fontWeight:900,color:ok?"#ffe1b0":GRAY}}>{reveal?w.zh:"？"}</div>
  </div>;})}</div>
</Paper>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);const stamp=ease(t,s.start+0.9,s.start+1.2);
  return <Paper>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:INK}}>声调规则在第 <span style={{color:RED}}>1</span> 册</div>
  <div style={{position:"absolute",top:520+(1-up)*60,left:120,opacity:up,transform:"rotate(-3deg)"}}><Books w={840} shadow="0 26px 60px rgba(36,32,30,.2)"/></div>
  <div style={{position:"absolute",top:1170,right:90,transform:`rotate(-12deg) scale(${0.6+0.4*stamp})`,opacity:stamp,border:`6px solid ${RED}`,color:RED,borderRadius:18,padding:"10px 26px",fontFamily:ZH,fontWeight:900,fontSize:50,background:"rgba(251,245,234,.85)"}}>附音频</div>
  <div style={{position:"absolute",top:1380,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:800,fontSize:52,color:RED}}>大学泰语专业教材</div>
</Paper>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:IVORY}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("tones")} t={t}><Tones p={p} t={t}/></Layer>
    <Layer s={S("trio")} t={t}><Trio p={p} t={t}/></Layer>
    <Layer s={S("pair")} t={t}><Pair p={p} t={t}/></Layer>
    <Layer s={S("quiz")} t={t}><Quiz p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, #d23a45 0%, #8e1420 75%)`} accent="#ffe1b0"/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
