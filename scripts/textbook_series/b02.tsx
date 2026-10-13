// 书本素材版 02：版式沿用原 02（象牙白 + 书名红、音高谱），素材换成书第 1 册第 3 课 ——
// 五声调总览贴书上的声调表；"以 ก 为例"的五个音用书的原声，每个音读的时候把走势画出来；
// 一对最小对立词和听音选词都出自第 30 页词汇表。
import React from "react";
import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, End, ZH, TH, ease, sceneOf, calcMeta} from "./Common";

type T={th:string;tone:string;desc?:string;zh?:string;curve:string};
export type SceneProps=BaseProps&{data:{five:T[];pair:T[];quiz:{th:string;zh:string}[];answer:number}};

const IVORY="#fbf5ea",RED="#c3202f",INK="#24201e",GRAY="#8d857a",LINE="rgba(36,32,30,.12)";
const PATHS:Record<string,string>={
  flat:"M30 150 C 200 150, 400 150, 570 150",
  low:"M30 200 C 200 210, 400 225, 570 240",
  fall:"M30 70 C 220 55, 380 140, 570 250",
  high:"M30 110 C 220 120, 400 90, 570 40",
  rise:"M30 200 C 180 250, 360 240, 570 50",
};
const Curve:React.FC<{kind:string;p:number;w:number;color:string;stroke?:number;staff?:boolean}>=({kind,p,w,color,stroke=16,staff})=>
  <svg width={w} height={w/2} viewBox="0 0 600 300">
    {staff&&[30,90,150,210,270].map(y=><line key={y} x1="0" x2="600" y1={y} y2={y} stroke={LINE} strokeWidth={3}/>)}
    <path d={PATHS[kind]} stroke={color} strokeWidth={stroke} fill="none" strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1-p}/>
  </svg>;
const Page:React.FC<{name:string;w:number;rot?:number}>=({name,w,rot=0})=><div style={{width:w,background:"#fff",padding:10,borderRadius:8,boxShadow:"0 14px 36px rgba(36,32,30,.16)",transform:`rotate(${rot}deg)`}}><Img src={staticFile(`book/${name}.png`)} style={{width:"100%",display:"block"}}/></div>;
const Paper:React.FC<{children:React.ReactNode}>=({children})=><AbsoluteFill style={{background:IVORY}}><Brand color={RED}/>{children}</AbsoluteFill>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:RED,overflow:"hidden"}}>
  <div style={{position:"absolute",inset:0,background:"radial-gradient(ellipse at 50% 45%, rgba(255,255,255,.12), transparent 65%)"}}/>
  <Brand color="#ffe1b0"/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:"#fff",border:"2px solid rgba(255,225,176,.7)",borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 声调</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:"#fff",letterSpacing:6}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:926,left:400}}><Curve kind="rise" p={1} w={280} color="#ffe1b0" stroke={16}/></div>
  <div style={{position:"absolute",top:1040,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:"#fff",letterSpacing:6}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:1330,left:0,right:0,display:"flex",justifyContent:"center",gap:40}}>{p.data.five.map(w=><div key={w.th} style={{fontFamily:TH,fontSize:76,lineHeight:1.45,color:"#fff"}}>{w.th}</div>)}</div>
</AbsoluteFill>;

const Tones:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"tones");const a=ease(t,s.start,s.start+0.5);return <Paper>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:110,color:INK}}><span style={{color:RED}}>5</span> 个声调</div>
  <div style={{position:"absolute",top:520,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:700,fontSize:50,color:GRAY}}>书上第 3 课的声调表</div>
  <div style={{position:"absolute",top:640+(1-a)*50,left:80,opacity:a}}><Page name="table" w={920}/></div>
</Paper>;};

const Five:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[4,3,2,1,0].find(k=>t>=m[`t${k}`])??0;const w=p.data.five[i];const draw=ease(t,m[`t${i}_a`],m[`t${i}_a`]+0.7);
  return <Paper>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:60,color:RED}}>{w.tone}<span style={{color:GRAY,fontWeight:700,fontSize:46}}>　{w.desc}</span></div>
  <div style={{position:"absolute",top:430,left:140}}><Curve kind={w.curve} p={draw} w={800} color={RED} stroke={20} staff/></div>
  <div style={{position:"absolute",top:830,left:0,right:0,textAlign:"center",fontFamily:TH,fontSize:250,lineHeight:1.35,color:INK}}>{w.th}</div>
  <div style={{position:"absolute",top:1190,left:190,width:700}}><FollowBar t={t} m={m} k={`t${i}`} fg={RED} track="rgba(195,32,47,.14)" muted={GRAY} label={`${i+1} / 5`}/></div>
  <div style={{position:"absolute",top:1320,left:150}}><Page name="ka" w={780}/></div>
</Paper>;};

const Pair:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const s=sceneOf(p,"pair");const act=t>=m.p1_a?1:t>=m.p0_a?0:-1;
  return <Paper>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:100,color:INK}}>旧 <span style={{color:RED}}>≠</span> 九</div>
  <div style={{position:"absolute",top:500,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:700,fontSize:50,color:GRAY}}>只差一个声调</div>
  {p.data.pair.map((w,i)=>{const on=act===i;const d=ease(t,s.start+0.4+i*0.4,s.start+1.2+i*0.4);return <div key={w.th} style={{position:"absolute",top:640+i*340,left:80,right:80,height:300,borderRadius:30,background:on?"#fff":"rgba(255,255,255,.5)",border:`4px solid ${on?RED:"transparent"}`,boxShadow:on?"0 20px 50px rgba(195,32,47,.15)":"none",display:"flex",alignItems:"center",padding:"0 50px",gap:30}}>
    <div style={{width:330,fontFamily:TH,fontSize:150,lineHeight:1.35,color:INK}}>{w.th}</div>
    <div style={{flex:1}}><Curve kind={w.curve} p={d} w={300} color={on?RED:INK} stroke={22}/><div style={{fontFamily:ZH,fontSize:64,fontWeight:900,color:on?RED:INK}}>{w.zh}<span style={{fontSize:38,color:GRAY,fontWeight:600}}>　{w.tone}</span></div></div>
  </div>;})}
  {act>=0&&<div style={{position:"absolute",top:1330,left:190,width:700}}><FollowBar t={t} m={m} k={`p${act}`} fg={RED} track="rgba(195,32,47,.14)" muted={GRAY} label={`${act+1} / 2`}/></div>}
</Paper>;};

const Quiz:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const reveal=t>=m.ans;const pulse=t>=m.q&&!reveal?1+0.08*Math.sin((t-m.q)*14):1;
  return <Paper>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:110,color:INK}}>听音选词</div>
  <div style={{position:"absolute",top:540,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{width:190,height:190,borderRadius:100,background:RED,color:"#fff",display:"flex",alignItems:"center",justifyContent:"center",fontFamily:ZH,fontWeight:900,fontSize:110,transform:`scale(${pulse})`}}>?</div></div>
  <div style={{position:"absolute",top:860,left:110,right:110,display:"flex",justifyContent:"space-between"}}>{p.data.quiz.map((w,i)=>{const ok=reveal&&i===p.data.answer;return <div key={w.th} style={{width:400,height:400,borderRadius:30,background:ok?RED:"#fff",boxShadow:"0 16px 40px rgba(36,32,30,.1)",opacity:reveal&&!ok?.35:1,display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",transform:`scale(${ok?1.06:1})`}}>
    <div style={{fontFamily:TH,fontSize:150,lineHeight:1.4,color:ok?"#fff":INK}}>{w.th}</div>
    <div style={{fontFamily:ZH,fontSize:60,fontWeight:900,color:ok?"#ffe1b0":GRAY}}>{reveal?w.zh:"？"}</div>
  </div>;})}</div>
</Paper>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);const stamp=ease(t,s.start+0.9,s.start+1.2);
  return <Paper>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:INK}}>第 <span style={{color:RED}}>1</span> 册 · 第 <span style={{color:RED}}>3</span> 课</div>
  <div style={{position:"absolute",top:500+(1-up)*60,left:140,opacity:up}}><Page name="lesson" w={800} rot={-2}/></div>
  <div style={{position:"absolute",top:1300,right:90,transform:`rotate(-12deg) scale(${0.6+0.4*stamp})`,opacity:stamp,border:`6px solid ${RED}`,color:RED,borderRadius:18,padding:"10px 26px",fontFamily:ZH,fontWeight:900,fontSize:50,background:"rgba(251,245,234,.9)"}}>附 MP3</div>
</Paper>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:IVORY}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("tones")} t={t}><Tones p={p} t={t}/></Layer>
    <Layer s={S("five")} t={t}><Five p={p} t={t}/></Layer>
    <Layer s={S("pair")} t={t}><Pair p={p} t={t}/></Layer>
    <Layer s={S("quiz")} t={t}><Quiz p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, #d23a45 0%, #8e1420 75%)`} accent="#ffe1b0"/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
