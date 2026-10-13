// 19 生病：一张门诊问诊单夹在写字板上。每句话勾掉一项症状；说到"发烧"时，
// 旁边的体温计一路升到 39.5（课文里的原数字）。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, BookPeek, End, ZH, TH, ease, sceneOf, calcMeta} from "./Common";

type Line={th:string;zh:string;tag:string};
export type SceneProps=BaseProps&{data:{lines:Line[]}};
const MINT="#eef7f6",TEAL="#0f8b8d",RED="#e63946",INK="#1d3557",GRAY="#7c8ea3",BOARD="#c9a26b";
const thSize=(s:string)=>s.length>22?56:s.length>14?66:78;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:MINT}}>
  <Brand color={TEAL}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:INK,border:`2px solid ${TEAL}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 疾病</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:160,color:INK,letterSpacing:4}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:RED,letterSpacing:6}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:1300,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{width:120,height:120,background:RED,clipPath:"polygon(35% 0,65% 0,65% 35%,100% 35%,100% 65%,65% 65%,65% 100%,35% 100%,35% 65%,0 65%,0 35%,35% 35%)"}}/></div>
</AbsoluteFill>;

const Chart:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[4,3,2,1,0].find(k=>t>=m[`s${k}`])??0;const l=p.data.lines[i];
  const temp=36.5+3*(i>=3?ease(t,m.s3,m.s3+1.2):0);const a=ease(t,m[`s${i}`],m[`s${i}`]+0.3);
  return <AbsoluteFill style={{background:MINT}}>
  <Brand color={TEAL}/>
  <div style={{position:"absolute",top:390,left:80,width:720,height:820,borderRadius:26,background:BOARD,boxShadow:"0 20px 40px rgba(29,53,87,.18)"}}>
    <div style={{position:"absolute",top:-26,left:260,width:200,height:60,borderRadius:14,background:"#9aa5b1"}}/>
    <div style={{position:"absolute",top:50,left:30,right:30,bottom:30,background:"#fff",borderRadius:8,padding:"30px 34px"}}>
      <div style={{fontFamily:ZH,fontWeight:900,fontSize:40,color:TEAL,borderBottom:`3px solid ${TEAL}`,paddingBottom:10}}>问诊单</div>
      {p.data.lines.map((x,k)=>{const done=t>=m[`s${k}`];return <div key={k} style={{display:"flex",alignItems:"center",gap:22,marginTop:44,opacity:done?1:.3}}>
        <div style={{width:60,height:60,borderRadius:12,border:`4px solid ${done?TEAL:GRAY}`,background:done?(k===i?RED:TEAL):"transparent",borderColor:done?(k===i?RED:TEAL):GRAY,color:"#fff",fontSize:32,display:"flex",alignItems:"center",justifyContent:"center"}}>{done?"✓":""}</div>
        <div style={{fontFamily:ZH,fontWeight:900,fontSize:60,color:k===i?RED:INK}}>{x.tag}</div>
      </div>;})}
    </div>
  </div>
  <div style={{position:"absolute",top:440,left:850,width:150,height:760}}>
    <div style={{position:"absolute",left:50,top:0,width:50,height:620,borderRadius:30,background:"#fff",border:`5px solid ${GRAY}`}}/>
    <div style={{position:"absolute",left:62,bottom:120,width:26,height:(temp-35)/6*560,borderRadius:14,background:RED}}/>
    <div style={{position:"absolute",left:30,bottom:20,width:90,height:110,borderRadius:60,background:RED}}/>
    <div style={{position:"absolute",left:-10,top:-70,width:170,textAlign:"center",fontFamily:"SF Pro Display, Helvetica, sans-serif",fontWeight:800,fontSize:46,color:temp>38?RED:INK}}>{temp.toFixed(1)}°</div>
  </div>
  <div style={{position:"absolute",top:1250,left:60,right:60,textAlign:"center",opacity:a}}>
    <div style={{fontFamily:ZH,fontWeight:900,fontSize:62,color:INK}}>{l.zh}</div>
    <div style={{fontFamily:TH,fontSize:thSize(l.th),lineHeight:1.45,color:TEAL}}>{l.th}</div>
  </div>
  <div style={{position:"absolute",top:1460,left:190,width:700}}><FollowBar t={t} m={m} k={`s${i}`} fg={RED} track="rgba(29,53,87,.12)" muted={GRAY} label={`${i+1} / 5`}/></div>
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:MINT}}>
  <Brand color={TEAL}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:INK}}>第 <span style={{color:RED}}>2</span> 册 · 第 <span style={{color:RED}}>10</span> 课</div>
  <div style={{position:"absolute",top:500+(1-up)*60,left:0,right:0,display:"flex",justifyContent:"center",opacity:up}}><BookPeek name="dlg" w={860} rot={-1.5}/></div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:MINT}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("chart")} t={t}><Chart p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, ${TEAL} 0%, #0a4f50 75%)`} accent="#c9f2f0"/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
