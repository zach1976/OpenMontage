// 05 自学三步：一台"播放器"。顶上三段进度 听/跟/对；中间一条声波 ——
// 老师读时是实心波，轮到你跟读时变成空心的虚波；第三步文字才揭开。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate} from "remotion";
import {BaseProps, Brand, Layer, Track, Books, End, ZH, TH, cl, ease, sceneOf, calcMeta} from "./Common";

export type SceneProps=BaseProps&{speak:[number,number][];data:{sentence:{th:string;zh:string;parts:[string,string][]}}};

const COAL="#17181c",COAL2="#23252b",MINT="#4fe0b0",WHITE="#f4f6f5",DIM="rgba(244,246,245,.4)";

const playing=(p:SceneProps,t:number)=>p.audio.some((a,i)=>a.file==="th_x.mp3"&&t>=p.speak[i][0]&&t<p.speak[i][1]);
const inFollow=(p:SceneProps,t:number)=>["r1","r2"].some(k=>t>=p.marks[`${k}_f`]&&t<p.marks[`${k}_f`]+(p.speak.find((_,i)=>p.audio[i].file==="th_x.mp3")![1]-p.speak.find((_,i)=>p.audio[i].file==="th_x.mp3")![0])+0.6);

const Wave:React.FC<{t:number;on:boolean;ghost:boolean;top:number}>=({t,on,ghost,top})=><div style={{position:"absolute",top,left:90,right:90,height:300,display:"flex",alignItems:"center",justifyContent:"space-between"}}>
  {Array.from({length:36}).map((_,i)=>{const n=Math.abs(Math.sin(i*1.7+t*9)*0.6+Math.sin(i*0.6-t*5)*0.4);const h=on||ghost?40+n*250:16;return <div key={i} style={{width:14,height:h,borderRadius:8,background:ghost?"transparent":on?MINT:"rgba(244,246,245,.18)",border:ghost?`3px dashed ${MINT}`:"none"}}/>;})}
</div>;

const Steps:React.FC<{at:number}>=({at})=><div style={{position:"absolute",top:340,left:80,right:80,display:"flex",gap:18}}>
  {["听","跟","对"].map((x,i)=><div key={x} style={{flex:1,textAlign:"center"}}>
    <div style={{height:10,borderRadius:6,background:i<=at?MINT:"rgba(244,246,245,.15)"}}/>
    <div style={{marginTop:16,fontFamily:ZH,fontWeight:900,fontSize:i===at?64:46,color:i===at?MINT:i<at?WHITE:DIM}}>{x}</div>
  </div>)}
</div>;

const Shell:React.FC<{children:React.ReactNode}>=({children})=><AbsoluteFill style={{background:`radial-gradient(ellipse at 50% 45%, ${COAL2} 0%, ${COAL} 70%)`}}><Brand color={MINT}/>{children}</AbsoluteFill>;

const Cover:React.FC<{p:SceneProps}>=({p})=><Shell>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:WHITE,border:"2px solid rgba(79,224,176,.6)",borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 音频</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:WHITE,letterSpacing:6}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:WHITE,letterSpacing:6}}>音频<span style={{color:MINT}}>这样用</span></div>
  <div style={{position:"absolute",top:1320,left:0,right:0,display:"flex",justifyContent:"center",gap:40}}>{["听","跟","对"].map((x,i)=><div key={x} style={{width:120,height:120,borderRadius:70,border:`5px solid ${MINT}`,display:"flex",alignItems:"center",justifyContent:"center",fontFamily:ZH,fontWeight:900,fontSize:60,color:i===0?COAL:MINT,background:i===0?MINT:"transparent"}}>{x}</div>)}</div>
</Shell>;

const Listen:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const n=t>=p.marks.l2?2:t>=p.marks.l1?1:0;return <Shell>
  <Steps at={0}/>
  <div style={{position:"absolute",top:560,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:88,color:WHITE}}>只听，不看字</div>
  <Wave t={t} on={playing(p,t)} ghost={false} top={760}/>
  <div style={{position:"absolute",top:1130,left:120,right:120,textAlign:"center",fontFamily:TH,fontSize:96,lineHeight:1.5,color:WHITE,filter:"blur(22px)",opacity:.5}}>{p.data.sentence.th}</div>
  <div style={{position:"absolute",top:1350,left:0,right:0,display:"flex",justifyContent:"center",gap:24}}>{[1,2].map(k=><div key={k} style={{fontFamily:ZH,fontWeight:800,fontSize:44,color:k<=n?COAL:DIM,background:k<=n?MINT:"transparent",border:`3px solid ${k<=n?MINT:"rgba(244,246,245,.25)"}`,borderRadius:40,padding:"8px 30px"}}>第 {k} 遍</div>)}</div>
</Shell>;};

const Shadow:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const you=inFollow(p,t);const n=t>=p.marks.r2_a?2:t>=p.marks.r1_a?1:0;return <Shell>
  <Steps at={1}/>
  <div style={{position:"absolute",top:560,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:88,color:you?MINT:WHITE}}>{you?"你来读":"跟着读"}</div>
  <Wave t={t} on={playing(p,t)} ghost={you} top={760}/>
  <div style={{position:"absolute",top:1130,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:700,fontSize:48,color:DIM}}>实心是音频 · 虚线是你</div>
  <div style={{position:"absolute",top:1350,left:0,right:0,display:"flex",justifyContent:"center",gap:24}}>{[1,2].map(k=><div key={k} style={{fontFamily:ZH,fontWeight:800,fontSize:44,color:k<=n?COAL:DIM,background:k<=n?MINT:"transparent",border:`3px solid ${k<=n?MINT:"rgba(244,246,245,.25)"}`,borderRadius:40,padding:"8px 30px"}}>跟读 {k}</div>)}</div>
</Shell>;};

const Check:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"check");const m=p.marks;const S=p.data.sentence;
  const ci=p.audio.findIndex(a=>a.file==="th_x.mp3"&&a.at===m.c1);const [c0,c1]=p.speak[ci];
  const total=S.parts.reduce((a,[w])=>a+w.length,0);let acc=0;
  const sum=ease(t,m.sum,m.sum+0.4);
  return <Shell>
  <Steps at={2}/>
  <div style={{position:"absolute",top:560,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:88,color:WHITE}}>再对照文字</div>
  <div style={{position:"absolute",top:780,left:60,right:60,display:"flex",justifyContent:"center",gap:14,opacity:ease(t,s.start+0.3,s.start+0.8)}}>
    {S.parts.map(([w,g],i)=>{const a=c0+(c1-c0)*acc/total;acc+=w.length;const b=c0+(c1-c0)*acc/total;const on=t>=a&&t<b;const miss=i===3&&t>=m.st2+1.6;return <div key={i} style={{display:"flex",flexDirection:"column",alignItems:"center",gap:8}}>
      <div style={{fontFamily:TH,fontSize:84,lineHeight:1.5,color:on?COAL:WHITE,background:on?MINT:"rgba(244,246,245,.06)",borderRadius:18,padding:"0 16px",border:miss?`4px solid #ffcf5a`:"4px solid transparent"}}>{w}</div>
      <div style={{fontFamily:ZH,fontSize:40,fontWeight:800,color:on?MINT:DIM}}>{g}</div>
    </div>;})}
  </div>
  <div style={{position:"absolute",top:1090,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:800,fontSize:56,color:WHITE}}>{S.zh}</div>
  <div style={{position:"absolute",top:1190,left:0,right:0,textAlign:"center",fontFamily:ZH,fontSize:40,color:"#ffcf5a",opacity:interpolate(t,[m.st2+1.6,m.st2+2],[0,1],cl)}}>没听出来的，圈出来</div>
  <div style={{position:"absolute",top:1340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:72,color:MINT,opacity:sum,letterSpacing:10}}>听 · 跟 · 对</div>
</Shell>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <Shell>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:96,color:WHITE}}>每册都<span style={{color:MINT}}>附音频</span></div>
  <div style={{position:"absolute",top:520+(1-up)*60,left:110,opacity:up}}><Books w={860} shadow="0 30px 80px rgba(0,0,0,.6)"/></div>
  <div style={{position:"absolute",top:1340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:800,fontSize:52,color:MINT,opacity:ease(t,s.start+0.9,s.start+1.3)}}>大学泰语专业教材</div>
</Shell>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:COAL}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("listen")} t={t}><Listen p={p} t={t}/></Layer>
    <Layer s={S("shadow")} t={t}><Shadow p={p} t={t}/></Layer>
    <Layer s={S("check")} t={t}><Check p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, ${COAL2} 0%, ${COAL} 72%)`} accent={MINT}/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
