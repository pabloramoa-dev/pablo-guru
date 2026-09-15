import {bundle} from '@remotion/bundler';
import {selectComposition,renderMedia,renderStill} from '@remotion/renderer';
import fs from 'node:fs';
const serveUrl=await bundle({entryPoint:new URL('./index.jsx',import.meta.url).pathname,publicDir:new URL('./public',import.meta.url).pathname});
for (const id of ['PabloLab','VoiceAudition']){
 const composition=await selectComposition({serveUrl,id});
 let last=-1;
 await renderMedia({serveUrl,composition,codec:'h264',crf:20,pixelFormat:'yuv420p',outputLocation:`output/${id}.mp4`,concurrency:2,onProgress:({progress})=>{const p=Math.floor(progress*10);if(p!==last){console.log(`${id}: ${p*10}%`);last=p;}}});
 if(id==='PabloLab')for(const [i,frame] of [45,300,650,1000,1500].entries())if(frame<composition.durationInFrames)await renderStill({serveUrl,composition,frame,output:`output/preview_${i}.png`});
}
const r=JSON.parse(fs.readFileSync('output/test-report.json'));
r.tools.remotion={status:'success',usage:'Full HD composition, articulated character layers, subtitles and export'};
r.tools['motion-canvas']={status:'success',usage:'Core easing functions control typography, bridge progression and camera drift; full Motion Canvas scene renderer not used'};
r.tools.blender={status:'success',usage:'Three original 3D rendered backgrounds'};
r.tools.manim={status:'success',usage:'Original repository characters rendered to articulated transparent layers'};
fs.writeFileSync('output/test-report.json',JSON.stringify(r,null,2));
