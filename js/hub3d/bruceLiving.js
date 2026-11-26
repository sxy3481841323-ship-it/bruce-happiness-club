import { createRiggedBruce } from "./bruceRigged.js";

/**
 * Shared living-pet entrypoint backed by the 86-bone rigged Bruce controller.
 * Falls back cleanly when callers still pass the legacy static bruce.glb path.
 */
export function createLivingBruce(opts = {}) {
  const rawUrl = opts.modelUrl || "./assets/models/bruce_rigged.glb";
  const resolvedUrl = rawUrl.endsWith("/bruce.glb")
    ? "./assets/models/bruce_rigged.glb"
    : rawUrl;
  return createRiggedBruce({
    ...opts,
    modelUrl: resolvedUrl,
  });
}
