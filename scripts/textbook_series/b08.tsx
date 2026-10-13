// 书本素材版 08（规则与男女原声取自第 2 册第 1 课）。原注：08 句尾小尾巴：四张卡，男生靛蓝、女生玫红。句子主体是灰的，只有句尾那条"尾巴"上色 ——
// 观众一眼看到：前面一样，差别全在尾巴上；女生提问时尾巴还会变成另一个。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, Books, BookPeek, End, ZH, TH, ease, sceneOf, calcMeta} from "./Common";

type Pair={who:string;base:string;tail:string;zh:string};
export type SceneProps=BaseProps&{data:{pairs:Pair[]}};

const LAV="#f3f1fa",INDIGO="#3949ab",ROSE="#d9537a",INK="#26233a",GRAY="#8b879c";
const col=(who:string)=>who==="男"?INDIGO:ROSE;

const Tail:React.FC<{text:string;color:string;size:number;on?:boolean}>=({text,color,size,on=true})=><span style={{fontFamily:TH,fontSize:size,lineHeight:1.4,color:on?"#fff":color,background:on?color:"transparent",border:`4px solid ${color}`,borderRadius:size*.28,padding:`0 ${size*.22}px`,marginLeft:size*.18}}>{text}</span>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:LAV}}>
  <Brand color={INDIGO}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:INK,border:`2px solid ${ROSE}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 语气词</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:INK,letterSpacing:6}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:INK,letterSpacing:6}}>要加<span style={{color:ROSE}}>尾巴</span></div>
  <div style={{position:"absolute",top:1320,left:0,right:0,display:"flex",justifyContent:"center",gap:30}}>
    <Tail text="ครับ" color={INDIGO} size={70}/><Tail text="ค่ะ" color={ROSE} size={70}/><Tail text="คะ" color={ROSE} size={70} on={false}/>
  </div>
</AbsoluteFill>;

const Mirror:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[3,2,1,0].find(k=>t>=m[`g${k}`])??0;
  return <AbsoluteFill style={{background:LAV}}>
  <Brand color={INDIGO}/>
  <div style={{position:"absolute",top:340,left:190,width:700}}><FollowBar t={t} m={m} k={`g${i}`} fg={col(p.data.pairs[i].who)} track="rgba(38,35,58,.1)" muted={GRAY} label={`${i+1} / 4`}/></div>
  {p.data.pairs.map((x,k)=>{const shown=t>=m[`g${k}`];const cur=k===i;const a=ease(t,m[`g${k}`],m[`g${k}`]+0.35);const c=col(x.who);const q=k===3;
    return <div key={k} style={{position:"absolute",top:480+k*262,left:60,right:60,height:236,borderRadius:30,background:"#fff",border:`4px solid ${cur?c:"transparent"}`,boxShadow:cur?`0 20px 50px ${c}33`:"0 8px 20px rgba(38,35,58,.06)",opacity:shown?(cur?1:.55)*a:.15,transform:`translateX(${(1-a)*(x.who==="男"?-40:40)}px)`,display:"flex",alignItems:"center",padding:"0 34px",gap:26}}>
      <div style={{width:100,height:100,borderRadius:60,background:c,color:"#fff",fontFamily:ZH,fontWeight:900,fontSize:56,display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0}}>{x.who}</div>
      <div style={{flex:1}}>
        <div style={{whiteSpace:"nowrap"}}><span style={{fontFamily:TH,fontSize:80,lineHeight:1.4,color:INK}}>{x.base}</span><Tail text={x.tail} color={c} size={80}/></div>
        <div style={{fontFamily:ZH,fontSize:38,fontWeight:700,color:GRAY}}>{x.zh}{q&&shown&&<span style={{color:ROSE,fontWeight:900}}>　提问 · 声调变了</span>}</div>
      </div>
    </div>;})}
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);const b=ease(t,s.start+1,s.start+1.5);return <AbsoluteFill style={{background:LAV}}>
  <Brand color={INDIGO}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:INK}}>第 <span style={{color:ROSE}}>2</span> 册 · 第 <span style={{color:ROSE}}>1</span> 课</div>
  <div style={{position:"absolute",top:500+(1-up)*60,left:0,right:0,display:"flex",justifyContent:"center",opacity:up}}><BookPeek name="note" w={900} shadow="0 26px 60px rgba(57,73,171,.22)"/></div>
  <div style={{position:"absolute",top:1000,left:0,right:0,display:"flex",justifyContent:"center",gap:20,opacity:b}}>
    <div style={{fontFamily:ZH,fontWeight:900,fontSize:46,color:"#fff",background:INDIGO,borderRadius:18,padding:"10px 30px"}}>男女对读</div>
    <div style={{fontFamily:ZH,fontWeight:900,fontSize:46,color:"#fff",background:ROSE,borderRadius:18,padding:"10px 30px"}}>附原声</div>
  </div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:LAV}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("mirror")} t={t}><Mirror p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`linear-gradient(135deg, ${INDIGO} 0%, #5b3a8f 55%, ${ROSE} 100%)`} accent="#ffd6e2"/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
