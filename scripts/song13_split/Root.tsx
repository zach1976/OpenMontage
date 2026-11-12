import React from 'react';
import {Composition} from 'remotion';
import {SplitLesson, LessonProps} from './SplitLesson';
export const Root:React.FC=()=> <Composition id="Song13SplitLesson" component={SplitLesson}
  durationInFrames={3600} fps={30} width={1080} height={1920}
  defaultProps={{} as LessonProps}
  calculateMetadata={({props})=>({durationInFrames:props.totalFrames,fps:props.fps,width:1080,height:1920})}/>;
