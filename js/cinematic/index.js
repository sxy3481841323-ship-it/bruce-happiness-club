import { CinematicDirector } from './director.js';
export { activityIds, cinematicScenes } from './scenes/index.js';

/**
 * Fullscreen, offline Three.js stage. onComplete fires once, after the 3.5s outro.
 * It reports a result only; score/API ownership stays with the calling application.
 * Optional preview controls are additive to the stable { destroy() } contract.
 */
export function mountCinematicStage(containerEl, options = {}) {
  let director;
  const mount = (next) => {
    director = new CinematicDirector(containerEl, { ...next, onRestart: mount });
  };
  mount(options);
  return {
    destroy: () => director.destroy(),
    setAutoplay: (enabled) => director.setAutoplay(enabled),
    revealSwap: (response) => director.revealSwap(response),
    getSnapshot: () => director.getSnapshot(),
  };
}
