import { sfx } from "../audio.js";

function pickRandom(arr) {
  if (!Array.isArray(arr) || !arr.length) return null;
  return arr[Math.floor(Math.random() * arr.length)];
}

function shuffle(arr) {
  const out = [...arr];
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

/**
 * Run a fullscreen interaction inside the theater overlay.
 * Returns a Promise<{ outcome: "win" | "phone_fail" | "hazard_fail" }> with `.cancel()` attached.
 */
export function runInteraction(type, ctx) {
  const { overlayEl, canvas, vignetteEl, warmOverlayEl, mediaLayer, autoplay, content, onPhoneTap } = ctx;

  let finished = false;
  let rafId = null;
  const timers = new Set();
  const cleanups = [];
  const particles = [];

  const later = (fn, ms) => {
    const id = setTimeout(() => {
      timers.delete(id);
      if (!finished) fn();
    }, ms);
    timers.add(id);
    return id;
  };

  const listen = (el, ev, fn, opts) => {
    el.addEventListener(ev, fn, opts);
    cleanups.push(() => el.removeEventListener(ev, fn, opts));
  };

  const spawnParticles = (x, y, kind = "gold", count = 10) => {
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 40 + Math.random() * 110;
      particles.push({
        x,
        y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - (kind === "note" ? 45 : 20),
        life: 0,
        maxLife: 0.55 + Math.random() * 0.45,
        r: kind === "warm" ? 5 + Math.random() * 6 : 2.5 + Math.random() * 3,
        kind,
      });
    }
  };

  // Single rAF particle loop
  const pCtx = canvas.getContext("2d");
  let lastT = performance.now();
  const drawLoop = (now) => {
    if (finished) return;
    const dt = Math.min(0.05, (now - lastT) / 1000);
    lastT = now;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = canvas.clientWidth || window.innerWidth;
    const h = canvas.clientHeight || window.innerHeight;
    if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
    }
    pCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
    pCtx.clearRect(0, 0, w, h);

    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.life += dt;
      if (p.life >= p.maxLife) {
        particles.splice(i, 1);
        continue;
      }
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      p.vy += (p.kind === "water" ? 210 : p.kind === "note" ? -25 : 40) * dt;
      const alpha = 1 - p.life / p.maxLife;
      pCtx.save();
      pCtx.globalAlpha = alpha;
      if (p.kind === "water") {
        pCtx.fillStyle = "#B8E4FF";
        pCtx.beginPath();
        pCtx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        pCtx.fill();
      } else if (p.kind === "note") {
        pCtx.fillStyle = "#FFE5A3";
        pCtx.font = "bold 16px sans-serif";
        pCtx.fillText("♪", p.x, p.y);
      } else if (p.kind === "warm") {
        pCtx.fillStyle = "rgba(255, 214, 134, 0.85)";
        pCtx.beginPath();
        pCtx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        pCtx.fill();
      } else {
        pCtx.fillStyle = "#FFE39C";
        pCtx.beginPath();
        pCtx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        pCtx.fill();
      }
      pCtx.restore();
    }

    rafId = requestAnimationFrame(drawLoop);
  };
  rafId = requestAnimationFrame(drawLoop);

  let resolveOuter;
  const cleanupAll = () => {
    if (finished) return;
    finished = true;
    if (rafId) cancelAnimationFrame(rafId);
    timers.forEach((t) => clearTimeout(t));
    timers.clear();
    cleanups.forEach((fn) => fn());
    cleanups.length = 0;
    mediaLayer?.setSlowmo(false);
    vignetteEl?.classList.remove("is-warn");
    overlayEl.innerHTML = "";
  };

  const finish = (outcome) => {
    if (finished) return;
    cleanupAll();
    resolveOuter({ outcome });
  };

  const promise = new Promise((resolve) => {
    resolveOuter = resolve;

    const promptEl = document.createElement("div");
    promptEl.className = "th-prompt";
    overlayEl.appendChild(promptEl);

    // Ghost cursor for autoplay
    let ghostEl = null;
    if (autoplay) {
      ghostEl = document.createElement("div");
      ghostEl.className = "th-ghost";
      ghostEl.style.left = "50%";
      ghostEl.style.top = "62%";
      overlayEl.appendChild(ghostEl);
    }

    const moveGhostTo = (xPct, yPct, tap = false) => {
      if (!ghostEl) return;
      ghostEl.style.left = `${xPct}%`;
      ghostEl.style.top = `${yPct}%`;
      if (tap) {
        later(() => {
          ghostEl.classList.add("is-tap");
          later(() => ghostEl?.classList.remove("is-tap"), 180);
        }, 420);
      }
    };

    const moveGhostToEl = (el, tap = false) => {
      if (!ghostEl || !el) return;
      const r = el.getBoundingClientRect();
      const xPct = ((r.left + r.width * 0.5) / window.innerWidth) * 100;
      const yPct = ((r.top + r.height * 0.5) / window.innerHeight) * 100;
      moveGhostTo(xPct, yPct, tap);
    };

    // Shared phone temptation banner (up to 2 times)
    let phoneEl = null;
    let phoneShownCount = 0;
    const triggerPhoneNotification = (forceAutoplayTap = false) => {
      if (finished || phoneShownCount >= 2 || phoneEl) return;
      phoneShownCount += 1;
      const note = pickRandom(content?.phone_notifications) || {
        app: "CHAT",
        text: "NEW MESSAGE · 99+",
      };
      const banner = document.createElement("button");
      banner.type = "button";
      banner.className = "th-phone-banner";
      banner.innerHTML = `
        <span class="th-phone-app"></span>
        <span class="th-phone-body">
          <span class="th-phone-title"></span>
          <span class="th-phone-text"></span>
        </span>
      `;
      banner.querySelector(".th-phone-app").textContent = String(note.app || "CHAT").slice(0, 4);
      banner.querySelector(".th-phone-title").textContent = `${note.app || "NOTIFICATION"} · NOW`;
      banner.querySelector(".th-phone-text").textContent = note.text || "NEW MESSAGE";
      overlayEl.appendChild(banner);
      phoneEl = banner;

      listen(banner, "click", (e) => {
        e.stopPropagation();
        sfx.playPhoneBuzz();
        onPhoneTap?.();
        finish("phone_fail");
      });

      requestAnimationFrame(() => banner.classList.add("is-shown"));
      sfx.playPhoneBuzz();

      if (forceAutoplayTap) {
        later(() => {
          moveGhostTo(50, 11, true);
          later(() => {
            sfx.playPhoneBuzz();
            onPhoneTap?.();
            finish("phone_fail");
          }, 680);
        }, 700);
        return;
      }

      later(() => {
        banner.classList.remove("is-shown");
        later(() => {
          banner.remove();
          if (phoneEl === banner) phoneEl = null;
        }, 380);
      }, 2600);
    };

    // Autoplay scripted outcome roll: 75% win, 25% fail (split phone_fail / hazard_fail)
    let autoOutcome = "win";
    if (autoplay) {
      const r = Math.random();
      if (r >= 0.75) autoOutcome = r < 0.88 ? "phone_fail" : "hazard_fail";
    }

    // Schedule regular phone temptations (unless autoplay rolled phone_fail, which triggers on cue)
    if (!autoplay || autoOutcome === "win") {
      later(() => triggerPhoneNotification(false), 1200 + Math.random() * 1800);
      later(() => triggerPhoneNotification(false), 4500 + Math.random() * 1800);
    }

    // --- Interaction 1: brush ---
    if (type === "brush") {
      promptEl.textContent = "在屏幕中央按住轻轻来回顺毛";
      const zone = document.createElement("div");
      zone.className = "th-brush-zone";
      const track = document.createElement("div");
      track.className = "th-progress-track";
      const fill = document.createElement("div");
      fill.className = "th-progress-fill";
      track.appendChild(fill);

      const dryer = document.createElement("button");
      dryer.type = "button";
      dryer.className = "th-corner-hazard";
      dryer.textContent = "DRYER · 吹风机";
      overlayEl.append(zone, track, dryer);

      listen(dryer, "click", (e) => {
        e.stopPropagation();
        finish("hazard_fail");
      });

      let progress = 0;
      const TARGET = 2200;
      let warning = false;
      let warnedOnce = false;
      let warnMove = 0;
      let dragging = false;
      let lastPos = null;
      let lastSfxAt = 0;

      const handleStroke = (dx, dy, cx, cy) => {
        const dist = Math.hypot(dx, dy);
        if (dist < 1) return;
        if (warning) {
          warnMove += dist;
          if (warnMove > 60) {
            finish("hazard_fail");
          }
          return;
        }
        progress = Math.min(TARGET, progress + dist);
        fill.style.width = `${(progress / TARGET) * 100}%`;
        spawnParticles(cx, cy, "gold", 3);
        const now = performance.now();
        if (now - lastSfxAt > 260) {
          lastSfxAt = now;
          sfx.playTap();
        }
        if (!warnedOnce && progress >= TARGET * 0.42) {
          warnedOnce = true;
          warning = true;
          warnMove = 0;
          vignetteEl.classList.add("is-warn");
          promptEl.textContent = "耳朵贴平了…先停一下！";
          later(() => {
            warning = false;
            vignetteEl.classList.remove("is-warn");
            promptEl.textContent = "布鲁斯放松了，继续轻轻顺毛";
          }, 1400);
        }
        if (progress >= TARGET) {
          finish("win");
        }
      };

      listen(overlayEl, "pointerdown", (e) => {
        if (autoplay || e.target === dryer || e.target.closest(".th-phone-banner")) return;
        const r = zone.getBoundingClientRect();
        if (e.clientX >= r.left - 30 && e.clientX <= r.right + 30 && e.clientY >= r.top - 30 && e.clientY <= r.bottom + 30) {
          dragging = true;
          lastPos = { x: e.clientX, y: e.clientY };
        }
      });

      listen(overlayEl, "pointermove", (e) => {
        if (autoplay || !dragging || !lastPos) return;
        handleStroke(e.clientX - lastPos.x, e.clientY - lastPos.y, e.clientX, e.clientY);
        lastPos = { x: e.clientX, y: e.clientY };
      });

      listen(window, "pointerup", () => {
        dragging = false;
        lastPos = null;
      });

      if (autoplay) {
        let stepIdx = 0;
        const stepBrush = () => {
          if (finished) return;
          if (autoOutcome === "phone_fail" && stepIdx === 2) {
            triggerPhoneNotification(true);
            return;
          }
          if (autoOutcome === "hazard_fail" && stepIdx === 2) {
            moveGhostToEl(dryer, true);
            later(() => finish("hazard_fail"), 650);
            return;
          }
          if (warning) {
            later(stepBrush, 450);
            return;
          }
          const xPct = stepIdx % 2 === 0 ? 38 : 62;
          const yPct = 50 + (stepIdx % 3 - 1) * 4;
          moveGhostTo(xPct, yPct, false);
          handleStroke(480, 40, window.innerWidth * (xPct / 100), window.innerHeight * (yPct / 100));
          stepIdx += 1;
          later(stepBrush, 720);
        };
        later(stepBrush, 400);
      }
      return;
    }

    // --- Interaction 2: rainVinyl ---
    if (type === "rainVinyl") {
      promptEl.textContent = "按顺序安顿布鲁斯：擦爪 → 盖毯 → 放黑胶";
      const circle = document.createElement("div");
      circle.className = "th-drop-circle";
      circle.textContent = "轻触道具安顿";
      const row = document.createElement("div");
      row.className = "th-props-row";

      const items = shuffle([
        { id: "towel", label: "TOWEL · 毛巾", kind: "water" },
        { id: "blanket", label: "BLANKET · 毛毯", kind: "warm" },
        { id: "vinyl", label: "VINYL · 黑胶", kind: "note" },
      ]);
      const order = ["towel", "blanket", "vinyl"];
      let step = 0;
      const btnMap = {};

      const applyProp = (item, btn, cx, cy) => {
        if (finished || btn.classList.contains("is-done")) return;
        if (item.id !== order[step]) {
          finish("hazard_fail");
          return;
        }
        btn.classList.add("is-done");
        step += 1;
        sfx.playTap();
        warmOverlayEl.style.opacity = String(step * 0.12);
        spawnParticles(cx, cy, item.kind, 16);
        if (step === 1) promptEl.textContent = "爪子擦干啦，接下来披上毛毯";
        else if (step === 2) promptEl.textContent = "暖烘烘的，点黑胶唱机放音乐";
        else {
          later(() => finish("win"), 650);
        }
      };

      items.forEach((item) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "th-prop-pill";
        btn.textContent = item.label;
        btnMap[item.id] = { item, btn };
        row.appendChild(btn);

        let startX = 0;
        let startY = 0;
        let active = false;
        listen(btn, "pointerdown", (e) => {
          if (autoplay) return;
          e.stopPropagation();
          active = true;
          startX = e.clientX;
          startY = e.clientY;
        });
        listen(btn, "pointermove", (e) => {
          if (!active) return;
          const dx = e.clientX - startX;
          const dy = e.clientY - startY;
          btn.style.transform = `translate3d(${dx}px, ${dy}px, 0) scale(1.04)`;
        });
        listen(btn, "pointerup", (e) => {
          if (!active) return;
          active = false;
          const dist = Math.hypot(e.clientX - startX, e.clientY - startY);
          btn.style.transform = "";
          const cr = circle.getBoundingClientRect();
          const inCircle =
            e.clientX >= cr.left - 35 &&
            e.clientX <= cr.right + 35 &&
            e.clientY >= cr.top - 35 &&
            e.clientY <= cr.bottom + 35;
          if (dist < 14 || inCircle) {
            applyProp(item, btn, cr.left + cr.width / 2, cr.top + cr.height / 2);
          }
        });
      });

      overlayEl.append(circle, row);

      if (autoplay) {
        const seq = autoOutcome === "hazard_fail" ? ["towel", "vinyl"] : ["towel", "blanket", "vinyl"];
        seq.forEach((id, idx) => {
          later(() => {
            if (autoOutcome === "phone_fail" && idx === 1) {
              triggerPhoneNotification(true);
              return;
            }
            const entry = btnMap[id];
            moveGhostToEl(entry.btn, true);
            later(() => {
              const r = entry.btn.getBoundingClientRect();
              applyProp(entry.item, entry.btn, r.left + r.width / 2, r.top + r.height / 2);
            }, 620);
          }, 600 + idx * 1150);
        });
      }
      return;
    }

    // --- Interaction 3: fetch ---
    if (type === "fetch") {
      promptEl.textContent = "按住网球向上甩动抛出";
      const ball = document.createElement("div");
      ball.className = "th-ball-token";
      ball.textContent = "BALL";
      const speaker = document.createElement("button");
      speaker.type = "button";
      speaker.className = "th-corner-hazard";
      speaker.textContent = "BLOWER · 高速吹风筒";
      overlayEl.append(ball, speaker);

      listen(speaker, "click", (e) => {
        e.stopPropagation();
        finish("hazard_fail");
      });

      let dragging = false;
      let startY = 0;
      let startX = 0;
      let startTime = 0;
      let thrown = false;

      const launchBall = () => {
        if (thrown) return;
        thrown = true;
        sfx.playTap();
        ball.style.transition = "transform 560ms cubic-bezier(0.22, 1, 0.36, 1), opacity 560ms ease";
        ball.style.transform = "translate(-50%, -44vh) scale(0.28)";
        ball.style.opacity = "0";
        spawnParticles(window.innerWidth / 2, window.innerHeight * 0.45, "gold", 14);
        promptEl.textContent = "布鲁斯去找球了…专心等它叼回来";
        if (!autoplay || autoOutcome === "phone_fail") {
          later(() => triggerPhoneNotification(autoplay && autoOutcome === "phone_fail"), 850);
        }
        if (!autoplay || autoOutcome === "win") {
          later(() => finish("win"), 3000);
        }
      };

      listen(ball, "pointerdown", (e) => {
        if (autoplay || thrown) return;
        e.stopPropagation();
        dragging = true;
        startX = e.clientX;
        startY = e.clientY;
        startTime = performance.now();
        ball.style.transition = "none";
      });
      listen(window, "pointermove", (e) => {
        if (!dragging || thrown) return;
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        ball.style.transform = `translate(calc(-50% + ${dx}px), ${dy}px)`;
      });
      listen(window, "pointerup", (e) => {
        if (!dragging || thrown) return;
        dragging = false;
        const dy = e.clientY - startY;
        const dt = Math.max(16, performance.now() - startTime);
        const velUp = -dy / dt;
        if (velUp > 0.6 || dy < -95) {
          launchBall();
        } else {
          ball.style.transition = "transform 280ms ease";
          ball.style.transform = "translate(-50%, 0)";
          promptEl.textContent = "再用力往上甩一点！";
        }
      });

      if (autoplay) {
        later(() => {
          if (autoOutcome === "hazard_fail") {
            moveGhostToEl(speaker, true);
            later(() => finish("hazard_fail"), 650);
            return;
          }
          moveGhostToEl(ball, false);
          later(() => {
            moveGhostTo(50, 32, false);
            launchBall();
          }, 550);
        }, 500);
      }
      return;
    }

    // --- Interaction 4: cafeDoors ---
    if (type === "cafeDoors") {
      mediaLayer.setSlowmo(true);
      promptEl.textContent = "看清门贴，选一家进去";
      const row = document.createElement("div");
      row.className = "th-doors-row";

      const doors = shuffle([
        { ok: true, cls: "is-welcome", title: "PAWS WELCOME", sub: "WATER & BISCUITS INSIDE" },
        { ok: false, cls: "is-nodogs", title: "NO DOGS", sub: "NO PETS ALLOWED" },
      ]);

      let welcomeBtn = null;
      let noDogsBtn = null;
      doors.forEach((d) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = `th-door-sign ${d.cls}`;
        btn.innerHTML = `<strong>${d.title}</strong><span>${d.sub}</span>`;
        if (d.ok) welcomeBtn = btn;
        else noDogsBtn = btn;
        listen(btn, "click", (e) => {
          e.stopPropagation();
          sfx.playTap();
          finish(d.ok ? "win" : "hazard_fail");
        });
        row.appendChild(btn);
      });
      overlayEl.appendChild(row);

      later(() => {
        promptEl.classList.add("is-pulse");
        promptEl.textContent = "看清门贴再决定：选绿色欢迎狗狗那家";
      }, 8000);

      if (autoplay) {
        later(() => {
          if (autoOutcome === "phone_fail") {
            triggerPhoneNotification(true);
            return;
          }
          const target = autoOutcome === "hazard_fail" ? noDogsBtn : welcomeBtn;
          moveGhostToEl(target, true);
          later(() => finish(autoOutcome === "hazard_fail" ? "hazard_fail" : "win"), 700);
        }, 900);
      }
      return;
    }

    // --- Interaction 5: lanterns ---
    if (type === "lanterns") {
      promptEl.textContent = "按 1 → 2 → 3 顺序点亮三盏岸灯，躲开噪音红圈";
      let nextIdx = 0;
      const dots = [25, 50, 75].map((xPct, idx) => {
        const dot = document.createElement("button");
        dot.type = "button";
        dot.className = "th-lantern-dot";
        dot.style.left = `${xPct}%`;
        dot.textContent = String(idx + 1);
        listen(dot, "click", (e) => {
          e.stopPropagation();
          if (finished || dot.classList.contains("is-lit")) return;
          if (idx !== nextIdx) {
            promptEl.textContent = `请先点亮第 ${nextIdx + 1} 盏灯`;
            return;
          }
          dot.classList.add("is-lit");
          nextIdx += 1;
          sfx.playTap();
          const r = dot.getBoundingClientRect();
          spawnParticles(r.left + r.width / 2, r.top + r.height / 2, "gold", 16);
          if (nextIdx >= 3) {
            later(() => finish("win"), 450);
          }
        });
        overlayEl.appendChild(dot);
        return dot;
      });

      let activeNoise = null;
      const spawnNoise = () => {
        if (finished) return;
        const noise = document.createElement("button");
        noise.type = "button";
        noise.className = "th-noise-circle";
        noise.style.left = `${22 + Math.random() * 56}%`;
        noise.style.top = `${56 + Math.random() * 20}%`;
        noise.textContent = Math.random() < 0.5 ? "LOUD SPEAKER" : "MOTORBIKE";
        listen(noise, "click", (e) => {
          e.stopPropagation();
          finish("hazard_fail");
        });
        overlayEl.appendChild(noise);
        activeNoise = noise;
        later(() => {
          noise.remove();
          if (activeNoise === noise) activeNoise = null;
        }, 1500);
        later(spawnNoise, 2200);
      };
      later(spawnNoise, 1100);

      if (autoplay) {
        dots.forEach((dot, idx) => {
          later(() => {
            if (autoOutcome === "phone_fail" && idx === 1) {
              triggerPhoneNotification(true);
              return;
            }
            if (autoOutcome === "hazard_fail" && idx === 1 && activeNoise) {
              moveGhostToEl(activeNoise, true);
              later(() => finish("hazard_fail"), 620);
              return;
            }
            moveGhostToEl(dot, true);
            later(() => {
              dot.click();
            }, 600);
          }, 550 + idx * 1050);
        });
      }
      return;
    }

    later(() => finish("win"), 1200);
  });

  promise.cancel = cleanupAll;
  return promise;
}
