import React from "react";
import {AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame, useVideoConfig, interpolate, CalculateMetadataFunction} from "remotion";

type Clip={file:string;dur:number};
type Card={id:string;zh:string;thai:string;hint:string;tag:string;intro:Clip;pronounce:Clip;explain:Clip;thaiAt:number;repeatAt:number;explainAt:number;dur:number;startFrame:number;frames:number};
type Lesson={title:string;word:string;meaning:string;tone:string;color:string;tagline:string;number:string};
export type SceneProps={fps:number;totalFrames:number;totalSeconds:number;lesson:Lesson;hook:{dur:number;startFrame:number;frames:number;nar:Clip;thai:Clip;thaiAt:number};cards:Card[];reveal:{dur:number;startFrame:number;frames:number;nar:Clip;rule:string};outro:{dur:number;startFrame:number;frames:number;nar:Clip};bgm:{file:string;volume:number};review_timeline:unknown[]};

const PAPER="#f8f5ea",INK="#1c3430",GOLD="#edb85c",MUTED="#706d65";
const ZH="PingFang SC, Noto Sans CJK SC, sans-serif",TH="ThaiBold, Thonburi, sans-serif";
const fade=(f:number)=>interpolate(f,[0,8],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"});
const thaiSize=(s:string)=>s.length>18?78:s.length>14?92:s.length>10?110:148;

const Page:React.FC<{index:string;lesson:Lesson;children:React.ReactNode}>=({index,lesson,children})=><AbsoluteFill style={{background:PAPER,color:INK,overflow:"hidden"}}>
  <div style={{position:"absolute",inset:0,backgroundImage:"linear-gradient(rgba(28,52,48,.045) 1px, transparent 1px),linear-gradient(90deg,rgba(28,52,48,.045) 1px,transparent 1px)",backgroundSize:"42px 42px",opacity:.3}}/>
  <div style={{position:"absolute",top:0,left:0,right:0,height:24,background:lesson.color}}/>
  <div style={{position:"absolute",top:86,left:78,right:78,display:"flex",justifyContent:"space-between",fontFamily:ZH,fontSize:27,letterSpacing:2,color:lesson.color,fontWeight:700}}><span>泰语千词 · 趣味泰语</span><span>{index} / 06</span></div>
  <div style={{position:"absolute",top:142,left:78,right:78,height:2,background:lesson.color,opacity:.3}}/>
  <div style={{position:"absolute",bottom:95,left:78,right:78,height:2,background:lesson.color,opacity:.24}}/>
  <div style={{position:"absolute",bottom:53,left:78,right:78,display:"flex",justifyContent:"space-between",fontFamily:ZH,fontSize:20,letterSpacing:1,color:MUTED}}><span>泰语口语 · 第 {lesson.number} 期</span><span>THAI 1000 WORDS</span></div>
  {children}
</AbsoluteFill>;

const Hook:React.FC<{lesson:Lesson;hook:SceneProps["hook"]}>=({lesson,hook})=>{const f=useCurrentFrame(),{fps}=useVideoConfig();return <Page lesson={lesson} index="01">
  <div style={{position:"absolute",top:260,left:76,right:76,fontFamily:ZH,fontSize:43,fontWeight:800,color:lesson.color}}>今天学一句泰语口语</div>
  <div style={{position:"absolute",top:390,left:72,right:72,fontFamily:ZH,fontSize:77,fontWeight:900,lineHeight:1.2,opacity:fade(f)}}>{lesson.meaning}<span style={{color:lesson.color}}>，怎么说？</span></div>
  <div style={{position:"absolute",top:655,left:72,right:72,height:415,borderRadius:28,background:INK,boxShadow:"0 26px 70px rgba(28,52,48,.18)",display:"flex",alignItems:"center",justifyContent:"center"}}><div style={{fontFamily:TH,fontSize:thaiSize(lesson.word),color:PAPER,textAlign:"center",lineHeight:1.3,padding:"0 22px",transform:`scale(${interpolate(f,[0,12],[.94,1],{extrapolateRight:"clamp"})})`}}>{lesson.word}</div></div>
  <div style={{position:"absolute",top:1170,left:78,right:78,fontFamily:ZH,fontSize:64,fontWeight:850,color:lesson.color}}>{lesson.meaning}</div>
  <div style={{position:"absolute",top:1315,left:78,right:78,fontFamily:ZH,fontSize:43}}>语气：<span style={{fontWeight:800}}>{lesson.tone}</span></div>
  <div style={{position:"absolute",top:1530,left:78,right:78,fontFamily:ZH,fontSize:34,color:MUTED}}>{lesson.tagline}</div>
  <Audio src={staticFile(`audio/${hook.nar.file}`)} volume={.98}/>
  <Sequence from={Math.round(hook.thaiAt*fps)}><Audio src={staticFile(`audio/${hook.thai.file}`)} volume={1}/></Sequence>
</Page>};

const LessonCard:React.FC<{lesson:Lesson;card:Card;index:number}>=({lesson,card,index})=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps,speaking=t>=card.thaiAt&&t<card.explainAt;return <Page lesson={lesson} index={`0${index+2}`}>
  <div style={{position:"absolute",top:235,left:76,right:76,fontFamily:ZH,fontSize:38,color:lesson.color,fontWeight:800}}>第 {index+1} 句 · {card.tag}</div>
  <div style={{position:"absolute",top:360,left:76,right:76,fontFamily:ZH,fontSize:83,fontWeight:900,lineHeight:1.25,opacity:fade(f)}}>{card.zh}</div>
  <div style={{position:"absolute",top:585,left:76,right:76,height:475,borderRadius:28,background:INK,boxShadow:"0 28px 70px rgba(28,52,48,.18)",display:"flex",alignItems:"center",justifyContent:"center"}}><div style={{fontFamily:TH,fontSize:thaiSize(card.thai),color:speaking?GOLD:PAPER,textAlign:"center",lineHeight:1.35,padding:"0 18px",transform:`scale(${speaking?1.035:1})`}}>{card.thai}</div></div>
  <div style={{position:"absolute",top:1160,left:76,right:76,fontFamily:ZH,fontSize:58,fontWeight:850,color:lesson.color}}>{card.zh}</div>
  <div style={{position:"absolute",top:1300,left:76,right:76,fontFamily:ZH,fontSize:40,lineHeight:1.5,color:MUTED}}>{card.hint}</div>
  <div style={{position:"absolute",top:1580,left:76,right:76,display:"flex",gap:16}}>{[0,1,2].map(i=><div key={i} style={{height:12,flex:1,borderRadius:20,background:i===index?lesson.color:"rgba(28,52,48,.12)"}}/>)}</div>
  <div style={{position:"absolute",top:1640,left:76,right:76,fontFamily:ZH,fontSize:28,color:lesson.color}}>先听中文，再跟读泰语两遍</div>
  <Audio src={staticFile(`audio/${card.intro.file}`)} volume={.98}/>
  <Sequence from={Math.round(card.thaiAt*fps)}><Audio src={staticFile(`audio/${card.pronounce.file}`)} volume={1}/></Sequence>
  <Sequence from={Math.round(card.repeatAt*fps)}><Audio src={staticFile(`audio/${card.pronounce.file}`)} volume={1}/></Sequence>
  <Sequence from={Math.round(card.explainAt*fps)}><Audio src={staticFile(`audio/${card.explain.file}`)} volume={.98}/></Sequence>
</Page>};

const Reveal:React.FC<{lesson:Lesson;reveal:SceneProps["reveal"];cards:Card[]}>=({lesson,reveal,cards})=><Page lesson={lesson} index="05">
  <div style={{position:"absolute",top:260,left:76,right:76,fontFamily:ZH,fontSize:43,color:lesson.color,fontWeight:800}}>语气小结</div>
  <div style={{position:"absolute",top:400,left:76,right:76,fontFamily:ZH,fontSize:82,fontWeight:900}}>听懂，也要会选</div>
  <div style={{position:"absolute",top:665,left:76,right:76,padding:"48px 45px",borderRadius:26,background:INK,color:PAPER}}><div style={{fontFamily:TH,fontSize:thaiSize(cards[1].thai),lineHeight:1.25}}>{cards[1].thai}</div><div style={{fontFamily:ZH,fontSize:41,marginTop:20,color:GOLD}}>{cards[1].zh} · 语气冲</div></div>
  <div style={{position:"absolute",top:1025,left:76,right:76,padding:"48px 45px",border:`3px solid ${lesson.color}`,borderRadius:26,background:"rgba(255,255,255,.6)"}}><div style={{fontFamily:TH,fontSize:thaiSize(cards[2].thai),lineHeight:1.25}}>{cards[2].thai}</div><div style={{fontFamily:ZH,fontSize:41,marginTop:20,color:lesson.color}}>{cards[2].zh} · 更平和</div></div>
  <div style={{position:"absolute",top:1480,left:76,right:76,fontFamily:ZH,fontSize:37,fontWeight:800,lineHeight:1.5,color:lesson.color}}>{reveal.rule}</div>
  <Audio src={staticFile(`audio/${reveal.nar.file}`)} volume={.98}/>
</Page>;

const Outro:React.FC<{lesson:Lesson;outro:SceneProps["outro"]}>=({lesson,outro})=><Page lesson={lesson} index="06">
  <div style={{position:"absolute",top:350,left:75,right:75,fontFamily:ZH,fontSize:46,color:lesson.color,textAlign:"center"}}>继续学实用泰语</div>
  <Img src={staticFile("app/app_icon.png")} style={{position:"absolute",top:540,left:390,width:300,height:300,borderRadius:55,boxShadow:"0 24px 55px rgba(28,52,48,.24)"}}/>
  <div style={{position:"absolute",top:930,left:75,right:75,fontFamily:ZH,fontSize:99,fontWeight:900,textAlign:"center"}}>泰语千词</div>
  <div style={{position:"absolute",top:1190,left:75,right:75,fontFamily:ZH,fontSize:58,fontWeight:800,color:lesson.color,textAlign:"center"}}>在泰国生活，够用了</div>
  <Audio src={staticFile(`audio/${outro.nar.file}`)} volume={.98}/>
</Page>;

export const Scene:React.FC<SceneProps>=({lesson,hook,cards,reveal,outro,bgm})=><AbsoluteFill style={{background:PAPER}}>
  <style>{`@font-face{font-family:ThaiBold;src:url("${staticFile("fonts/Sarabun-Bold.ttf")}")}`}</style>
  <Audio src={staticFile(`audio/${bgm.file}`)} volume={bgm.volume}/>
  <Sequence from={hook.startFrame} durationInFrames={hook.frames}><Hook lesson={lesson} hook={hook}/></Sequence>
  {cards.map((card,index)=><Sequence key={card.id} from={card.startFrame} durationInFrames={card.frames}><LessonCard lesson={lesson} card={card} index={index}/></Sequence>)}
  <Sequence from={reveal.startFrame} durationInFrames={reveal.frames}><Reveal lesson={lesson} reveal={reveal} cards={cards}/></Sequence>
  <Sequence from={outro.startFrame} durationInFrames={outro.frames}><Outro lesson={lesson} outro={outro}/></Sequence>
</AbsoluteFill>;
export const calculateMetadata:CalculateMetadataFunction<SceneProps>=async({props})=>({durationInFrames:props.totalFrames,fps:props.fps,width:1080,height:1920});
