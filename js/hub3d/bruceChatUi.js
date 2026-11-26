import { apiAskBruce } from "../api.js";
import { sfx } from "../audio.js";
import { spawnFloatNumber } from "../juice.js";

const QUICK_PROMPTS = [
  "布鲁斯翻个肚皮求摸摸",
  "走过来吃三文鱼冻干啦",
  "对不起刚刚看手机了别生气",
];

/**
 * Shared floating DeepSeek AI chat bar for 3D Living Room & Coastal Café.
 * Drives Bruce's cinema subtitle + 86-bone skeletal action + sincerity delta.
 */
export function mountBruceChatBar({ stageEl, toggleBtn, getContext, onAiResponse }) {
  if (!stageEl || !toggleBtn) return () => {};

  const pop = document.createElement("div");
  pop.className = "hub3d-chat-popover";
  pop.setAttribute("aria-hidden", "true");
  pop.innerHTML = `
    <div class="chat-chips-row">
      ${QUICK_PROMPTS.map(
        (q) => `<button type="button" class="chat-chip" data-q="${q}">${q}</button>`,
      ).join("")}
    </div>
    <form class="chat-input-row">
      <input type="text" class="chat-input" maxlength="40" placeholder="跟布鲁斯说句话（夸它/喊它/哄它）…" autocomplete="off" />
      <button type="submit" class="chat-send-btn">发送</button>
    </form>
  `;
  stageEl.appendChild(pop);

  const form = pop.querySelector(".chat-input-row");
  const input = pop.querySelector(".chat-input");
  const sendBtn = pop.querySelector(".chat-send-btn");
  let open = false;
  let busy = false;

  const setOpen = (next) => {
    open = Boolean(next);
    pop.classList.toggle("is-open", open);
    pop.setAttribute("aria-hidden", open ? "false" : "true");
    toggleBtn.classList.toggle("is-playing", open);
    if (open) {
      setTimeout(() => input?.focus(), 60);
    }
  };

  const submitMessage = async (rawText) => {
    const msg = String(rawText || "").trim();
    if (!msg || busy) return;
    busy = true;
    sendBtn.disabled = true;
    sendBtn.textContent = "思考中…";
    sfx.playTap();
    try {
      const ctx = getContext?.() || {};
      const res = await apiAskBruce({
        mode: "chat",
        message: msg,
        owner: ctx.owner || "Alex",
        nickname: ctx.nickname || "新邻居",
        happiness: ctx.happiness ?? 100,
        sulking: Boolean(ctx.sulking),
        scene: ctx.scene || "living_room",
      });
      if (input) input.value = "";
      setOpen(false);
      onAiResponse?.(res, (delta) => {
        if (delta) {
          const r = toggleBtn.getBoundingClientRect();
          spawnFloatNumber(`${delta >= 0 ? "+" : ""}${delta}`, r.left + r.width * 0.5, r.top - 12, delta >= 0);
        }
      });
    } finally {
      busy = false;
      sendBtn.disabled = false;
      sendBtn.textContent = "发送";
    }
  };

  const onToggle = (e) => {
    e.stopPropagation();
    sfx.playTap();
    setOpen(!open);
  };

  const onSubmit = (e) => {
    e.preventDefault();
    submitMessage(input?.value);
  };

  const onChipClick = (e) => {
    e.stopPropagation();
    const q = e.currentTarget.getAttribute("data-q");
    if (q) submitMessage(q);
  };

  const onDocClick = (e) => {
    if (open && !pop.contains(e.target) && !toggleBtn.contains(e.target)) {
      setOpen(false);
    }
  };

  const stopBubble = (e) => e.stopPropagation();

  toggleBtn.addEventListener("click", onToggle);
  form?.addEventListener("submit", onSubmit);
  pop.addEventListener("click", stopBubble);
  pop.addEventListener("pointerdown", stopBubble);
  const chips = Array.from(pop.querySelectorAll(".chat-chip"));
  chips.forEach((c) => c.addEventListener("click", onChipClick));
  document.addEventListener("click", onDocClick);

  return () => {
    toggleBtn.removeEventListener("click", onToggle);
    form?.removeEventListener("submit", onSubmit);
    pop.removeEventListener("click", stopBubble);
    pop.removeEventListener("pointerdown", stopBubble);
    chips.forEach((c) => c.removeEventListener("click", onChipClick));
    document.removeEventListener("click", onDocClick);
    pop.remove();
  };
}
