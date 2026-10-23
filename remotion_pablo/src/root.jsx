import React from "react";
import {Composition} from "remotion";
import {PabloRemotion} from "./video";
const defaults = {
  title: "PABLO GURU", durationSeconds: 27,
  clips: [{ini: 0.6, fim: 5, falante: "perguntadora", texto: "O medo de errar te paralisa? Escute isso."}]
};
export const Root = () => <Composition id="PabloGuruRemotion" component={PabloRemotion}
  width={1080} height={1920} fps={30} durationInFrames={810}
  defaultProps={defaults}
  calculateMetadata={({props}) => ({durationInFrames: Math.max(30, Math.round(props.durationSeconds * 30))})}/>;