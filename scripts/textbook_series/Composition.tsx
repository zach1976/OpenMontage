import React from "react";
import {AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame, useVideoConfig, interpolate, CalculateMetadataFunction} from "remotion";

type Mid={ch:string;name:string;anchor:string;live:boolean};
type SceneT={id:string;start:number;end:number;label:string;text:string};
export type SceneProps={fps:number;totalFrames:number;totalSeconds:number;mid:Mid[];pass1:{i:number;at:number}[];pass2:{i:number;at:number;gap:number}[];scenes:SceneT[];audio:{file:string;at:number}[];bgm:{file:string;volume:number};review_timeline:unknown[]};

// 课本世界：封面蓝 + 郑王庙晨光橙 + 课本纸
const NAVY="#14245e",BLUE="#1f3a93",ORANGE="#f08a2c",PAPER="#f6f0e3",INK="#1b2240",MUTED="#7b7768";
const ZH="PingFang SC, Noto Sans CJK SC, sans-serif",TH="ThaiBold, Thonburi, sans-serif";
const cl={extrapolateLeft:"clamp",extrapolateRight:"clamp"} as const;
const ease=(t:number,a:number,b:number)=>{const x=interpolate(t,[a,b],[0,1],cl);return 1-Math.pow(1-x,3);};

const Brand:React.FC<{dark?:boolean}>=({dark})=><div style={{position:"absolute",top:270,left:0,right:0,textAlign:"center",fontFamily:ZH,fontSize:32,fontWeight:700,letterSpacing:4,color:dark?"#f2c46b":BLUE}}>泰语千词 · 跟着教材学</div>;

const Ruled:React.FC=()=><AbsoluteFill style={{background:PAPER}}>
  <div style={{position:"absolute",inset:0,backgroundImage:"repeating-linear-gradient(transparent 0 63px, rgba(31,58,147,.08) 63px 65px)"}}/>
  <div style={{position:"absolute",top:0,bottom:0,left:92,width:3,background:"rgba(240,138,44,.35)"}}/>
</AbsoluteFill>;

const Layer:React.FC<{s:SceneT;t:number;first?:boolean;children:React.ReactNode}>=({s,t,first,children})=>{
  if(t<s.start-0.01||t>=s.end+0.3)return null;
  const o=Math.min(first?1:interpolate(t,[s.start,s.start+0.27],[0,1],cl),interpolate(t,[s.end,s.end+0.27],[1,0],cl));
  return <AbsoluteFill style={{opacity:o}}>{children}</AbsoluteFill>;
};

/* 封面：第 0 帧即成品；标题整个落在 660–1260 */
const Cover:React.FC<{mid:Mid[]}>=({mid})=><AbsoluteFill style={{background:`radial-gradient(ellipse at 50% 48%, ${BLUE} 0%, ${NAVY} 70%)`,overflow:"hidden"}}>
  <div style={{position:"absolute",right:-260,top:380,fontFamily:TH,fontSize:1250,lineHeight:1,color:"#fff",opacity:.055}}>ก</div>
  <Brand dark/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:"#fff",border:"2px solid rgba(242,196,107,.7)",borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · No.01</div></div>
  <div style={{position:"absolute",top:700,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:170,color:"#fff",letterSpacing:6}}>泰语第一课</div>
  <div style={{position:"absolute",top:930,left:330,right:330,height:8,borderRadius:8,background:ORANGE}}/>
  <div style={{position:"absolute",top:990,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:170,color:"#fff",letterSpacing:6}}>先背这<span style={{color:ORANGE}}>9</span>个</div>
  <div style={{position:"absolute",top:1320,left:0,right:0,display:"flex",justifyContent:"center",gap:14}}>{mid.map(m=><div key={m.ch} style={{width:92,height:104,borderRadius:16,background:"rgba(255,255,255,.1)",display:"flex",alignItems:"center",justifyContent:"center",fontFamily:TH,fontSize:66,lineHeight:1.4,color:"#fff",opacity:m.live?.9:.4}}>{m.ch}</div>)}</div>
</AbsoluteFill>;

/* 44 → 三组：条形长度就是个数 */
const Groups:React.FC<{s:SceneT;t:number}>=({s,t})=>{const rows=[["中",9],["高",11],["低",24]] as const;const hi=t>s.start+3.6;return <AbsoluteFill>
  <Ruled/><Brand/>
  <div style={{position:"absolute",top:360,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:132,color:INK}}><span style={{color:ORANGE}}>44</span> 个辅音</div>
  <div style={{position:"absolute",top:540,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:700,fontSize:58,color:BLUE}}>分三组，组定声调</div>
  {rows.map(([k,n],i)=>{const g=ease(t,s.start+0.9+i*0.55,s.start+1.6+i*0.55);const on=i===0&&hi;return <div key={k} style={{position:"absolute",top:760+i*200,left:120,right:100,height:150,display:"flex",alignItems:"center",gap:30}}>
    <div style={{width:130,height:130,borderRadius:70,background:on?ORANGE:BLUE,color:"#fff",fontFamily:ZH,fontWeight:900,fontSize:70,display:"flex",alignItems:"center",justifyContent:"center"}}>{k}</div>
    <div style={{height:84,width:(n/24)*620*g,borderRadius:14,background:on?ORANGE:"rgba(31,58,147,.75)"}}/>
    <div style={{fontFamily:ZH,fontWeight:900,fontSize:76,color:on?ORANGE:INK,opacity:g}}>{n}</div>
  </div>;})}
  <div style={{position:"absolute",top:1400,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:800,fontSize:50,color:ORANGE,opacity:interpolate(t,[s.start+3.6,s.start+4.1],[0,1],cl)}}>今天先学「中」</div>
</AbsoluteFill>;};

/* 中辅音九宫格：第一遍逐个点亮，第二遍放大跟读 */
const MidGrid:React.FC<{p:SceneProps;s:SceneT;t:number}>=({p,s,t})=>{
  const againAt=p.audio.find(a=>a.file==="again.mp3")!.at;
  const cur1=[...p.pass1].reverse().find(x=>t>=x.at);
  const inPass2=t>=againAt;
  const cur2=[...p.pass2].reverse().find(x=>t>=x.at);
  const active=inPass2?undefined:cur1?.i;
  return <AbsoluteFill>
  <Ruled/><Brand/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:100,color:INK}}>中辅音 · <span style={{color:ORANGE}}>9</span> 个</div>
  <div style={{position:"absolute",top:520,left:105,width:870,display:"flex",flexWrap:"wrap",gap:30,opacity:inPass2?.07:1}}>
    {p.mid.map((m,i)=>{const on=i===active;const pop=ease(t,s.start+0.15+i*0.07,s.start+0.5+i*0.07);return <div key={m.ch} style={{width:270,height:270,borderRadius:28,background:on?ORANGE:"#fff",boxShadow:"0 10px 30px rgba(20,36,94,.12)",opacity:(m.live?1:.38)*pop,transform:`scale(${(on?1.07:1)*(0.9+0.1*pop)})`,display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",position:"relative"}}>
      <div style={{fontFamily:TH,fontSize:150,lineHeight:1.3,color:on?"#fff":NAVY}}>{m.ch}</div>
      {m.live&&<div style={{fontFamily:ZH,fontSize:40,fontWeight:700,color:on?"#fff":MUTED,marginTop:-14}}>{m.anchor}</div>}
      {!m.live&&<div style={{position:"absolute",top:16,right:16,fontFamily:ZH,fontSize:26,color:MUTED,border:`2px solid ${MUTED}`,borderRadius:10,padding:"0 8px"}}>少用</div>}
    </div>;})}
  </div>
  {!inPass2&&<div style={{position:"absolute",top:1450,left:0,right:0,textAlign:"center"}}>
    {active===undefined
      ?<div style={{fontFamily:ZH,fontWeight:800,fontSize:56,color:BLUE}}>常用的是这 7 个</div>
      :<div style={{fontFamily:TH,fontSize:84,lineHeight:1.45,color:INK}}>{p.mid[active].name}<span style={{fontFamily:ZH,fontSize:56,color:ORANGE,fontWeight:800}}>　{p.mid[active].anchor}</span></div>}
  </div>}
  {inPass2&&(()=>{const m=cur2?p.mid[cur2.i]:undefined;const k=cur2?p.pass2.indexOf(cur2)+1:0;
    const readDur=cur2?cur2.gap-0.55:0;const follow=cur2?interpolate(t,[cur2.at+readDur,cur2.at+readDur+cur2.gap],[0,1],cl):0;const listening=cur2?t<cur2.at+readDur:true;
    return <>
    <div style={{position:"absolute",top:540,left:190,width:700,height:780,borderRadius:40,background:"#fff",boxShadow:"0 24px 70px rgba(20,36,94,.2)",display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center"}}>
      {m?<>
        <div style={{fontFamily:TH,fontSize:330,lineHeight:1.3,color:NAVY}}>{m.ch}</div>
        <div style={{fontFamily:TH,fontSize:76,lineHeight:1.4,color:INK}}>{m.name}</div>
      </>:<div style={{fontFamily:ZH,fontWeight:900,fontSize:90,color:BLUE}}>再读一遍</div>}
    </div>
    {m&&<div style={{position:"absolute",top:1380,left:190,width:700}}>
      <div style={{display:"flex",justifyContent:"space-between",fontFamily:ZH,fontWeight:800,fontSize:46,color:listening?BLUE:ORANGE}}><span>{listening?"听":"你来读"}</span><span style={{color:MUTED}}>{k} / 7</span></div>
      <div style={{marginTop:14,height:14,borderRadius:10,background:"rgba(31,58,147,.12)"}}><div style={{height:14,borderRadius:10,width:`${follow*100}%`,background:ORANGE}}/></div>
    </div>}
  </>;})()}
</AbsoluteFill>;};

/* 回到书：今天这一课在第 1 册 */
const Book:React.FC<{s:SceneT;t:number}>=({s,t})=>{const up=ease(t,s.start,s.start+0.6);const chips=["发音","语法","课文","写作"];return <AbsoluteFill>
  <Ruled/><Brand/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:INK}}>大学泰语专业教材</div>
  <div style={{position:"absolute",top:500+(1-up)*80,left:90,width:900,height:816,borderRadius:30,background:"#fff",boxShadow:"0 26px 70px rgba(20,36,94,.18)",overflow:"hidden",opacity:up}}>
    <Img src={staticFile("img/books.png")} style={{width:900,height:816,objectFit:"cover"}}/>
  </div>
  <div style={{position:"absolute",top:470,right:60,transform:`rotate(8deg) scale(${ease(t,s.start+0.8,s.start+1.1)})`,background:ORANGE,color:"#fff",fontFamily:ZH,fontWeight:900,fontSize:46,padding:"14px 30px",borderRadius:20,boxShadow:"0 10px 26px rgba(240,138,44,.4)"}}>附音频</div>
  <div style={{position:"absolute",top:1380,left:70,right:70,display:"flex",justifyContent:"space-between",alignItems:"center"}}>
    {chips.map((c,i)=>{const on=ease(t,s.start+1.6+i*0.45,s.start+1.9+i*0.45);return <React.Fragment key={c}>
      <div style={{opacity:.25+.75*on,background:i===0?ORANGE:BLUE,color:"#fff",borderRadius:18,padding:"12px 0",width:190,textAlign:"center",fontFamily:ZH}}>
        <div style={{fontSize:28,opacity:.85}}>第 {i+1} 册</div><div style={{fontSize:44,fontWeight:900}}>{c}</div>
      </div>
      {i<3&&<div style={{fontFamily:ZH,fontSize:40,color:MUTED,opacity:on}}>›</div>}
    </React.Fragment>;})}
  </div>
</AbsoluteFill>;};

/* 收尾：小黄车 + app icon */
const End:React.FC<{p:SceneProps;s:SceneT;t:number}>=({p,s,t})=>{const outroAt=p.audio.find(a=>a.file==="outro.mp3")!.at;const bob=Math.sin((t-s.start)*6)*14;const app=ease(t,outroAt-0.2,outroAt+0.3);return <AbsoluteFill style={{background:`radial-gradient(ellipse at 50% 40%, ${BLUE} 0%, ${NAVY} 72%)`}}>
  <Brand dark/>
  <div style={{position:"absolute",top:380,left:230,width:620,height:563,borderRadius:26,overflow:"hidden",background:"#fff",boxShadow:"0 26px 70px rgba(0,0,0,.35)"}}><Img src={staticFile("img/books.png")} style={{width:620,height:563,objectFit:"cover"}}/></div>
  <div style={{position:"absolute",top:1000,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:96,color:"#fff"}}>点左下角<span style={{color:"#ffd34d"}}>小黄车</span></div>
  <div style={{position:"absolute",top:1160,left:0,right:0,display:"flex",justifyContent:"center",alignItems:"center",gap:28,opacity:app,transform:`translateY(${(1-app)*30}px)`}}>
    <Img src={staticFile("app/alpha_icon.png")} style={{width:140,height:140,borderRadius:32,border:"3px solid #f2c46b"}}/>
    <div style={{fontFamily:ZH,color:"#fff"}}><div style={{fontSize:58,fontWeight:900}}>学泰文字母</div><div style={{fontSize:36,color:"#f2c46b"}}>44 个辅音 跟着练</div></div>
  </div>
  <svg style={{position:"absolute",left:120,top:1340+bob}} width="220" height="200" viewBox="0 0 220 200"><path d="M200 10 Q 120 40 50 150" stroke="#ffd34d" strokeWidth="14" fill="none" strokeLinecap="round"/><path d="M28 112 L 44 170 L 98 150" stroke="#ffd34d" strokeWidth="14" fill="none" strokeLinecap="round" strokeLinejoin="round"/></svg>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>p.scenes.find(x=>x.id===id)!;
  return <AbsoluteFill style={{background:PAPER}}>
    <style>{`@font-face{font-family:ThaiBold;src:url("${staticFile("fonts/Sarabun-Bold.ttf")}")}`}</style>
    <Audio src={staticFile(`audio/${p.bgm.file}`)} volume={p.bgm.volume}/>
    {p.audio.map((a,i)=><Sequence key={i} from={Math.round(a.at*fps)}><Audio src={staticFile(`audio/${a.file}`)}/></Sequence>)}
    <Layer s={S("cover")} t={t} first><Cover mid={p.mid}/></Layer>
    <Layer s={S("groups")} t={t}><Groups s={S("groups")} t={t}/></Layer>
    <Layer s={S("mid")} t={t}><MidGrid p={p} s={S("mid")} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book s={S("book")} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} s={S("end")} t={t}/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata:CalculateMetadataFunction<SceneProps>=async({props})=>({durationInFrames:props.totalFrames,fps:props.fps,width:1080,height:1920});
