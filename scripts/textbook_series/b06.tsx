// 书本素材版 06（读音与例句取自第 2 册第 2 课）。原注：06 数字：一块翻页数字牌。每翻一张，底下露出泰语读法和泰文数字 ๑–๑๐；
// 最后一张变成价签 —— 数字真正用上的地方。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, Books, BookPeek, End, ZH, TH, cl, ease, sceneOf, calcMeta} from "./Common";

type Num={n:number;thd:string;th:string};
export type SceneProps=BaseProps&{data:{nums:Num[];use:{th:string;zh:string;parts:[string,string][]}}};

const OFF="#f2efe8",BLACK="#1d1d1d",GOLD="#d9a520",GRAY="#8a857b";

const Flip:React.FC<{n:number;since:number;t:number}>=({n,since,t})=>{const r=interpolate(t,[since,since+0.18],[-90,0],cl);return <div style={{width:620,height:520,borderRadius:36,background:BLACK,position:"relative",perspective:1200,boxShadow:"0 30px 70px rgba(0,0,0,.25)"}}>
  <div style={{position:"absolute",left:0,right:0,top:258,height:4,background:OFF,opacity:.9,zIndex:2}}/>
  <div style={{position:"absolute",inset:0,display:"flex",alignItems:"center",justifyContent:"center",fontFamily:"SF Pro Display, Helvetica, sans-serif",fontWeight:800,fontSize:360,color:"#fff",transform:`rotateX(${r}deg)`,transformOrigin:"50% 50%"}}>{n}</div>
</div>;};

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:OFF}}>
  <Brand color={GOLD}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:BLACK,border:`2px solid ${GOLD}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 数字</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:BLACK,letterSpacing:6}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:960,left:0,right:0,display:"flex",justifyContent:"center",alignItems:"center",gap:30}}>
    {["1","10"].map((x,i)=><React.Fragment key={x}>{i===1&&<div style={{fontFamily:ZH,fontWeight:900,fontSize:120,color:BLACK}}>到</div>}<div style={{background:BLACK,color:"#fff",borderRadius:26,padding:"0 34px",fontFamily:"SF Pro Display, Helvetica, sans-serif",fontWeight:800,fontSize:190,lineHeight:1.2,position:"relative"}}>{x}<div style={{position:"absolute",left:0,right:0,top:"50%",height:4,background:OFF}}/></div></React.Fragment>)}
  </div>
  <div style={{position:"absolute",top:1330,left:0,right:0,display:"flex",justifyContent:"center",gap:18}}>{p.data.nums.map(x=><div key={x.n} style={{fontFamily:TH,fontSize:62,lineHeight:1.4,color:GOLD}}>{x.thd}</div>)}</div>
</AbsoluteFill>;

const Count:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const pass2=t>=m.again;
  const idx=pass2?[...Array(10).keys()].reverse().find(i=>t>=m[`n${i}_a`]):[...Array(10).keys()].reverse().find(i=>t>=m[`p${i}`]);
  const cur=idx===undefined?undefined:p.data.nums[idx];const since=idx===undefined?0:pass2?m[`n${idx}_a`]:m[`p${idx}`];
  return <AbsoluteFill style={{background:OFF}}>
  <Brand color={GOLD}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:64,color:pass2?GOLD:GRAY}}>{pass2?"跟我读":"先听一遍"}</div>
  <div style={{position:"absolute",top:460,left:230}}>{cur?<Flip n={cur.n} since={since} t={t}/>:<Flip n={1} since={-1} t={t}/>}</div>
  {cur&&<div style={{position:"absolute",top:1010,left:0,right:0,display:"flex",justifyContent:"center",alignItems:"center",gap:40}}>
    <div style={{fontFamily:TH,fontSize:130,lineHeight:1.4,color:BLACK}}>{cur.th}</div>
    <div style={{fontFamily:TH,fontSize:96,lineHeight:1.3,color:"#fff",background:GOLD,borderRadius:22,padding:"0 26px"}}>{cur.thd}</div>
  </div>}
  {pass2&&idx!==undefined&&<div style={{position:"absolute",top:1240,left:190,width:700}}><FollowBar t={t} m={m} k={`n${idx}`} fg={GOLD} track="rgba(217,165,32,.16)" muted={GRAY} label={`${idx+1} / 10`}/></div>}
  <div style={{position:"absolute",top:1380,left:110,right:110,display:"flex",justifyContent:"space-between"}}>{p.data.nums.map((x,i)=>{const done=idx!==undefined&&i<=idx;return <div key={x.n} style={{width:72,height:72,borderRadius:14,background:done?BLACK:"transparent",border:`3px solid ${done?BLACK:"rgba(29,29,29,.2)"}`,color:done?"#fff":GRAY,display:"flex",alignItems:"center",justifyContent:"center",fontFamily:"SF Pro Display, Helvetica, sans-serif",fontWeight:800,fontSize:34}}>{x.n}</div>;})}</div>
</AbsoluteFill>;};

const Use:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"use");const m=p.marks;const u=p.data.use;const sw=ease(t,s.start,s.start+0.5);
  return <AbsoluteFill style={{background:OFF}}>
  <Brand color={GOLD}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:88,color:BLACK}}>课文里这样用</div>
  <div style={{position:"absolute",top:520,left:170,width:740,height:520,transform:`rotate(${-6+6*(1-sw)}deg) scale(${0.9+0.1*sw})`,opacity:sw}}>
    <div style={{position:"absolute",inset:0,background:GOLD,borderRadius:"40px 40px 40px 40px",clipPath:"polygon(14% 0, 100% 0, 100% 100%, 14% 100%, 0 50%)"}}/>
    <div style={{position:"absolute",left:46,top:236,width:48,height:48,borderRadius:30,background:OFF}}/>
    <div style={{position:"absolute",left:140,right:30,top:40,textAlign:"center",fontFamily:"SF Pro Display, Helvetica, sans-serif",fontWeight:800,fontSize:200,color:BLACK}}>๔ คน</div>
    <div style={{position:"absolute",left:140,right:30,top:310,display:"flex",justifyContent:"center",gap:26}}>{u.parts.map(([w,g])=><div key={w} style={{textAlign:"center"}}><div style={{fontFamily:TH,fontSize:84,lineHeight:1.4,color:BLACK}}>{w}</div><div style={{fontFamily:ZH,fontSize:34,fontWeight:800,color:"#5a4410"}}>{g}</div></div>)}</div>
  </div>
  <div style={{position:"absolute",top:1120,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:70,color:BLACK}}>{u.zh}</div>
  <div style={{position:"absolute",top:1210,left:0,right:0,display:"flex",justifyContent:"center",opacity:sw}}><BookPeek name="use" w={900}/></div>
  {m.u_f&&<div style={{position:"absolute",top:1340,left:190,width:700}}><FollowBar t={t} m={m} k="u" fg={GOLD} track="rgba(217,165,32,.16)" muted={GRAY}/></div>}
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);const b=ease(t,s.start+1,s.start+1.5);return <AbsoluteFill style={{background:OFF}}>
  <Brand color={GOLD}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:BLACK}}>第 <span style={{color:GOLD}}>2</span> 册 · 第 <span style={{color:GOLD}}>2</span> 课</div>
  <div style={{position:"absolute",top:500+(1-up)*60,left:0,right:0,display:"flex",justifyContent:"center",opacity:up}}><BookPeek name="table" w={860} rot={-1.5}/></div>
  <div style={{position:"absolute",top:930,left:0,right:0,display:"flex",justifyContent:"center",opacity:b}}><BookPeek name="table10" w={760} rot={1.5}/></div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:OFF}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("count")} t={t}><Count p={p} t={t}/></Layer>
    <Layer s={S("use")} t={t}><Use p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, #3a3a3a 0%, ${BLACK} 75%)`} accent={GOLD}/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
