import React from 'react';
import {Composition} from 'remotion';
import {KheedkanLesson, LessonProps} from './Composition';

export const Root: React.FC = () => <Composition
  id="KheedkanLesson"
  component={KheedkanLesson}
  durationInFrames={2700}
  fps={30}
  width={1080}
  height={1920}
  defaultProps={{} as LessonProps}
  calculateMetadata={({props}) => ({durationInFrames: props.totalFrames, fps: props.fps, width: 1080, height: 1920})}
/>;
