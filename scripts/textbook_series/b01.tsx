// 书本素材版 01：版式沿用原 01（深蓝 + 橙、课本纸、九宫格、两遍读），素材换成书本身 ——
// 九个辅音按书第 10 页的顺序、用书的原声；第二遍跟读时把书上那张"发音方法"卡原样贴出来。
import React from "react";
import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig, interpolate} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, End, ZH, TH, cl, ease, sceneOf, calcMeta} from "./Common";

type Mid={ch:string;hint:string;card:string};
export type SceneProps=BaseProps&{data:{mid:Mid[]}};

const NAVY="#14245e",BLUE="#1f3a93",ORANGE="#f08a2c",PAPER="#f6f0e3",INK="#1b2240",MUTED="#7b7768";

const Ruled:React.FC=()=><AbsoluteFill style={{background:PAPER}}>
  <div style={{position:"absolute",inset:0,backgroundImage:"repeating-linear-gradient(transparent 0 63px, rgba(31,58,147,.08) 63px 65px)"}}/>
  <div style={{position:"absolute",top:0,bottom:0,left:92,width:3,background:"rgba(240,138,44,.35)"}}/>
</AbsoluteFill>;
const Page:React.FC<{name:string;w:number;rot?:number}>=({name,w,rot=0})=><div style={{width:w,background:"#fff",padding:10,borderRadius:8,boxShadow:"0 14px 36px rgba(20,36,94,.16)",transform:`rotate(${rot}deg)`}}><Img src={staticFile(`book/${name}.png`)} style={{width:"100%",display:"block"}}/></div>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:`radial-gradient(ellipse at 50% 48%, ${BLUE} 0%, ${NAVY} 70%)`,overflow:"hidden"}}>
  <div style={{position:"absolute",right:-260,top:380,fontFamily:TH,fontSize:1250,lineHeight:1,color:"#fff",opacity:.055}}>ก</div>
  <Brand color="#f2c46b"/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:"#fff",border:"2px solid rgba(242,196,107,.7)",borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 辅音</div></div>
  <div style={{position:"absolute",top:700,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:170,color:"#fff",letterSpacing:6}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:930,left:330,right:330,height:8,borderRadius:8,background:ORANGE}}/>
  <div style={{position:"absolute",top:990,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:170,color:"#fff",letterSpacing:6}}>先背这<span style={{color:ORANGE}}>9</span>个</div>
  <div style={{position:"absolute",top:1320,left:0,right:0,display:"flex",justifyContent:"center",gap:14}}>{p.data.mid.map(m=><div key={m.ch} style={{width:92,height:104,borderRadius:16,background:"rgba(255,255,255,.1)",display:"flex",alignItems:"center",justifyContent:"center",fontFamily:TH,fontSize:66,lineHeight:1.4,color:"#fff"}}>{m.ch}</div>)}</div>
</AbsoluteFill>;

const Groups:React.FC<{s:{start:number};t:number}>=({s,t})=>{const rows=[["中",9],["高",11],["低",24]] as const;const hi=t>s.start+3.6;return <AbsoluteFill>
  <Ruled/><Brand color={BLUE}/>
  <div style={{position:"absolute",top:360,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:132,color:INK}}><span style={{color:ORANGE}}>44</span> 个辅音</div>
  <div style={{position:"absolute",top:540,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:700,fontSize:58,color:BLUE}}>分三组，组定声调</div>
  {rows.map(([k,n],i)=>{const g=ease(t,s.start+0.9+i*0.55,s.start+1.6+i*0.55);const on=i===0&&hi;return <div key={k} style={{position:"absolute",top:760+i*200,left:120,right:100,height:150,display:"flex",alignItems:"center",gap:30}}>
    <div style={{width:130,height:130,borderRadius:70,background:on?ORANGE:BLUE,color:"#fff",fontFamily:ZH,fontWeight:900,fontSize:70,display:"flex",alignItems:"center",justifyContent:"center"}}>{k}</div>
    <div style={{height:84,width:(n/24)*620*g,borderRadius:14,background:on?ORANGE:"rgba(31,58,147,.75)"}}/>
    <div style={{fontFamily:ZH,fontWeight:900,fontSize:76,color:on?ORANGE:INK,opacity:g}}>{n}</div>
  </div>;})}
  <div style={{position:"absolute",top:1400,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:800,fontSize:50,color:ORANGE,opacity:interpolate(t,[s.start+3.6,s.start+4.1],[0,1],cl)}}>今天先学「中」</div>
</AbsoluteFill>;};

const MidGrid:React.FC<{p:SceneProps;s:{start:number};t:number}>=({p,s,t})=>{const m=p.marks;const inPass2=t>=m.again;
  const a1=[...Array(9).keys()].reverse().find(i=>t>=m[`p${i}`]);const a2=[...Array(9).keys()].reverse().find(i=>t>=m[`m${i}_a`]);
  const active=inPass2?undefined:a1;
  return <AbsoluteFill>
  <Ruled/><Brand color={BLUE}/>
  <div style={{position:"absolute",top:330,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:84,color:INK}}>第 1 课 · 中辅音 <span style={{color:ORANGE}}>9</span> 个</div>
  <div style={{position:"absolute",top:460,left:90,opacity:inPass2?.15:1}}><Page name="row9" w={900}/></div>
  <div style={{position:"absolute",top:610,left:156,width:768,display:"flex",flexWrap:"wrap",gap:24,opacity:inPass2?.07:1}}>
    {p.data.mid.map((x,i)=>{const on=i===active;const pop=ease(t,s.start+0.15+i*0.07,s.start+0.5+i*0.07);return <div key={x.ch} style={{width:240,height:240,borderRadius:26,background:on?ORANGE:"#fff",boxShadow:"0 10px 30px rgba(20,36,94,.12)",opacity:pop,transform:`scale(${(on?1.07:1)*(0.9+0.1*pop)})`,display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"flex-start",position:"relative"}}>
      <div style={{fontFamily:TH,fontSize:124,lineHeight:1.25,marginTop:6,color:on?"#fff":NAVY}}>{x.ch}</div>
      <div style={{position:"absolute",bottom:12,left:0,right:0,textAlign:"center",fontFamily:ZH,fontSize:30,fontWeight:700,color:on?"#fff":MUTED}}>{x.hint}</div>
    </div>;})}
  </div>
  {!inPass2&&<div style={{position:"absolute",top:1420,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:800,fontSize:50,color:BLUE}}>{active===undefined?"听书里的原声":`拼音提示：${p.data.mid[active].hint}`}</div>}
  {inPass2&&(()=>{const x=a2!==undefined?p.data.mid[a2]:undefined;const pop=a2!==undefined?ease(t,m[`m${a2}_a`]-0.05,m[`m${a2}_a`]+0.2):0;return <>
    {x?<>
      <div style={{position:"absolute",top:450,left:0,right:0,textAlign:"center",fontFamily:TH,fontSize:330,lineHeight:1.3,color:NAVY,transform:`scale(${0.94+0.06*pop})`}}>{x.ch}</div>
      <div style={{position:"absolute",top:930,left:70,opacity:pop}}><Page name={x.card} w={940}/></div>
      {(x.ch==="ฎ"||x.ch==="ฏ")&&<div style={{position:"absolute",top:1160,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:46,color:ORANGE}}>书上：{x.ch} 和 {x.ch==="ฎ"?"ด":"ต"} 同音</div>}
      <div style={{position:"absolute",top:1260,left:190,width:700}}><FollowBar t={t} m={m} k={`m${a2}`} fg={ORANGE} track="rgba(31,58,147,.12)" muted={MUTED} label={`${a2!+1} / 9`}/></div>
    </>:<div style={{position:"absolute",top:760,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:90,color:BLUE}}>跟着原声再读一遍</div>}
  </>;})()}
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);const chips=ease(t,s.start+1.2,s.start+1.6);return <AbsoluteFill>
  <Ruled/><Brand color={BLUE}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:INK}}>第 <span style={{color:ORANGE}}>1</span> 册 · 第 <span style={{color:ORANGE}}>1</span> 课</div>
  <div style={{position:"absolute",top:500+(1-up)*60,left:140,opacity:up}}><Page name="lesson" w={800} rot={-2}/></div>
  <div style={{position:"absolute",top:1380,left:0,right:0,display:"flex",justifyContent:"center",gap:20,opacity:chips}}>{["适用培训班学员","附 MP3"].map(x=><div key={x} style={{fontFamily:ZH,fontWeight:900,fontSize:44,color:"#fff",background:ORANGE,borderRadius:18,padding:"10px 28px"}}>{x}</div>)}</div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:PAPER}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("groups")} t={t}><Groups s={S("groups")} t={t}/></Layer>
    <Layer s={S("mid")} t={t}><MidGrid p={p} s={S("mid")} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, ${BLUE} 0%, ${NAVY} 72%)`} accent="#f2c46b"/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
