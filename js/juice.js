import { sfx } from "./audio.js";

let trauma = 0;
let rafRunning = false;
let tPhase = 0;

function stepShake() {
  const stage = document.getElementById("stage-wrap");
  if (!stage || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    trauma = 0;
    rafRunning = false;
    if (stage) stage.style.transform = "";
    return;
  }
  trauma = Math.max(0, trauma - 0.045);
  if (trauma <= 0) {
    stage.style.transform = "";
    rafRunning = false;
    return;
  }
  tPhase += 0.55;
  const mag = trauma * trauma * 11;
  const dx = mag * Math.sin(tPhase * 1.7);
  const dy = mag * Math.cos(tPhase * 2.3);
  stage.style.transform = `translate3d(${dx.toFixed(2)}px, ${dy.toFixed(2)}px, 0)`;
  requestAnimationFrame(stepShake);
}

export function addTrauma(amount) {
  trauma = Math.min(1, trauma + amount);
  if (!rafRunning) {
    rafRunning = true;
    requestAnimationFrame(stepShake);
  }
}

export function spawnFloatNumber(text, x, y, positive = true) {
  const layer = document.getElementById("fx-layer");
  if (!layer) return;
  const el = document.createElement("div");
  el.className = `fx-float-num ${positive ? "pos" : "neg"}`;
  el.textContent = text;
  el.style.left = `${x}px`;
  el.style.top = `${y}px`;
  layer.appendChild(el);
  setTimeout(() => el.remove(), 920);
}

export function spawnParticles(x, y, count = 10, palette = ["#7F2334", "#C88D3B", "#3A5A46"]) {
  const layer = document.getElementById("fx-layer");
  if (!layer || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  for (let i = 0; i < count; i += 1) {
    const p = document.createElement("span");
    p.className = "fx-particle";
    const angle = (Math.PI * 2 * i) / count + (Math.random() - 0.5) * 0.4;
    const dist = 26 + Math.random() * 48;
    p.style.left = `${x}px`;
    p.style.top = `${y}px`;
    p.style.background = palette[i % palette.length];
    p.style.setProperty("--dx", `${Math.cos(angle) * dist}px`);
    p.style.setProperty("--dy", `${Math.sin(angle) * dist}px`);
    layer.appendChild(p);
    setTimeout(() => p.remove(), 660);
  }
}

export function feedback(tier, x = window.innerWidth / 2, y = window.innerHeight * 0.35, deltaText = "") {
  if (tier === "small") {
    sfx.playTap();
    spawnParticles(x, y, 4);
  } else if (tier === "win") {
    sfx.playSuccess();
    addTrauma(0.22);
    spawnParticles(x, y, 14, ["#3A5A46", "#C88D3B", "#7F2334"]);
    if (deltaText) spawnFloatNumber(deltaText, x, y, true);
  } else if (tier === "fail") {
    sfx.playFail();
    addTrauma(0.65);
    spawnParticles(x, y, 12, ["#B4382A", "#1B1917"]);
    if (deltaText) spawnFloatNumber(deltaText, x, y, false);
  } else if (tier === "swap") {
    sfx.playSwapCelebration();
    addTrauma(0.45);
    spawnParticles(x, y, 22, ["#7F2334", "#C88D3B", "#3A5A46"]);
  }
}
