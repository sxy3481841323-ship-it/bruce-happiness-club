/**
 * Dual-buffered fullscreen media layer (zero-black crossfade between video/Ken Burns image fallbacks).
 */
export function createMediaLayer(rootEl, baseTintClass = "") {
  const layers = [0, 1].map(() => {
    const el = document.createElement("div");
    el.className = "th-layer";
    rootEl.appendChild(el);
    return el;
  });

  let activeIdx = 0;
  let destroyed = false;
  let showToken = 0;
  let activeResolve = null;
  const timers = new Set();
  const preloadedVideos = [];

  function trackTimer(id) {
    timers.add(id);
    return id;
  }

  function clearMediaEl(layerEl) {
    const vids = layerEl.querySelectorAll("video");
    vids.forEach((v) => {
      try {
        v.pause();
        v.removeAttribute("src");
        v.load();
      } catch (_) {}
    });
    layerEl.innerHTML = "";
    layerEl.className = "th-layer";
  }

  function resolvePending() {
    if (activeResolve) {
      const fn = activeResolve;
      activeResolve = null;
      fn();
    }
  }

  function mountImageFallback(layerEl, fallbackSrc, secondaryFallback, loop, duration, tintClass, onDone) {
    clearMediaEl(layerEl);
    if (tintClass) layerEl.classList.add(tintClass);
    const img = document.createElement("img");
    img.className = "th-media th-kenburns";
    img.alt = "";
    img.style.animationDuration = loop ? "9000ms" : `${duration}ms`;
    img.style.animationIterationCount = loop ? "infinite" : "1";
    img.src = fallbackSrc;
    img.addEventListener("error", () => {
      if (secondaryFallback && !img.dataset.secTried) {
        img.dataset.secTried = "1";
        img.src = secondaryFallback;
      }
    });
    layerEl.appendChild(img);

    if (!loop) {
      const t = trackTimer(setTimeout(() => {
        timers.delete(t);
        onDone();
      }, duration));
    }
  }

  function show({ video, fallback, secondaryFallback = "", loop = false, duration = 4200, tint = baseTintClass }) {
    if (destroyed) return Promise.resolve();
    resolvePending();
    const token = ++showToken;
    const nextIdx = 1 - activeIdx;
    const nextLayer = layers[nextIdx];
    const prevLayer = layers[activeIdx];
    clearMediaEl(nextLayer);
    if (tint) nextLayer.classList.add(tint);

    return new Promise((resolve) => {
      let settled = false;
      const done = () => {
        if (settled) return;
        settled = true;
        if (activeResolve === done) activeResolve = null;
        resolve();
      };
      activeResolve = done;

      const activateLayer = () => {
        if (destroyed || token !== showToken) {
          done();
          return;
        }
        nextLayer.classList.add("is-active");
        prevLayer.classList.remove("is-active");
        activeIdx = nextIdx;
        const cleanupPrev = trackTimer(setTimeout(() => {
          timers.delete(cleanupPrev);
          if (!destroyed && activeIdx === nextIdx) clearMediaEl(prevLayer);
        }, 480));
        if (loop) done();
      };

      const vid = document.createElement("video");
      vid.className = "th-media";
      vid.muted = true;
      vid.playsInline = true;
      vid.loop = loop;
      vid.preload = "auto";
      vid.setAttribute("muted", "");
      vid.setAttribute("playsinline", "");
      vid.setAttribute("webkit-playsinline", "");
      vid.setAttribute("x5-playsinline", "");

      let switchedToFallback = false;
      const fallbackToImage = () => {
        if (switchedToFallback || destroyed || token !== showToken) return;
        switchedToFallback = true;
        clearTimeout(loadTimeout);
        mountImageFallback(nextLayer, fallback, secondaryFallback, loop, duration, tint, done);
        activateLayer();
      };

      const loadTimeout = trackTimer(setTimeout(() => {
        timers.delete(loadTimeout);
        fallbackToImage();
      }, 2500));

      vid.addEventListener("loadeddata", () => {
        if (switchedToFallback || destroyed || token !== showToken) return;
        clearTimeout(loadTimeout);
        timers.delete(loadTimeout);
        nextLayer.appendChild(vid);
        vid.play().catch(() => {});
        activateLayer();
        if (!loop) {
          const safety = trackTimer(setTimeout(() => {
            timers.delete(safety);
            done();
          }, Math.max(duration + 4000, 12000)));
          vid.addEventListener("ended", () => {
            clearTimeout(safety);
            timers.delete(safety);
            done();
          }, { once: true });
        }
      }, { once: true });

      vid.addEventListener("error", fallbackToImage, { once: true });
      vid.src = video;
      vid.load();
    });
  }

  function preload(src) {
    if (destroyed || !src) return;
    const v = document.createElement("video");
    v.muted = true;
    v.preload = "auto";
    v.src = src;
    preloadedVideos.push(v);
  }

  function setSlowmo(on) {
    rootEl.classList.toggle("th-slowmo", Boolean(on));
  }

  function destroy() {
    destroyed = true;
    showToken++;
    resolvePending();
    timers.forEach((t) => clearTimeout(t));
    timers.clear();
    layers.forEach((l) => clearMediaEl(l));
    preloadedVideos.forEach((v) => {
      try {
        v.removeAttribute("src");
        v.load();
      } catch (_) {}
    });
    preloadedVideos.length = 0;
  }

  return { show, preload, setSlowmo, destroy };
}
