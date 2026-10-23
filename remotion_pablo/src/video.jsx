import React from "react";
import {AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame, useVideoConfig, interpolate} from "remotion";

/* Remotion sobre o vídeo original, com voz neural, lip sync e personagens reais preservados.
   Não recriamos Pablo e Marina usando imagens paradas. */
const gold = "#EBD09C";
const blue = "#72D6DA";
const opt = {extrapolateLeft: "clamp", extrapolateRight: "clamp"};
const noise = (n) => {const v = Math.sin((n + 3) * 213.23) * 6137.17; return v - Math.floor(v);};
const fade = (t, a, b, d = 0.20) => Math.min(1, Math.max(0, (t-a)/d)) *
  Math.min(1, Math.max(0, (b-t)/d));

export const PabloRemotion = ({title="PABLO GURU", clips=[], durationSeconds=27}) => {
  const frame = useCurrentFrame();
  const fps = useVideoConfig().fps;
  const t = frame / fps;
  const found = clips.findIndex((c) => c.ini <= t && t < c.fim);
  const idx = found < 0 ? 0 : found;
  const scene = clips[idx];
  const virada = !!scene && (scene.desfecho || (idx >= 5 && idx <= 6));
  const first = clips[0] || {ini:.6,fim:4};
  const introAlpha = fade(t, first.ini, Math.min(first.fim, first.ini+3.3));
  const labelAlpha = scene ? fade(t, scene.ini + .1, Math.min(scene.fim, scene.ini+3), .2) : 0;
  const endAlpha = interpolate(t, [durationSeconds-1.1,durationSeconds-.25], [0,.8],opt);
  const camScale = 1.023 + Math.sin(t * .3) * .006 + (virada ? .007 : 0);
  const sceneName = idx === 0 ? "O GANCHO" :
    virada ? "A VIRADA" : scene && scene.falante === "pablo" ? "A HISTÓRIA" : "A DESCOBERTA";
  const cut = clips.slice(1).find((c) => Math.abs(t-c.ini) < .11);
  return <AbsoluteFill style={{background: "#091d26", overflow: "hidden", fontFamily: "Arial,sans-serif"}}>
    <AbsoluteFill style={{transform:"translate("+(Math.sin(t*.17)*5)+"px,"+(Math.cos(t*.21)*4)+"px) scale("+camScale+")"}}>
      <OffthreadVideo src={staticFile("source.mp4")} style={{width:"100%",height:"100%",objectFit:"cover"}} />
    </AbsoluteFill>
    <AbsoluteFill style={{background:"linear-gradient(to bottom,rgba(0,17,24,.44),transparent 16%,transparent 79%,rgba(0,11,18,.39))",pointerEvents:"none"}}/>
    <AbsoluteFill style={{border:"4px solid rgba(228,194,135,.12)",pointerEvents:"none"}}/>
    <div style={{position:"absolute",left:52,top:65,width:4,height:84,background:gold,boxShadow:"0 0 18px "+gold}}/>
    <div style={{position:"absolute",left:75,top:64,fontSize:27,fontWeight:900,letterSpacing:5,color:gold,textShadow:"0 2px 10px #17252a"}}>@OPABLOGURU</div>
    <div style={{position:"absolute",left:75,top:112,fontSize:15,letterSpacing:4,color:"#eff8f3"}}>UMA HISTÓRIA. UMA VIRADA.</div>
    {Array.from({length:18}).map((_,n) => {
      const x=n%2===0 ? 7+noise(n)*70 : 995+noise(n)*76;
      const y=(noise(n+50)*1920+t*(17+n))%1930;
      const op=.12+Math.max(0,Math.sin(t*1.3+n))*.26;
      return <div key={n} style={{position:"absolute",left:x,top:y,width:3,height:3,borderRadius:"50%",opacity:op,background:n%3===0?blue:gold,boxShadow:"0 0 12px "+gold}}/>;
    })}
    <div style={{position:"absolute",top:197,left:78,right:78,textAlign:"center",fontSize:43,fontWeight:900,
      letterSpacing:2,color:gold,opacity:introAlpha,textShadow:"0 4px 20px #041826"}}>ESCUTE ISSO.</div>
    <div style={{position:"absolute",bottom:144,left:58,right:58,display:"flex",justifyContent:"space-between",alignItems:"end"}}>
      <div style={{color:"#faf7ee",fontSize:24,fontWeight:900,letterSpacing:3,opacity:labelAlpha,
        transform:"translateY("+((1-labelAlpha)*12)+"px)",borderLeft:"5px solid "+(virada?gold:blue),paddingLeft:18,
        textShadow:"0 2px 10px #001827"}}>{sceneName}</div>
      <div style={{fontSize:18,color:gold,fontWeight:800,letterSpacing:2,opacity:.87}}>PABLO GURU</div>
    </div>
    <div style={{position:"absolute",bottom:82,left:52,right:52,height:5,background:"rgba(255,255,255,.25)",borderRadius:5}}>
      <div style={{height:"100%",width:Math.min(100,(t/durationSeconds)*100)+"%",
        borderRadius:5,background:"linear-gradient(90deg,"+blue+","+gold+")",boxShadow:"0 0 13px "+gold}}/>
    </div>
    {virada && <AbsoluteFill style={{pointerEvents:"none",background:"radial-gradient(ellipse,transparent 42%,rgba(235,195,115,.13))"}}/>}
    {cut && <AbsoluteFill style={{pointerEvents:"none",background:"rgba(250,227,169,"+(.11*(1-Math.abs(t-cut.ini)/.11))+")"}}/>}
    {endAlpha>0 && <AbsoluteFill style={{background:"rgba(7,25,32,"+endAlpha+")",display:"flex",
      justifyContent:"center",alignItems:"center",flexDirection:"column",textAlign:"center",color:"#fbf1d9",
      fontWeight:900,fontSize:55,letterSpacing:4}}>
      <div>GUARDE ESTA REFLEXÃO</div>
      <div style={{color:gold,fontSize:32,marginTop:22}}>@opabloguru</div>
    </AbsoluteFill>}
  </AbsoluteFill>;
};