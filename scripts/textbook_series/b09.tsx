// 书本素材版 09（例词、规则与原声取自第 2 册第 1 课）。原注：09 语序：牛皮纸上的便利贴。中文词块先按中文顺序贴好，泰语一开口，
// 词块就当着观众的面挪到下一排、换成泰语的顺序 —— "反着的"是被看见的，不是被告知的。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, Books, BookPeek, End, ZH, TH, ease, sceneOf, calcMeta} from "./Common";

type Item={label:string;zh:string[];th:[string,string][]};
export type SceneProps=BaseProps&{data:{items:Item[]}};

const KRAFT="#c9a274",KRAFT2="#b88f5f",STICKY="#ffd84a",INK="#2a2116",RED="#d6452f",PAPER="#fffbea";
const BG=`radial-gradient(ellipse at 50% 40%, ${KRAFT} 0%, ${KRAFT2} 80%)`;
const GAP=28;
const tileW=(zh:string,th:string)=>Math.max(zh.length*110,th.length*44)+70;

const Sticky:React.FC<{w:number;h:number;rot?:number;children:React.ReactNode;color?:string}>=({w,h,rot=0,children,color=STICKY})=><div style={{width:w,height:h,background:color,transform:`rotate(${rot}deg)`,boxShadow:"0 14px 26px rgba(42,33,22,.28)",display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",position:"relative"}}>
  <div style={{position:"absolute",top:-14,left:"50%",marginLeft:-50,width:100,height:30,background:"rgba(255,255,255,.55)",transform:"rotate(-3deg)"}}/>{children}</div>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:BG}}>
  <Brand color={PAPER}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:PAPER,border:`2px solid ${PAPER}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 语序</div></div>
  <div style={{position:"absolute",top:680,left:0,right:0,display:"flex",justifyContent:"center"}}><Sticky w={820} h={240} rot={-2}><div style={{fontFamily:ZH,fontWeight:900,fontSize:160,color:INK,letterSpacing:6}}>{p.cover[0]}</div></Sticky></div>
  <div style={{position:"absolute",top:990,left:0,right:0,display:"flex",justifyContent:"center"}}><Sticky w={820} h={240} rot={2} color={PAPER}><div style={{fontFamily:ZH,fontWeight:900,fontSize:160,color:RED,letterSpacing:6}}>{p.cover[1]}</div></Sticky></div>
  <div style={{position:"absolute",top:1330,left:0,right:0,display:"flex",justifyContent:"center",alignItems:"center",gap:18,fontFamily:ZH,fontWeight:900,fontSize:56,color:INK}}>
    {["新","生"].map(x=><div key={x} style={{background:STICKY,padding:"4px 20px"}}>{x}</div>)}<div style={{color:PAPER}}>→</div>{["生","新"].map((x,i)=><div key={i} style={{background:PAPER,padding:"4px 20px"}}>{x}</div>)}
  </div>
</AbsoluteFill>;

const Tiles:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[2,1,0].find(k=>t>=m[`o${k}`])??0;const it=p.data.items[i];
  const thOf=(z:string)=>it.th.findIndex(([,g])=>g===z);
  const widths=it.zh.map(z=>tileW(z,it.th[thOf(z)][0]));
  const slotsA:number[]=[],slotsB:number[]=new Array(it.zh.length).fill(0);
  const total=widths.reduce((a,b)=>a+b,0)+GAP*(widths.length-1);
  let x=(1080-total)/2;widths.forEach((w,k)=>{slotsA.push(x);x+=w+GAP;});
  const order=[...it.zh.keys()].sort((a,b)=>thOf(it.zh[a])-thOf(it.zh[b]));
  x=(1080-total)/2;order.forEach(k=>{slotsB[k]=x;x+=widths[k]+GAP;});
  const mv=ease(t,m[`o${i}_a`]-0.2,m[`o${i}_a`]+0.5);const intro=ease(t,m[`o${i}`],m[`o${i}`]+0.3);
  return <AbsoluteFill style={{background:BG}}>
  <Brand color={PAPER}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:96,color:INK}}>{it.label}</div>
  <div style={{position:"absolute",top:520,left:70,fontFamily:ZH,fontWeight:900,fontSize:36,color:PAPER}}>中文</div>
  <div style={{position:"absolute",top:880,left:70,fontFamily:ZH,fontWeight:900,fontSize:36,color:PAPER}}>泰语</div>
  <div style={{position:"absolute",top:930,left:0,right:0,height:4,background:"rgba(255,251,234,.25)"}}/>
  {it.zh.map((z,k)=><div key={`g${k}`} style={{position:"absolute",top:580,left:slotsA[k],width:widths[k],height:220,border:"4px dashed rgba(255,251,234,.45)",opacity:mv}}/>)}
  {it.zh.map((z,k)=>{const left=slotsA[k]+(slotsB[k]-slotsA[k])*mv,top=580+(400*mv);const rot=(k%2?2:-2)*(1-mv*0.5);const thw=it.th[thOf(z)][0];
    return <div key={k} style={{position:"absolute",left,top,opacity:intro}}><Sticky w={widths[k]} h={220+90*mv} rot={rot}>
      <div style={{fontFamily:ZH,fontWeight:900,fontSize:mv>0.5?64:110,color:INK}}>{z}</div>
      {mv>0.5&&<div style={{fontFamily:TH,fontSize:96,lineHeight:1.4,color:RED,opacity:(mv-0.5)*2}}>{thw}</div>}
    </Sticky></div>;})}
  <div style={{position:"absolute",top:1340,left:190,width:700}}><FollowBar t={t} m={m} k={`o${i}`} fg={INK} track="rgba(42,33,22,.15)" muted={PAPER} label={`${i+1} / 3`}/></div>
</AbsoluteFill>;};

const Rule:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const a=ease(t,p.marks.rule,p.marks.rule+0.4),b=ease(t,p.marks.rule+1.2,p.marks.rule+1.6);return <AbsoluteFill style={{background:BG}}>
  <Brand color={PAPER}/>
  <div style={{position:"absolute",top:360,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:84,color:INK}}>书上原话</div>
  <div style={{position:"absolute",top:540,left:0,right:0,display:"flex",justifyContent:"center",opacity:a}}><BookPeek name="note" w={940} rot={-1.5} shadow="0 20px 40px rgba(42,33,22,.35)"/></div>
  <div style={{position:"absolute",top:880,left:0,right:0,display:"flex",justifyContent:"center",opacity:b}}><Sticky w={820} h={230} rot={2}><div style={{fontFamily:ZH,fontWeight:900,fontSize:110,color:INK}}>修饰<span style={{color:RED}}>在后</span></div></Sticky></div>
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:BG}}>
  <Brand color={PAPER}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:INK}}>第 <span style={{color:RED}}>2</span> 册 · 第 <span style={{color:RED}}>1</span> 课</div>
  <div style={{position:"absolute",top:500+(1-up)*60,left:0,right:0,display:"flex",justifyContent:"center",opacity:up}}><BookPeek name="lesson" w={760} rot={1.5} shadow="0 26px 50px rgba(42,33,22,.35)"/></div>
  <div style={{position:"absolute",top:1290,right:90,opacity:ease(t,s.start+0.9,s.start+1.3)}}><Sticky w={300} h={130} rot={-6}><div style={{fontFamily:ZH,fontWeight:900,fontSize:52,color:INK}}>附音频</div></Sticky></div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:KRAFT}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("tiles")} t={t}><Tiles p={p} t={t}/></Layer>
    <Layer s={S("rule")} t={t}><Rule p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, #5a4128 0%, #2e2216 75%)`} accent={STICKY}/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
