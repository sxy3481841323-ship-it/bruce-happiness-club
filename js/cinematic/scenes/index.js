import { homeScenes } from './home.js';
import { streetScenes } from './street.js';

export const cinematicScenes = Object.freeze({ ...homeScenes, ...streetScenes });
export const activityIds = Object.freeze(Object.keys(cinematicScenes));
export function getScene(activityId) {
  if (!Object.hasOwn(cinematicScenes, activityId))
    throw new RangeError(`Unknown cinematic activity: ${activityId}`);
  const config = cinematicScenes[activityId];
  return config;
}
