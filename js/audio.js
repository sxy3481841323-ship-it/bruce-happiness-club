// Procedural Web Audio sound effects (no external audio files required)

class SoundEngine {
  constructor() {
    this.ctx = null;
    this.muted = false;
  }

  _ensureCtx() {
    if (this.muted) return null;
    if (!this.ctx && typeof window !== "undefined") {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (AC) this.ctx = new AC();
    }
    if (this.ctx && this.ctx.state === "suspended") {
      this.ctx.resume().catch(() => {});
    }
    return this.ctx;
  }

  toggleMute() {
    this.muted = !this.muted;
    return this.muted;
  }

  _tone(freq, dur, type = "sine", gainVal = 0.08, delay = 0) {
    const ctx = this._ensureCtx();
    if (!ctx) return;
    const now = ctx.currentTime + delay;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, now);
    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.exponentialRampToValueAtTime(gainVal, now + 0.015);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + dur);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + dur + 0.02);
  }

  playTap() {
    this._tone(520, 0.07, "triangle", 0.05);
  }

  playSuccess() {
    this._tone(523.25, 0.14, "triangle", 0.08, 0);
    this._tone(659.25, 0.16, "triangle", 0.08, 0.07);
    this._tone(783.99, 0.24, "sine", 0.09, 0.14);
  }

  playFail() {
    this._tone(310, 0.16, "sawtooth", 0.05, 0);
    this._tone(215, 0.28, "triangle", 0.07, 0.11);
  }

  playPhoneBuzz() {
    this._tone(740, 0.06, "square", 0.03, 0);
    this._tone(740, 0.06, "square", 0.03, 0.09);
  }

  playSwapCelebration() {
    [523.25, 659.25, 783.99, 1046.5].forEach((f, idx) => {
      this._tone(f, 0.25, "triangle", 0.08, idx * 0.08);
    });
  }

  playElevatorChime() {
    this._tone(783.99, 0.28, "sine", 0.06, 0);
    this._tone(1567.98, 0.22, "triangle", 0.02, 0);
    this._tone(659.25, 0.42, "sine", 0.065, 0.19);
    this._tone(1318.5, 0.34, "triangle", 0.02, 0.19);
  }

  playDoorPaws() {
    [172, 198, 165, 206].forEach((f, idx) => {
      this._tone(f, 0.055, "triangle", 0.036, idx * 0.095);
    });
  }

  playDoorUnlock() {
    this._tone(920, 0.045, "triangle", 0.05, 0);
    this._tone(420, 0.06, "triangle", 0.045, 0.045);
    [523.25, 659.25, 783.99, 987.77].forEach((f, idx) => {
      this._tone(f, 0.36, "sine", 0.055, 0.12 + idx * 0.045);
    });
  }

  playPawStep(soft = false) {
    const pitch = soft ? 162 + Math.random() * 28 : 185 + Math.random() * 30;
    this._tone(pitch, 0.048, "triangle", soft ? 0.022 : 0.032, 0);
  }

  playRollJoy() {
    this._tone(440, 0.1, "sine", 0.045, 0);
    this._tone(554.37, 0.12, "triangle", 0.05, 0.09);
    this._tone(659.25, 0.16, "sine", 0.05, 0.18);
  }

  playStretchSigh() {
    this._tone(392, 0.16, "sine", 0.04, 0);
    this._tone(523.25, 0.24, "sine", 0.04, 0.1);
  }
}

export const sfx = new SoundEngine();
