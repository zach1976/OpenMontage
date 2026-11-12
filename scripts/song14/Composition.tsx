import React from 'react';
import {AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

// 第 14 首《กีดกัน (Skyline)》：副歌是四重阻隔的排比 —— 天空、高山、时间、命运。
// 这一集的视觉语言从这四重阻隔长出来：画面下方一条「阻隔栏」，唱到哪一重就亮哪一重；
// 词卡下方是一道横墙，讲到中文意思时墙从中间裂开（ฝ่าไป：闯过去）；
// 回听前的过渡把前三重划掉、只剩命运亮着 —— 天和山和时间都挡不住，只有命运让他认输。
type Chunk = {at: number; text: string; xie?: string};
type Line = {at: number; th: string; zh: string; group: number; chunks: Chunk[]};
type Clip = {file: string; dur: number};
type Block = {id: string; kind: 'song_open' | 'intro' | 'word' | 'replay_bridge' | 'song_replay' | 'outro'; startFrame: number; frames: number;
  index?: number; group?: number; th?: string; zh?: string; xie?: string; source?: Clip; still?: string; thaiAt?: number; zhAt?: number; nar?: Clip;
  segments?: {start: number; end: number; offset: number}[]};
export type LessonProps = {fps: number; totalFrames: number; totalSeconds: number; title: string; hookStart: number; lines: Line[]; blocks: Block[]; review_timeline: unknown[]};

const NIGHT = '#1A1430', PLUM = '#33204A', CORAL = '#F2785C', APRICOT = '#FFD9B8', CREAM = '#FFF4EA', MUTED = '#B9A6C2';
const ZH = 'PingFang SC, Noto Sans CJK SC, sans-serif';
const ZH_SERIF = 'Songti SC, STSong, serif';
const TH = 'Sarabun, Thonburi, sans-serif';
const GROUPS = [{zh: '天空', th: 'แผ่นฟ้า'}, {zh: '高山', th: 'ภูผา'}, {zh: '时间', th: 'เวลา'}, {zh: '命运', th: 'ชะตา'}];
const clamp = (v: number) => Math.max(0, Math.min(1, v));

const GroupIcon: React.FC<{g: number; size?: number; color: string}> = ({g, size = 46, color}) => {
  const s = {width: size, height: size};
  if (g === 0) return <svg {...s} viewBox="0 0 48 48" fill="none"><path d="M6 30c6-10 30-10 36 0" stroke={color} strokeWidth="3.4" strokeLinecap="round"/><path d="M12 38c4-6 20-6 24 0" stroke={color} strokeWidth="3.4" strokeLinecap="round" opacity=".6"/><circle cx="24" cy="14" r="5" fill={color}/></svg>;
  if (g === 1) return <svg {...s} viewBox="0 0 48 48" fill="none"><path d="M4 40L18 14l8 12 5-7 13 21z" stroke={color} strokeWidth="3.4" strokeLinejoin="round"/></svg>;
  if (g === 2) return <svg {...s} viewBox="0 0 48 48" fill="none"><circle cx="24" cy="24" r="17" stroke={color} strokeWidth="3.4"/><path d="M24 13v12l8 5" stroke={color} strokeWidth="3.4" strokeLinecap="round"/></svg>;
  return <svg {...s} viewBox="0 0 48 48" fill="none"><path d="M6 30c8-14 14 8 22-4s10-12 14-6" stroke={color} strokeWidth="3.4" strokeLinecap="round"/><circle cx="28" cy="26" r="4" fill={color}/></svg>;
};

// 远山剪影 —— Skyline：几层越远越淡
const Ridges: React.FC<{f: number}> = ({f}) => {
  const d = Math.sin(f / 90) * 6;
  return <svg width={1080} height={420} viewBox="0 0 1080 420" style={{position: 'absolute', left: 0, bottom: 0}}>
    <path d={`M0 210 L140 ${150 + d} L300 200 L470 120 L640 190 L820 ${110 - d} L1080 180 V420 H0Z`} fill="#4A2B57" opacity=".55"/>
    <path d={`M0 290 L180 220 L360 ${270 + d} L560 200 L760 260 L940 ${215 - d} L1080 250 V420 H0Z`} fill="#2A1B3C" opacity=".85"/>
    <path d="M0 360 L240 310 L520 350 L800 300 L1080 340 V420 H0Z" fill="#150F25"/>
  </svg>;
};

const Shell: React.FC<{children: React.ReactNode; label: string; f: number}> = ({children, label, f}) => <AbsoluteFill style={{background: `linear-gradient(180deg, ${PLUM} 0%, ${NIGHT} 46%, #120D22 100%)`, color: CREAM, overflow: 'hidden'}}>
  <div style={{position: 'absolute', left: -200, right: -200, top: 980, height: 520, background: `radial-gradient(ellipse at 50% 100%, rgba(242,120,92,.30), transparent 62%)`}}/>
  <Ridges f={f}/>
  <div style={{position: 'absolute', top: 150, left: 64, right: 64, display: 'flex', justifyContent: 'space-between', alignItems: 'baseline'}}>
    <span style={{fontFamily: ZH, fontSize: 31, fontWeight: 800, letterSpacing: 3, color: APRICOT}}>泰语千词 · 泰语神曲</span>
    <span style={{fontFamily: ZH, fontSize: 27, color: MUTED}}>{label}</span>
  </div>
  <div style={{position: 'absolute', left: 64, right: 64, bottom: 72, display: 'flex', justifyContent: 'space-between', fontFamily: ZH, fontSize: 22, letterSpacing: 1, color: MUTED}}>
    <span>Billkin · <span style={{fontFamily: TH}}>กีดกัน</span> (Skyline)</span><span>官方 MV · Nadao Music</span>
  </div>
  {children}
</AbsoluteFill>;

const MV: React.FC<{video?: string; still?: string}> = ({video, still}) => <div style={{position: 'absolute', left: 0, right: 0, top: 236, height: 608, overflow: 'hidden', background: '#0E0A18'}}>
  {still ? <Img src={staticFile(`images/${still}`)} style={{width: '100%', height: '100%', objectFit: 'cover'}}/>
    : <OffthreadVideo src={staticFile(`video/${video}`)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}}/>}
  <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 6, background: `linear-gradient(90deg, transparent, ${CORAL}, transparent)`}}/>
</div>;

// 阻隔栏：四重阻隔一字排开，当前那一重亮起；crossed=已经被「闯过去」的
const Rail: React.FC<{active: number; crossed?: number[]}> = ({active, crossed = []}) => <div style={{position: 'absolute', left: 52, right: 52, top: 880, display: 'flex', gap: 14}}>
  {GROUPS.map((g, i) => {
    const on = i === active, x = crossed.includes(i);
    return <div key={i} style={{flex: 1, height: 96, borderRadius: 18, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
      background: on ? CORAL : 'rgba(255,244,234,.06)', border: `2px solid ${on ? CORAL : 'rgba(255,217,184,.22)'}`, position: 'relative'}}>
      <GroupIcon g={i} size={38} color={on ? NIGHT : x ? '#7D6C88' : APRICOT}/>
      <span style={{fontFamily: ZH, fontSize: 33, fontWeight: 800, color: on ? NIGHT : x ? '#7D6C88' : CREAM}}>{g.zh}</span>
      {x && <div style={{position: 'absolute', left: 16, right: 16, top: 46, height: 4, background: APRICOT, transform: 'rotate(-8deg)', opacity: .8}}/>}
    </div>;
  })}
</div>;

const Song: React.FC<{block: Block; lines: Line[]; hookStart: number}> = ({block, lines, hookStart}) => {
  const f = useCurrentFrame(), {fps} = useVideoConfig(), t = f / fps;
  const replay = block.kind === 'song_replay';
  // 把块内时间换算回原曲绝对时间（回听是两段拼起来的）
  const segs = block.segments!;
  let abs = segs[0].start + t;
  for (const s of segs) if (t >= s.offset) abs = s.start + (t - s.offset);
  const li = Math.max(0, lines.reduce((acc, l, k) => abs >= l.at - 0.25 ? k : acc, 0));
  const line = lines[li];
  const ci = Math.max(0, line.chunks.reduce((acc, c, k) => abs >= c.at ? k : acc, 0));
  const cover = replay ? 0 : interpolate(f, [0, 36, 54], [1, 1, 0], {extrapolateRight: 'clamp'});
  const big = line.th.length > 26;
  return <Shell label={replay ? '再听一遍 · 听懂了吗' : '先听原唱副歌'} f={f}>
    <MV video={replay ? 'mv_replay.mp4' : 'mv_hook.mp4'}/>
    <Rail active={line.group}/>
    <div style={{position: 'absolute', left: 60, right: 60, top: 1040, minHeight: 380, opacity: 1 - cover}}>
      <div style={{display: 'flex', flexWrap: 'wrap', alignItems: 'flex-start', columnGap: 18, rowGap: 6}}>
        {line.chunks.map((c, k) => <div key={k} style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
          <span style={{fontFamily: TH, fontWeight: 700, fontSize: big ? 62 : 72, lineHeight: 1.4, textShadow: '0 8px 30px rgba(0,0,0,.35)', color: k === ci ? CORAL : k < ci ? CREAM : 'rgba(255,244,234,.55)'}}>{c.text.trim()}</span>
          {c.xie ? <span style={{fontFamily: ZH, fontWeight: 700, fontSize: 32, letterSpacing: 2, color: k === ci ? APRICOT : 'rgba(255,217,184,.55)', marginTop: -4}}>{c.xie}</span> : null}
        </div>)}
      </div>
      <div style={{fontFamily: ZH, fontWeight: 700, fontSize: 46, lineHeight: 1.45, color: APRICOT, marginTop: 26}}>{line.zh}</div>
    </div>
    <div style={{position: 'absolute', left: 64, right: 64, top: 1500, height: 4, background: 'rgba(255,244,234,.16)'}}>
      <div style={{width: `${clamp(f / block.frames) * 100}%`, height: '100%', background: CORAL}}/>
    </div>
    {segs.map((s, k) => <Sequence key={k} from={Math.round(s.offset * fps)}>
      <Audio src={staticFile('audio/original.mp3')} trimBefore={Math.round(s.start * fps)} trimAfter={Math.round(s.end * fps)} volume={.8}/>
    </Sequence>)}
    {cover > 0 && <div style={{position: 'absolute', left: 0, right: 0, top: 640, height: 640, opacity: cover, background: 'rgb(24,16,40)', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', borderTop: `4px solid ${CORAL}`, borderBottom: `4px solid ${CORAL}`}}>
      <div style={{fontFamily: ZH_SERIF, fontWeight: 900, fontSize: 150, lineHeight: 1.18, color: CREAM, letterSpacing: 4}}>泰国神曲</div>
      <div style={{fontFamily: ZH_SERIF, fontWeight: 900, fontSize: 150, lineHeight: 1.18, color: CORAL, letterSpacing: 4}}>《阻挡》</div>
      <div style={{fontFamily: TH, fontWeight: 700, fontSize: 54, color: APRICOT, marginTop: 26}}>กีดกั้นด้วยแผ่นฟ้า</div>
    </div>}
  </Shell>;
};

const Intro: React.FC<{block: Block}> = ({block}) => {
  const f = useCurrentFrame();
  const y = interpolate(f, [0, 20], [26, 0], {extrapolateRight: 'clamp'});
  return <Shell label="这首歌讲什么" f={f}>
    <MV still={block.still}/>
    <div style={{position: 'absolute', left: 64, right: 64, top: 900, fontFamily: ZH, fontSize: 32, color: APRICOT, letterSpacing: 2}}>Billkin ·《以你的心诠释我的爱》插曲</div>
    <div style={{position: 'absolute', left: 64, right: 64, top: 1000, transform: `translateY(${y}px)`, fontFamily: ZH_SERIF, fontSize: 78, fontWeight: 900, lineHeight: 1.4}}>
      四句副歌，<br/>每句都是<span style={{color: CORAL}}>被什么挡住</span>
    </div>
    <div style={{position: 'absolute', left: 64, right: 64, top: 1290, display: 'flex', gap: 22}}>
      {GROUPS.map((g, i) => <div key={i} style={{display: 'flex', alignItems: 'center', gap: 8, opacity: interpolate(f, [10 + i * 8, 22 + i * 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
        <GroupIcon g={i} size={40} color={APRICOT}/><span style={{fontFamily: ZH, fontSize: 36, fontWeight: 800}}>{g.zh}</span>
      </div>)}
    </div>
    <Audio src={staticFile(`audio/${block.nar!.file}`)}/>
  </Shell>;
};

const Word: React.FC<{block: Block}> = ({block}) => {
  const f = useCurrentFrame(), {fps} = useVideoConfig(), t = f / fps;
  const phase = t < block.thaiAt! ? 0 : t < block.zhAt! ? 1 : 2;
  const open = interpolate(t, [block.zhAt!, block.zhAt! + .35], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const enter = interpolate(f, [0, 12], [.9, 1], {extrapolateRight: 'clamp'});
  const g = block.group!;
  return <Shell label={`第${'一二三四'[g]}重阻隔 · ${GROUPS[g].zh}`} f={f}>
    <MV still={block.still}/>
    <Rail active={g} crossed={[0, 1, 2, 3].filter((i) => i < g)}/>
    <div style={{position: 'absolute', left: 60, right: 60, top: 1010, textAlign: 'center', transform: `scale(${enter})`, fontFamily: TH, fontWeight: 700, fontSize: block.th!.length > 10 ? 104 : 124, lineHeight: 1.4, color: CREAM}}>{block.th}</div>
    <div style={{position: 'absolute', left: 60, right: 60, top: 1196, textAlign: 'center', fontFamily: ZH, fontSize: 40, fontWeight: 700, letterSpacing: 4, color: APRICOT}}>谐音 · {block.xie}</div>
    {/* 横墙：讲到中文意思时从中间裂开 */}
    <div style={{position: 'absolute', top: 1286, left: 64, width: 476 - open * 150, height: 14, borderRadius: 7, background: APRICOT, opacity: .85}}/>
    <div style={{position: 'absolute', top: 1286, right: 64, width: 476 - open * 150, height: 14, borderRadius: 7, background: APRICOT, opacity: .85}}/>
    <div style={{position: 'absolute', left: 60, right: 60, top: 1336, textAlign: 'center', fontFamily: ZH, fontSize: 84, fontWeight: 850, color: CORAL, opacity: phase === 2 ? 1 : .0, transform: `translateY(${(1 - open) * 18}px)`}}>{block.zh}</div>
    <div style={{position: 'absolute', left: 200, right: 200, top: 1520, display: 'flex', justifyContent: 'space-between'}}>
      {['原唱', '跟读', '意思'].map((x, i) => <div key={x} style={{display: 'flex', alignItems: 'center', gap: 10, fontFamily: ZH, fontSize: 30, fontWeight: 700, color: phase === i ? CORAL : MUTED}}>
        <div style={{width: 16, height: 16, borderRadius: 8, background: phase === i ? CORAL : 'transparent', border: `2px solid ${phase === i ? CORAL : MUTED}`}}/>{x}
      </div>)}
    </div>
    <Audio src={staticFile(`audio/${block.source!.file}`)} volume={.8}/>
    <Sequence from={Math.round(block.thaiAt! * fps)}><Audio src={staticFile(`audio/${block.id}_th.mp3`)}/></Sequence>
    <Sequence from={Math.round(block.zhAt! * fps)}><Audio src={staticFile(`audio/${block.id}_zh.mp3`)}/></Sequence>
  </Shell>;
};

const ReplayBridge: React.FC<{block: Block}> = ({block}) => {
  const f = useCurrentFrame();
  return <Shell label="再听之前" f={f}>
    <div style={{position: 'absolute', left: 90, right: 90, top: 380}}>
      {GROUPS.map((g, i) => {
        const fate = i === 3;
        const strike = interpolate(f, [8 + i * 10, 20 + i * 10], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        return <div key={i} style={{position: 'relative', height: 200, display: 'flex', alignItems: 'center', gap: 28, borderBottom: '1px solid rgba(255,217,184,.18)'}}>
          <GroupIcon g={i} size={70} color={fate ? CORAL : '#8C7A96'}/>
          <span style={{fontFamily: ZH_SERIF, fontWeight: 900, fontSize: 84, color: fate ? CORAL : '#8C7A96'}}>{g.zh}</span>
          <span style={{fontFamily: TH, fontWeight: 700, fontSize: 52, color: fate ? APRICOT : '#6E5F79'}}>{g.th}</span>
          <span style={{marginLeft: 'auto', fontFamily: ZH, fontSize: 36, fontWeight: 800, color: fate ? CORAL : '#8C7A96'}}>{fate ? '挡住了' : '挡不住'}</span>
          {!fate && <div style={{position: 'absolute', left: 0, top: 98, height: 5, width: `${strike * 62}%`, background: APRICOT, opacity: .7}}/>}
        </div>;
      })}
    </div>
    <div style={{position: 'absolute', left: 90, right: 90, top: 1260, fontFamily: ZH, fontSize: 44, fontWeight: 800, color: CREAM}}>最后一句：<span style={{fontFamily: TH, color: CORAL}}>ใช่ไหม</span> 是吗？</div>
    <Audio src={staticFile(`audio/${block.nar!.file}`)}/>
  </Shell>;
};

const Outro: React.FC<{block: Block}> = ({block}) => {
  const f = useCurrentFrame();
  const r = interpolate(f, [0, 12], [0, 1], {extrapolateRight: 'clamp'});
  return <Shell label="学泰语 · 泰语千词" f={f}>
    <div style={{position: 'absolute', left: 350, top: 470, width: 380, height: 380, borderRadius: 84, overflow: 'hidden', boxShadow: '0 28px 72px rgba(0,0,0,.4)', border: `3px solid ${APRICOT}`, opacity: r, transform: `scale(${.92 + .08 * r})`}}>
      <Img src={staticFile('app/app_icon.png')} style={{width: '100%', height: '100%'}}/>
    </div>
    <div style={{position: 'absolute', left: 60, right: 60, top: 930, textAlign: 'center', fontFamily: ZH, fontSize: 96, fontWeight: 850, opacity: r}}>泰语千词</div>
    <div style={{position: 'absolute', left: 300, right: 300, top: 1090, height: 3, background: CORAL, opacity: r}}/>
    <div style={{position: 'absolute', left: 60, right: 60, top: 1150, textAlign: 'center', fontFamily: ZH, fontSize: 58, fontWeight: 800, color: APRICOT, opacity: r}}>在泰国生活，够用了</div>
    <Audio src={staticFile(`audio/${block.nar!.file}`)}/>
  </Shell>;
};

export const KheedkanLesson: React.FC<LessonProps> = (props) => <AbsoluteFill style={{background: NIGHT}}>
  <style>{`@font-face{font-family:Sarabun;src:url("${staticFile('fonts/Sarabun-Bold.ttf')}");font-weight:700;}`}</style>
  {props.blocks.map((b) => <Sequence key={b.id} from={b.startFrame} durationInFrames={b.frames}>
    {b.kind === 'song_open' || b.kind === 'song_replay' ? <Song block={b} lines={props.lines} hookStart={props.hookStart}/>
      : b.kind === 'intro' ? <Intro block={b}/> : b.kind === 'word' ? <Word block={b}/>
        : b.kind === 'replay_bridge' ? <ReplayBridge block={b}/> : <Outro block={b}/>}
  </Sequence>)}
</AbsoluteFill>;
