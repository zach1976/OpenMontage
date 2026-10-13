// 18 打电话：画面就是一通正在进行的电话。通话计时在走，对方（总机/接电话的人）的话在左、
// 我的话在右，一来一回就是课本那两段电话对话。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, BookPeek, End, ZH, TH, ease, sceneOf, calcMeta} from "./Common";

type Line={th:string;zh:string;who:string};
export type SceneProps=BaseProps&{data:{lines:Line[]}};
const BLACK="#0b0b0f",PANEL="#1c1c22",GREEN="#34c759",WHITE="#f5f5f7",DIM="rgba(245,245,247,.45)",BLUE="#0a84ff";
const thSize=(s:string)=>s.length>20?58:s.length>14?68:80;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:BLACK}}>
  <Brand color={GREEN}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:WHITE,border:`2px solid ${GREEN}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 打电话</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:WHITE,letterSpacing:6}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:GREEN,letterSpacing:6}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:1320,left:0,right:0,display:"flex",justifyContent:"center",gap:80}}>
    {[GREEN,"#ff3b30"].map(c=><div key={c} style={{width:130,height:130,borderRadius:70,background:c,display:"flex",alignItems:"center",justifyContent:"center"}}><svg width="64" height="64" viewBox="0 0 24 24" style={{transform:c===GREEN?"none":"rotate(135deg)"}}><path d="M6.6 10.8a15 15 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.6a1 1 0 0 1-.25 1z" fill="#fff"/></svg></div>)}
  </div>
</AbsoluteFill>;

const Call:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const s=sceneOf(p,"call");const i=[3,2,1,0].find(k=>t>=m[`p${k}`])??0;
  const sec=Math.max(0,Math.floor(t-s.start));const timer=`${String(Math.floor(sec/60)).padStart(2,"0")}:${String(sec%60).padStart(2,"0")}`;
  return <AbsoluteFill style={{background:BLACK}}>
  <Brand color={GREEN}/>
  <div style={{position:"absolute",top:330,left:0,right:0,textAlign:"center"}}>
    <div style={{fontFamily:ZH,fontSize:40,color:DIM}}>通话中</div>
    <div style={{fontFamily:"SF Pro Display, Helvetica, sans-serif",fontWeight:300,fontSize:64,color:WHITE,letterSpacing:4}}>{timer}</div>
  </div>
  <div style={{position:"absolute",top:490,left:40,right:40,display:"flex",flexDirection:"column",gap:24}}>
    {p.data.lines.map((l,k)=>{if(t<m[`p${k}`])return null;const a=ease(t,m[`p${k}`],m[`p${k}`]+0.3);const me=l.who==="me";const cur=k===i;
      return <div key={k} style={{alignSelf:me?"flex-end":"flex-start",maxWidth:960,opacity:(cur?1:.45)*a,transform:`translateY(${(1-a)*20}px)`}}>
        <div style={{background:me?GREEN:PANEL,color:me?BLACK:WHITE,borderRadius:me?"34px 34px 8px 34px":"34px 34px 34px 8px",padding:"16px 32px"}}>
          <div style={{fontFamily:TH,fontSize:thSize(l.th),lineHeight:1.5}}>{l.th}</div>
          <div style={{fontFamily:ZH,fontWeight:800,fontSize:38,opacity:.85}}>{l.zh}</div>
        </div>
      </div>;})}
  </div>
  <div style={{position:"absolute",top:1430,left:190,width:700}}><FollowBar t={t} m={m} k={`p${i}`} fg={GREEN} track="rgba(245,245,247,.12)" muted={DIM} label={`${i+1} / 4`}/></div>
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:BLACK}}>
  <Brand color={GREEN}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:WHITE}}>第 <span style={{color:GREEN}}>2</span> 册 · 第 <span style={{color:GREEN}}>9</span> 课</div>
  <div style={{position:"absolute",top:500+(1-up)*60,left:0,right:0,display:"flex",justifyContent:"center",opacity:up}}><BookPeek name="dlg" w={860} shadow="0 30px 80px rgba(0,0,0,.7)"/></div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:BLACK}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("call")} t={t}><Call p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, #1d3a26 0%, ${BLACK} 75%)`} accent={GREEN}/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
