import React from 'react';
import {AbsoluteFill,Audio,Composition,registerRoot,staticFile,useCurrentFrame} from 'remotion';
import {easeInOutCubic,easeOutBack} from '@motion-canvas/core/lib/tweening';
import scenes from './public/timeline.json';
const clamp=v=>Math.max(0,Math.min(1,v));const lerp=(a,b,p)=>a+(b-a)*p;
function Character({rabbit=false,t,talk,cue,x,y,excited=false}){
 const color=rabbit?'#e2aff5':'#67cec1',outline=rabbit?'#885da4':'#287f7c';
 const blink=((t+(rabbit?1:0))%4.3)>4.12;
 const bounce=excited?Math.abs(Math.sin(t*5))*17:Math.sin(t*2)*3;
 const arm=talk?Math.sin(t*3)*14:Math.sin(t)*4;
 const mouth={X:0,A:4,B:9,C:17,D:25,E:20,F:13,G:8,H:17}[cue]||0;
 return <g transform={`translate(${x},${y-bounce})`} stroke={outline} strokeWidth="6" strokeLinejoin="round" strokeLinecap="round">
  <ellipse cx="190" cy="545" rx="138" ry="24" fill="#42774c" opacity=".13" stroke="none"/>
  {!rabbit&&<path d="M80 455 Q-34 463 22 349 Q42 417 103 401" fill={color}/>}
  <g transform={`rotate(${Math.sin(t*2)*2} 190 360)`}>
  <ellipse cx="136" cy="509" rx="47" ry="27" fill={color}/><ellipse cx="244" cy="509" rx="47" ry="27" fill={color}/>
  <ellipse cx="190" cy="383" rx="110" ry="128" fill={color}/>
  <ellipse cx="190" cy="404" rx="70" ry="81" fill={rabbit?'#fff4d9':'#c2f0d0'} stroke="none"/>
  {rabbit&&<><path d="M113 365 L128 469 Q190 504 254 469 L267 365" fill="#54b9c2"/><path d="M135 305 L150 380 M245 305 L230 380" stroke="#54b9c2" strokeWidth="24"/><rect x="166" y="401" width="50" height="39" rx="10" fill="#b4eaeb" stroke="none"/></>}
  <g transform={`rotate(${-arm} 100 341)`}><ellipse cx="88" cy="385" rx="29" ry="66" fill={color}/></g>
  <g transform={`rotate(${arm+((t>7&&t<14)?-35:0)} 279 341)`}><ellipse cx="288" cy="385" rx="29" ry="66" fill={color}/></g>
  <g transform={`rotate(${Math.sin(t*1.8)*(talk?2:1)} 190 252)`}>
  {rabbit?<><ellipse cx="137" cy="108" rx="42" ry="109" fill={color} transform="rotate(-12 137 108)"/><ellipse cx="244" cy="103" rx="42" ry="107" fill={color} transform="rotate(12 244 103)"/><ellipse cx="137" cy="99" rx="22" ry="68" fill="#f9d0e8" stroke="none"/><ellipse cx="244" cy="96" rx="22" ry="68" fill="#f9d0e8" stroke="none"/></>:<><path d="M84 158 L55 111 L117 129 L135 79 L170 122 L209 86 L222 137" fill="#f6cb63"/><ellipse cx="91" cy="200" rx="30" ry="38" fill={color}/></>}
  <ellipse cx="190" cy="222" rx="133" ry="118" fill={color}/>
  {!rabbit&&<ellipse cx="212" cy="257" rx="115" ry="63" fill="#a6e7c7" stroke="none"/>}
  {[145,241].map((ex,i)=><g key={i}>{blink?<path d={`M${ex-16} 206 Q${ex} 218 ${ex+16} 206`} fill="none"/>:<><ellipse cx={ex} cy="204" rx="29" ry="36" fill="white" stroke="none"/><ellipse cx={ex+(rabbit?-3:3)} cy="209" rx="15" ry="23" fill="#263e53" stroke="none"/><circle cx={ex+5} cy="198" r="6" fill="white" stroke="none"/></>}</g>)}
  <ellipse cx="109" cy="256" rx="22" ry="12" fill="#ef9daa" opacity=".8" stroke="none"/><ellipse cx="278" cy="256" rx="22" ry="12" fill="#ef9daa" opacity=".8" stroke="none"/>
  {rabbit&&<path d="M177 237 Q190 229 203 237 L190 249 Z" fill="#b8759c" stroke="none"/>}
  {mouth>0?<ellipse cx="194" cy="275" rx={cue==='F'?12:25} ry={mouth} fill="#63344d" strokeWidth="3"/>:<path d="M172 272 Q194 291 216 270" fill="none" strokeWidth="5"/>}
  {!rabbit&&<><circle cx="264" cy="238" r="4" fill={outline} stroke="none"/><circle cx="287" cy="238" r="4" fill={outline} stroke="none"/></>}
  {rabbit?<path d="M271 128 Q329 91 325 153 Q292 141 271 128 Q287 98 258 94 Q242 108 271 128" fill="#ffcf60"/>:<path d="M107 316 Q190 350 278 313 L267 342 Q190 364 113 342 M222 345 L253 390 L273 352" fill="#f5ac55"/>}
  </g></g></g>
}
function App(){
 const frame=useCurrentFrame(),t=frame/24;
 const scene=scenes.find(s=>t>=s.start&&t<s.end)||scenes[scenes.length-1];
 const st=t-scene.start-scene.offset;
 const cue=scene.cues.find(c=>st>=c.start&&st<c.end)?.value||'X';
 const talking=st>=0&&st<scene.duration;
 const night=t>29&&t<34?Math.sin((t-29)/5*Math.PI):0;
 const growth=easeInOutCubic(clamp((t-35)/6));const flower=easeInOutCubic(clamp((t-50)/4));
 const active=scene.words.findIndex(w=>st>=w.start&&st<w.end+.06);
 const group=active<0?[]:scene.words.slice(Math.floor(active/5)*5,Math.floor(active/5)*5+5);
 const intro=clamp((5-t)/1.5);const zoom=1+.025*Math.sin(t*.12);
 return <AbsoluteFill style={{background:'#def3ee',fontFamily:'DejaVu Sans, sans-serif',overflow:'hidden'}}>
 <Audio src={staticFile('soundtrack.wav')}/>
 <svg viewBox="0 0 1080 1920" width="1080" height="1920">
 <defs><linearGradient id="sky" x2="0" y2="1"><stop stopColor="#abe2f1"/><stop offset="1" stopColor="#f6fbdb"/></linearGradient><linearGradient id="earth" x2="0" y2="1"><stop stopColor="#ba7953"/><stop offset="1" stopColor="#8d563e"/></linearGradient></defs>
 <rect width="1080" height="1920" fill="url(#sky)"/>
 <g transform={`translate(${790-Math.sin(t*.1)*20},${310+Math.sin(t*.15)*12})`}>
 {Array.from({length:12},(_,i)=><path key={i} d="M0 -103 L0 -128" stroke="#efbb52" strokeWidth="10" strokeLinecap="round" transform={`rotate(${i*30+t*2})`}/>)}
 <circle r="78" fill="#ffdc70"/><path d="M-30 0 Q-22 -12 -14 0 M14 0 Q22 -12 30 0 M-20 24 Q0 42 20 24" fill="none" stroke="#c28c44" strokeWidth="5" strokeLinecap="round"/>
 </g>
 {[[-120,410],[630,570],[100,260]].map(([x,y],i)=><g key={i} transform={`translate(${x+(t*(i+1)*2)%350},${y})`} fill="white" opacity=".75"><ellipse cx="80" cy="25" rx="125" ry="38"/><circle cx="28" cy="0" r="53"/><circle cx="95" cy="-13" r="67"/><circle cx="152" cy="12" r="44"/></g>)}
 <path d="M0 860 Q280 650 580 850 Q880 660 1080 800 L1080 1920 L0 1920Z" fill="#99dba8"/>
 <path d="M0 1010 Q340 810 600 980 Q800 880 1080 980 L1080 1920 L0 1920Z" fill="#75c996"/>
 <path d="M0 1350 Q530 1020 1080 1350 L1080 1920 L0 1920Z" fill="#d2e9a7"/>
 <path d="M310 1920 Q860 1470 590 1240 Q870 1440 940 1920" fill="#f5dfac"/>
 <g transform={`translate(540 1090) scale(${zoom}) translate(-540 -1090)`}>
 {/* Gentle garden plants in the foreground. */}
 {[60,985].map((x,i)=><g key={x} transform={`translate(${x} 1300) rotate(${Math.sin(t+i)*2})`} stroke="#4c9f77" strokeWidth="10" fill="#70bc80"><path d="M0 170 L0 0"/><ellipse cx="-23" cy="57" rx="39" ry="18" transform="rotate(30 -23 57)"/><ellipse cx="27" cy="103" rx="42" ry="20" transform="rotate(-30 27 103)"/></g>)}
 <Character t={t} talk={talking&&scene.actor==='tico'} cue={scene.actor==='tico'?cue:'X'} x={74+Math.sin(t*.5)*5} y={790} excited={t>14&&t<20||t>42&&t<46}/>
 <Character rabbit t={t} talk={talking&&scene.actor==='lila'} cue={scene.actor==='lila'?cue:'X'} x={618+Math.sin(t*.5+2)*4} y={790} excited={t>37&&t<41}/>
 <ellipse cx="540" cy="1419" rx="139" ry="24" fill="#527a53" opacity=".14"/>
 <path d="M433 1290 L459 1394 Q540 1430 621 1394 L647 1290" fill="#e29c73" stroke="#b97958" strokeWidth="7"/>
 <rect x="420" y="1258" width="240" height="58" rx="21" fill="#f0b38b" stroke="#b97958" strokeWidth="7"/>
 <ellipse cx="540" cy="1259" rx="104" ry="20" fill="url(#earth)"/>
 {t<7&&<ellipse cx="540" cy={1237-Math.max(0,1-t)*80} rx="12" ry="18" fill="#efc26f" transform={`rotate(25 540 1237)`}/>}
 <g transform={`translate(540 1253) scale(${growth})`}>
 <path d={`M0 0 Q-22 -70 0 ${-120-flower*75}`} stroke="#438e60" strokeWidth="13" fill="none"/>
 <path d="M-7 -51 Q-100 -118 -90 -56 Q-61 -17 -7 -51" fill="#6bbf69" stroke="#438e60" strokeWidth="5"/>
 <path d="M-6 -90 Q72 -153 80 -99 Q65 -57 -6 -90" fill="#8dcf70" stroke="#438e60" strokeWidth="5"/>
 <g transform={`translate(0 ${-120-flower*75}) scale(${flower}) rotate(${Math.sin(t)*4})`}>
 {Array.from({length:7},(_,i)=><ellipse key={i} cx="0" cy="-42" rx="23" ry="40" fill="#ffcc70" stroke="#efaa57" strokeWidth="3" transform={`rotate(${i*360/7})`}/>)}<circle r="28" fill="#d78b52"/><circle cx="-9" cy="-3" r="3" fill="#7d533e"/><circle cx="9" cy="-3" r="3" fill="#7d533e"/><path d="M-9 9 Q0 17 9 9" stroke="#7d533e" strokeWidth="3" fill="none"/>
 </g></g>
 {t>=7&&t<14&&<g transform={`translate(385 1150) rotate(${-20+Math.sin(t*2)*6})`}><rect x="-55" y="-48" width="85" height="63" rx="20" fill="#78b6df" stroke="#4986b0" strokeWidth="5"/><path d="M25 -23 L91 -60 L104 -34 L29 3" fill="#78b6df" stroke="#4986b0" strokeWidth="5"/>{Array.from({length:5},(_,i)=><ellipse key={i} cx={110+i*9} cy={-12+((t*100+i*18)%90)} rx="4" ry="8" fill="#69bad9"/>)}</g>}
 {t>14&&t<21&&Array.from({length:5},(_,i)=><text key={i} x={300+i*105} y={1000-((t*40+i*60)%190)} fill={i%2?'#e9a14c':'#6c9cae'} fontSize="52" opacity=".8">♪</text>)}
 </g>
 <rect width="1080" height="1920" fill="#203866" opacity={night*.75}/>
 {night>.1&&Array.from({length:16},(_,i)=><circle key={i} cx={(i*139+87)%1050} cy={220+(i*173)%520} r={3+i%3} fill="#fff7ce" opacity={night}/>) }
 <text x="540" y="200" textAnchor="middle" fontSize="57" fontWeight="bold" fill="#306c64" letterSpacing="5">TICO &amp; LILA</text>
 {intro>0&&<g opacity={intro}><rect x="175" y="244" width="730" height="125" rx="38" fill="#fff9e9" opacity=".94"/><text x="540" y="324" textAnchor="middle" fontSize="45" fontWeight="bold" fill="#577360">A semente apressada</text></g>}
 {t>34&&t<38&&<g><rect x="298" y="414" width="484" height="80" rx="35" fill="#fff9e9"/><text x="540" y="468" textAnchor="middle" fontSize="35" fill="#577360">Alguns dias depois...</text></g>}
 {t>49&&t<53&&<g><rect x="298" y="414" width="484" height="80" rx="35" fill="#fff9e9"/><text x="540" y="468" textAnchor="middle" fontSize="35" fill="#577360">Mais alguns dias...</text></g>}
 {t>56&&<text x="540" y="610" textAnchor="middle" fontSize="43" fontWeight="bold" fill="#377463">Cuidar também é esperar.</text>}
 </svg>
 {group.length>0&&<div style={{position:'absolute',top:1510,left:100,width:880,minHeight:135,padding:'22px 34px',boxSizing:'border-box',borderRadius:35,background:'#fff9ecf2',boxShadow:'0 6px 0 #94bd8e66',display:'flex',alignItems:'center',justifyContent:'center',flexWrap:'wrap',gap:'5px 12px',fontSize:40,lineHeight:1.3,color:'#315e57',textAlign:'center'}}>{group.map((w,i)=><span key={i} style={{fontWeight:st>=w.start&&st<w.end?700:400,color:st>=w.start&&st<w.end?'#a85b3b':'#315e57'}}>{w.text}</span>)}</div>}
 </AbsoluteFill>
}
registerRoot(()=> <Composition id="KidsSeed" component={App} fps={24} durationInFrames={1440} width={1080} height={1920}/>);
