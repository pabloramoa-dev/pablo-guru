import React from 'react';
import {AbsoluteFill,Audio,Composition,Img,Sequence,registerRoot,staticFile,useCurrentFrame} from 'remotion';
import {easeInOutCubic,easeOutCubic} from '@motion-canvas/core/lib/tweening';
import timeline from './public/timeline.json';
import meta from './public/actors/metadata.json';
const gold='#edc97e',ink='#101d22',white='#f6f1e8';
const clamp=v=>Math.max(0,Math.min(1,v));
const font='DejaVu Sans, sans-serif';
const layer={position:'absolute',inset:0,width:'100%',height:'100%'};
function Actor({name,t,cues=[],speaking=false,width=1000,left=850,top=110}){
 const cue=cues.find(c=>t>=c.start&&t<c.end)?.value||'X';
 const blink=(t+(name==='marina'?1.2:0))%4.1>3.94?1:0;
 const breath=Math.sin(t*1.7)*3;
 const gesture=speaking?(Math.sin(t*1.1)*.5+.5)*13:2*Math.sin(t*.7);
 return <div style={{position:'absolute',left,top:top+breath,width,height:width*900/780,filter:'drop-shadow(0px 15px 12px #0005)',transform:`rotate(${Math.sin(t*.7)*.35}deg)`}}>
  <Img src={staticFile(`actors/${name}_body.png`)} style={layer}/>
  {['left','right'].map((side,i)=><Img key={side} src={staticFile(`actors/${name}_${side}.png`)} style={{...layer,transformOrigin:`${meta[name][side][0]/780*100}% ${meta[name][side][1]/900*100}%`,transform:`rotate(${(i?1:-1)*gesture}deg)`}}/>)}
  <Img src={staticFile(`actors/${name}_${cue}_${blink}.png`)} style={{...layer,transformOrigin:'50% 40%',transform:`rotate(${Math.sin(t*.9)*.65}deg)`}}/>
 </div>
}
function Symbol({mode,t}){
 const p=easeInOutCubic(clamp(t/5));
 return <svg width="760" height="180" viewBox="0 0 760 180" style={{position:'absolute',left:140,top:530}}>
  {['bridge','step','resolve','end'].includes(mode)?<>
   <path d="M20 138 Q380 40 740 138" fill="none" stroke="#ffffff35" strokeWidth="3"/>
   {Array.from({length:9},(_,i)=><g key={i} opacity={.15+.85*clamp(p*10-i)} transform={`translate(${60+i*77},${116-Math.sin(i/8*Math.PI)*50}) rotate(${(i-4)*3})`}><rect width="55" height="16" rx="5" fill={gold}/><circle cx="27" cy="-25" r="4" fill={gold}/></g>)}
  </>:mode==='wait'?<>
   <circle cx="95" cy="87" r="62" stroke={gold} strokeWidth="3" fill="none"/>
   <line x1="95" y1="87" x2="95" y2="39" stroke={gold} strokeWidth="4" transform={`rotate(${t*35} 95 87)`}/>
   <text x="197" y="99" fill={white} fontSize="27" fontFamily={font} letterSpacing="5">AMANHÃ. DEPOIS. UM DIA.</text>
  </>:<>
   <line x1="10" y1="65" x2={10+p*660} y2="65" stroke={gold} strokeWidth="3"/>
   <circle cx={10+p*660} cy="65" r="8" fill={gold}/>
   <text x="10" y="123" fill={gold} fontSize="24" fontFamily={font} letterSpacing="6">{mode==='hook'?'UMA HISTÓRIA SOBRE COMEÇAR':mode==='question'?'O MEDO PEDE CERTEZA.':mode==='reveal'?'PERCEBER É O PRIMEIRO PASSO.':'CADA HISTÓRIA ABRE UM CAMINHO.'}</text>
  </>}
 </svg>
}
function Scene({scene,index}){
 const frame=useCurrentFrame(),t=frame/30;
 const enter=easeOutCubic(clamp(frame/24));
 const slow=easeInOutCubic(clamp(frame/scene.frames));
 const words=scene.words||[];
 const idx=words.findIndex(w=>t>=w.start&&t<w.end);
 const group=idx<0?[]:words.slice(Math.floor(idx/7)*7,Math.floor(idx/7)*7+7);
 return <AbsoluteFill style={{background:ink,color:white,fontFamily:font,overflow:'hidden'}}>
  <Img src={staticFile(`background_${index%3}.png`)} style={{...layer,objectFit:'cover',transform:`scale(${1.04+slow*.035}) translateX(${-slow*16}px)`}}/>
  <AbsoluteFill style={{background:'linear-gradient(90deg,rgba(10,25,29,.96) 0%,rgba(10,25,29,.83) 42%,rgba(10,25,29,.24) 100%)'}}/>
  <AbsoluteFill style={{background:'linear-gradient(0deg,#08191eee 0%,transparent 30%,transparent 80%,#0b1d2280 100%)'}}/>
  <div style={{position:'absolute',left:140,top:75,fontSize:24,letterSpacing:7,color:gold}}>PABLO GURU <span style={{color:'#b8c6c4',letterSpacing:4,fontSize:18}}> / HISTÓRIAS PARA PENSAR</span></div>
  <div style={{position:'absolute',left:140,top:194,color:gold,fontSize:18,letterSpacing:5}}>{String(index+1).padStart(2,'0')} — A PRIMEIRA TÁBUA</div>
  <div style={{position:'absolute',left:140,top:265,width:850,fontSize:77,fontWeight:700,lineHeight:1.14,whiteSpace:'pre-line',letterSpacing:-3,opacity:enter,transform:`translateY(${(1-enter)*25}px)`}}>{scene.title}</div>
  <Symbol mode={scene.mode} t={t}/>
  <Actor name={scene.actor} t={t} cues={scene.cues} speaking={t<scene.seconds}/>
  <Actor name={scene.actor==='pablo'?'marina':'pablo'} t={t} width={410} left={105} top={655}/>
  <div style={{position:'absolute',left:440,top:807,fontSize:19,letterSpacing:3,color:'#d8dfda'}}>ÀS VEZES, UMA HISTÓRIA<br/><span style={{color:gold,lineHeight:2}}>MUDA O PRÓXIMO PASSO.</span></div>
  {group.length>0&&<div style={{position:'absolute',bottom:62,left:460,right:120,display:'flex',gap:10,justifyContent:'center',flexWrap:'wrap',fontSize:31,fontWeight:500,textShadow:'0 2px 8px #000'}}>{group.map((w,i)=><span key={i} style={{color:t>=w.start&&t<w.end?gold:white}}>{w.text}</span>)}</div>}
  <div style={{position:'absolute',bottom:0,left:0,width:`${100*(scene.from+frame)/timeline.frames}%`,height:5,background:gold}}/>
 </AbsoluteFill>
}
function Episode(){return <AbsoluteFill><Audio src={staticFile('soundtrack.wav')}/>{timeline.scenes.map((s,i)=><Sequence key={i} from={s.from} durationInFrames={s.frames}><Scene scene={s} index={i}/></Sequence>)}</AbsoluteFill>}
const audition=[];let pos=0;for(const s of timeline.samples){let frames=Math.ceil((s.duration+1)*30);audition.push({...s,from:pos,frames});pos+=frames;}
function VoiceCard({s,i}){const t=useCurrentFrame()/30;return <AbsoluteFill style={{background:ink,color:white,fontFamily:font}}>
 <Img src={staticFile('background_0.png')} style={{...layer,opacity:.22}}/>
 <div style={{position:'absolute',left:140,top:100,fontSize:24,color:gold,letterSpacing:6}}>PABLO GURU / TESTE DE VOZ {i+1}</div>
 <div style={{position:'absolute',left:140,top:280,fontSize:65,fontWeight:700,width:1500}}>{s.voice.replace('edge:','Edge • ').replace('piper:','Piper • ')}</div>
 <div style={{position:'absolute',left:140,top:440,fontSize:38,lineHeight:1.6,width:1540}}>O medo de errar te paralisa? Escute isso.<br/>Uma ponte não aparece pronta. Ela começa com a primeira tábua,<br/>colocada por alguém que decidiu tentar.</div>
 <div style={{position:'absolute',left:140,top:810,fontSize:22,color:gold,letterSpacing:4}}>MESMO TEXTO • VOLUME NORMALIZADO • SEM TRILHA</div>
 <div style={{position:'absolute',left:140,top:900,width:1500*clamp(t/s.duration),height:4,background:gold}}/>
 <Audio src={staticFile(s.file)}/>
 </AbsoluteFill>}
function Audition(){return <AbsoluteFill>{audition.map((s,i)=><Sequence key={i} from={s.from} durationInFrames={s.frames}><VoiceCard s={s} i={i}/></Sequence>)}</AbsoluteFill>}
registerRoot(()=> <><Composition id="PabloLab" component={Episode} durationInFrames={timeline.frames} fps={30} width={1920} height={1080}/><Composition id="VoiceAudition" component={Audition} durationInFrames={pos} fps={30} width={1920} height={1080}/></>);
