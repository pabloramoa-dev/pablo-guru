import {bundle} from '@remotion/bundler';
import {selectComposition,renderMedia,renderStill} from '@remotion/renderer';
const serveUrl=await bundle({entryPoint:new URL('./index.jsx',import.meta.url).pathname,publicDir:new URL('./public',import.meta.url).pathname});
const composition=await selectComposition({serveUrl,id:'KidsSeed'});
let last=-1;
await renderMedia({serveUrl,composition,codec:'h264',crf:20,pixelFormat:'yuv420p',outputLocation:'output/Tico_e_Lila_A_Semente_Apressada.mp4',concurrency:2,onProgress:({progress})=>{const n=Math.floor(progress*10);if(n!==last){console.log(n*10+'%');last=n;}}});
for(const [i,frame] of [48,240,880,1300].entries())await renderStill({serveUrl,composition,frame,output:`output/preview_${i}.png`});
