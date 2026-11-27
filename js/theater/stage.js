import { sfx } from "../audio.js";
import { getClipSources, getScene } from "./clips.js";
import { createMediaLayer } from "./player.js";
import { runInteraction } from "./interactions.js";

function pickRandom(arr, fallback = "") {
  if (!Array.isArray(arr) || !arr.length) return fallback;
  return arr[Math.floor(Math.random() * arr.length)];
}

/**
 * Fullscreen interactive film theater controller.
 * Never mutates store or calls backend APIs directly — delegates settlement to `onSettle`.
 */
export function mountTheater({ activityId, player, content, autoplay = false, onSettle, onExit }) {
  const scene = getScene(activityId);
  const clips = getClipSources(scene);
  let destroyed = false;
  let activeInteraction = null;
  const timers = new Set();

  const later = (fn, ms) => {
    const id = setTimeout(() => {
      timers.delete(id);
      if (!destroyed) fn();
    }, ms);
    timers.add(id);
    return id;
  };

  const prevHtmlOverflow = document.documentElement.style.overflow;
  const prevBodyOverflow = document.body.style.overflow;
  document.documentElement.style.overflow = "hidden";
  document.body.style.overflow = "hidden";

  const root = document.createElement("div");
  root.className = "th-root";
  root.innerHTML = `
    <div class="th-stage-media"></div>
    <div class="th-warm-overlay"></div>
    <div class="th-vignette"></div>
    <canvas class="th-fx-canvas" aria-hidden="true"></canvas>

    <header class="th-topbar">
      <button type="button" class="th-glass-btn" id="th-btn-exit">退出</button>
      <div class="th-topbar-right">
        <div class="th-score-chip">幸福指数 <strong id="th-hud-score">${player?.happiness ?? 100}</strong></div>
        <button type="button" class="th-glass-btn" id="th-btn-mute">${sfx.muted ? "静音" : "音效"}</button>
      </div>
    </header>

    <div class="th-title-card">
      <span class="th-title-sub"></span>
      <h1 class="th-title-main"></h1>
    </div>

    <div class="th-overlay"></div>
    <div class="th-autoplay-tag">${autoplay ? "自动观影中 · 同样计分" : ""}</div>

    <div class="th-swap-overlay">
      <div class="th-swap-rings">
        <div class="th-swap-num">100</div>
      </div>
      <div class="th-swap-msg"></div>
    </div>

    <section class="th-result-pill" aria-live="polite">
      <div class="th-result-head">
        <span class="th-result-kicker"></span>
        <span class="th-result-delta"></span>
      </div>
      <p class="th-result-line"></p>
      <p class="th-result-status"></p>
      <div class="th-result-actions">
        <button type="button" class="th-btn-primary" id="th-btn-replay">再来一次</button>
        <button type="button" class="th-btn-ghost" id="th-btn-back"></button>
      </div>
    </section>
  `;
  document.body.appendChild(root);

  const mediaRoot = root.querySelector(".th-stage-media");
  const warmEl = root.querySelector(".th-warm-overlay");
  const vignetteEl = root.querySelector(".th-vignette");
  const fxCanvas = root.querySelector(".th-fx-canvas");
  const titleCard = root.querySelector(".th-title-card");
  const overlayEl = root.querySelector(".th-overlay");
  const autoplayTag = root.querySelector(".th-autoplay-tag");
  const swapOverlay = root.querySelector(".th-swap-overlay");
  const swapNumEl = root.querySelector(".th-swap-num");
  const swapMsgEl = root.querySelector(".th-swap-msg");
  const resultPill = root.querySelector(".th-result-pill");
  const scoreEl = root.querySelector("#th-hud-score");
  const replayBtn = root.querySelector("#th-btn-replay");
  const backBtn = root.querySelector("#th-btn-back");

  const mediaLayer = createMediaLayer(mediaRoot, scene.tintClass);

  const cleanupAndExit = () => {
    destroy();
    onExit?.();
  };

  root.querySelector("#th-btn-exit").addEventListener("click", cleanupAndExit);
  backBtn.addEventListener("click", cleanupAndExit);
  root.querySelector("#th-btn-mute").addEventListener("click", (e) => {
    const muted = sfx.toggleMute();
    e.currentTarget.textContent = muted ? "静音" : "音效";
  });

  const onKeyDown = (e) => {
    if (e.key === "Escape") {
      e.preventDefault();
      cleanupAndExit();
    }
  };
  document.addEventListener("keydown", onKeyDown);

  let currentScore = player?.happiness ?? 100;

  const animateScoreNumber = (fromVal, toVal) => {
    const start = performance.now();
    const dur = 1100;
    const step = (now) => {
      if (destroyed) return;
      const t = Math.min(1, (now - start) / dur);
      const eased = 1 - Math.pow(1 - t, 3);
      swapNumEl.textContent = String(Math.round(fromVal + (toVal - fromVal) * eased));
      if (t < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };

  const runSequence = async () => {
    if (destroyed) return;
    activeInteraction?.cancel?.();
    activeInteraction = null;

    warmEl.style.opacity = "0";
    vignetteEl.classList.remove("is-warn", "is-cold");
    swapOverlay.classList.remove("is-visible");
    resultPill.classList.remove("is-visible");
    autoplayTag.style.display = autoplay ? "" : "none";

    // Step 1: Intro loop + title card + preload outcome clips
    titleCard.querySelector(".th-title-sub").textContent = scene.subtitle;
    titleCard.querySelector(".th-title-main").textContent = scene.title;
    titleCard.classList.add("is-visible");

    mediaLayer.preload(clips.win);
    mediaLayer.preload(clips.fail_phone);
    mediaLayer.preload(clips.fail_hazard);
    mediaLayer.preload(clips.swap);

    await mediaLayer.show({
      video: clips.intro,
      fallback: clips.introFallback,
      loop: true,
    });
    if (destroyed) return;

    await new Promise((res) => later(res, 1800));
    if (destroyed) return;
    titleCard.classList.remove("is-visible");

    // Step 2: Keyframe interaction
    activeInteraction = runInteraction(scene.interaction, {
      overlayEl,
      canvas: fxCanvas,
      vignetteEl,
      warmOverlayEl: warmEl,
      mediaLayer,
      autoplay,
      content,
    });
    const { outcome } = await activeInteraction;
    activeInteraction = null;
    if (destroyed) return;

    autoplayTag.style.display = "none";
    const isWin = outcome === "win";
    const delta = isWin ? scene.win : scene.fail;

    if (isWin) {
      sfx.playSuccess();
      warmEl.style.opacity = "0.28";
    } else {
      sfx.playFail();
      vignetteEl.classList.add("is-cold");
    }

    // Step 3: Outcome clip (non-looping)
    const clipUrl =
      outcome === "win" ? clips.win : outcome === "phone_fail" ? clips.fail_phone : clips.fail_hazard;
    const fallbackImg =
      outcome === "win"
        ? clips.winFallback
        : outcome === "phone_fail"
          ? clips.failPhoneFallback
          : clips.failHazardFallback;

    const clipPromise = mediaLayer.show({
      video: clipUrl,
      fallback: fallbackImg,
      secondaryFallback: "./assets/img/bruce_sulk.jpg",
      loop: false,
      duration: 4200,
    });

    // Step 4: Fade in settlement pill ~1.2s after outcome clip begins
    await new Promise((res) => later(res, 1200));
    if (destroyed) return;

    const actCopy = content?.activities?.[scene.id] || {};
    const linePool =
      outcome === "win"
        ? actCopy.win_lines
        : outcome === "phone_fail"
          ? actCopy.phone_fail_lines
          : actCopy.hazard_fail_lines;
    const summaryLine = pickRandom(
      linePool,
      isWin ? "布鲁斯开心地蹭了蹭你，尾巴摇成小风扇。" : "布鲁斯耳朵贴平扭过头去，有点委屈。",
    );

    const kickerEl = resultPill.querySelector(".th-result-kicker");
    const deltaEl = resultPill.querySelector(".th-result-delta");
    const lineEl = resultPill.querySelector(".th-result-line");
    const statusEl = resultPill.querySelector(".th-result-status");

    kickerEl.textContent =
      outcome === "win" ? "陪伴成功" : outcome === "phone_fail" ? "被手机抢走了" : "踩到雷点了";
    deltaEl.textContent = `${delta >= 0 ? "+" : ""}${delta}`;
    deltaEl.classList.toggle("is-neg", delta < 0);
    lineEl.textContent = summaryLine;

    const projectedScore = Math.max(0, currentScore + delta);
    statusEl.textContent = "正在同步幸福指数……";
    replayBtn.hidden = projectedScore < 80;
    backBtn.textContent =
      projectedScore < 80
        ? "去私厨鲜食柜"
        : scene.zone === "home"
          ? "回到小院"
          : "回到街区";
    resultPill.classList.add("is-visible");

    // Step 5: Settle via host callback
    const triggerSwapCandidate = isWin && Math.random() < scene.swapProb;
    try {
      const swap = await onSettle?.({
        outcome,
        delta,
        triggerSwapCandidate,
        summaryLine,
      });
      if (destroyed) return;

      currentScore = Number.isFinite(swap?.newScore) ? swap.newScore : projectedScore;
      scoreEl.textContent = String(currentScore);
      replayBtn.hidden = currentScore < 80;

      if (currentScore < 80) {
        statusEl.textContent = "布鲁斯扭过头生闷气，去私厨冷柜哄回 80 分";
        backBtn.textContent = "去私厨鲜食柜";
      } else {
        statusEl.textContent = `当前幸福指数 · ${currentScore}`;
        backBtn.textContent = scene.zone === "home" ? "回到小院" : "回到街区";
      }

      if (Number.isFinite(swap?.newScore)) {
        resultPill.classList.remove("is-visible");
        mediaLayer.show({
          video: clips.swap,
          fallback: clips.swapFallback,
          loop: true,
        });
        swapMsgEl.textContent = swap.topBonus
          ? "已经站在最高处，再送你 +6"
          : `这一束光来自 ${swap.targetNickname || "一位新朋友"}`;
        swapOverlay.classList.add("is-visible");
        sfx.playSwapCelebration();
        animateScoreNumber(swap.oldScore ?? projectedScore, swap.newScore);

        await new Promise((res) => later(res, 3400));
        if (destroyed) return;
        swapOverlay.classList.remove("is-visible");
        statusEl.textContent = `高位换分完成 · 当前幸福指数 ${swap.newScore}`;
        resultPill.classList.add("is-visible");
      }
    } catch (_) {
      if (!destroyed) {
        statusEl.textContent = "结算暂未同步，请稍后重试";
      }
    }

    await clipPromise;
  };

  replayBtn.addEventListener("click", () => {
    if (currentScore < 80) return;
    sfx.playTap();
    runSequence();
  });

  runSequence();

  function destroy() {
    if (destroyed) return;
    destroyed = true;
    activeInteraction?.cancel?.();
    activeInteraction = null;
    timers.forEach((t) => clearTimeout(t));
    timers.clear();
    document.removeEventListener("keydown", onKeyDown);
    mediaLayer.destroy();
    root.remove();
    document.documentElement.style.overflow = prevHtmlOverflow;
    document.body.style.overflow = prevBodyOverflow;
  }

  return { destroy };
}
