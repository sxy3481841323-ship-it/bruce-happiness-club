// Procedural Web Audio sound effects & spatial soundscapes (zero external audio files)
import { createSoundscapeController } from "./audioSoundscape.js";

class SoundEngine {
  constructor() {
    this.ctx = null;
    this.muted = false;
    this._gestureBound = false;
    this.soundscape = createSoundscapeController(
      () => this._ensureCtx(),
      () => this.muted,
    );
    this._bindGestureUnlock();
  }

  _bindGestureUnlock() {
    if (this._gestureBound || typeof window === "undefined") return;
    this._gestureBound = true;
    const unlock = () => {
      if (this.muted) return;
      const c = this._ensureCtx();
      if (c) {
        this.soundscape.unlock();
      }
    };
    window.addEventListener("pointerdown", unlock, { passive: true });
    window.addEventListener("keydown", unlock, { passive: true });
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
    this.soundscape.syncMute(this.muted);
    return this.muted;
  }

  setSceneAmbience(sceneId, opts = {}) {
    this.soundscape.setSceneAmbience(sceneId, opts);
  }

  clearSceneAmbience(expectedSceneId) {
    this.soundscape.clearSceneAmbience(expectedSceneId);
  }

  setFloorAmbience(floorId) {
    this.soundscape.setFloor(floorId);
  }

  setTvChannel(channelId) {
    return this.soundscape.setTvChannel(channelId);
  }

  getTvChannel() {
    return this.soundscape.getTvChannel();
  }

  toggleHifi(forceBool) {
    return this.soundscape.toggleHifi(forceBool);
  }

  isHifiOn() {
    return this.soundscape.isHifiOn();
  }

  setVinylMode(active) {
    this.soundscape.setVinylMode(active);
  }

  stokeFireplace() {
    this.soundscape.stokeFireplace();
  }

  playConciergeBell() {
    this.soundscape.playConciergeBell();
  }

  playGlassPour() {
    this.soundscape.playGlassPour();
  }

  playVinylDrop() {
    this.soundscape.playVinylDrop();
  }

  playChauffeurReady() {
    this.soundscape.playChauffeurReady();
  }

  _uiBus(ctx) {
    if (!this._bus && ctx) {
      const lp = ctx.createBiquadFilter();
      lp.type = "lowpass";
      lp.frequency.value = 1050;
      lp.Q.value = 0.7;
      const g = ctx.createGain();
      g.gain.value = 0.55;
      lp.connect(g).connect(ctx.destination);
      this._bus = lp;
      this._busNoise = null;
    }
    return this._bus || ctx.destination;
  }

  _tone(freq, dur, type = "sine", gainVal = 0.045, delay = 0) {
    const ctx = this._ensureCtx();
    if (!ctx) return;
    const bus = this._uiBus(ctx);
    const now = ctx.currentTime + delay;
    const safeType = type === "sawtooth" || type === "square" ? "sine" : type;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = safeType;
    osc.frequency.setValueAtTime(Math.min(freq, 760), now);
    gain.gain.setValueAtTime(0.001, now);
    gain.gain.linearRampToValueAtTime(gainVal, now + Math.min(0.022, dur * 0.25));
    gain.gain.exponentialRampToValueAtTime(0.001, now + Math.max(0.04, dur));
    osc.connect(gain);
    gain.connect(bus);
    osc.start(now);
    osc.stop(now + dur + 0.03);
  }

  playTap() {
    const ctx = this._ensureCtx();
    if (!ctx) return;
    const bus = this._uiBus(ctx);
    const now = ctx.currentTime;
    // Soft organic wooden/leather micro-thock instead of piercing piezo click
    const osc = ctx.createOscillator();
    const g = ctx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(195, now);
    osc.frequency.exponentialRampToValueAtTime(108, now + 0.026);
    g.gain.setValueAtTime(0.001, now);
    g.gain.linearRampToValueAtTime(0.028, now + 0.004);
    g.gain.exponentialRampToValueAtTime(0.001, now + 0.036);
    osc.connect(g).connect(bus);
    osc.start(now);
    osc.stop(now + 0.045);
  }

  playSuccess() {
    this._tone(261.63, 0.18, "sine", 0.045, 0);
    this._tone(329.63, 0.22, "sine", 0.045, 0.075);
    this._tone(392.00, 0.30, "sine", 0.050, 0.15);
  }

  playFail() {
    this._tone(196.0, 0.18, "sine", 0.036, 0);
    this._tone(155.56, 0.28, "sine", 0.040, 0.11);
  }

  playPhoneBuzz() {
    this._tone(220.0, 0.075, "sine", 0.024, 0);
    this._tone(220.0, 0.075, "sine", 0.024, 0.11);
  }

  playSwapCelebration() {
    [261.63, 329.63, 392.00, 493.88].forEach((f, idx) => {
      this._tone(f, 0.32, "sine", 0.045, idx * 0.085);
    });
  }

  playElevatorChime() {
    this._tone(392.00, 0.34, "sine", 0.042, 0);
    this._tone(329.63, 0.46, "sine", 0.045, 0.20);
  }

  playDoorPaws() {
    [138, 158, 132, 162].forEach((f, idx) => {
      this._tone(f, 0.055, "sine", 0.028, idx * 0.095);
    });
  }

  playDoorUnlock() {
    this._tone(310, 0.05, "sine", 0.032, 0);
    this._tone(220, 0.07, "sine", 0.030, 0.05);
    [261.63, 329.63, 392.00, 493.88].forEach((f, idx) => {
      this._tone(f, 0.40, "sine", 0.040, 0.12 + idx * 0.05);
    });
  }

  playPawStep(soft = false) {
    const pitch = soft ? 128 + Math.random() * 20 : 146 + Math.random() * 24;
    this._tone(pitch, 0.048, "sine", soft ? 0.018 : 0.025, 0);
  }

  playRollJoy() {
    this._tone(293.66, 0.13, "sine", 0.034, 0);
    this._tone(349.23, 0.16, "sine", 0.036, 0.09);
    this._tone(440.00, 0.22, "sine", 0.036, 0.18);
  }

  playStretchSigh() {
    this._tone(261.63, 0.18, "sine", 0.030, 0);
    this._tone(329.63, 0.28, "sine", 0.030, 0.11);
  }

  playPianoNocturne() {
    // Felt-hammered Db-major9 grand piano arpeggio with warm 2nd harmonic
    const notes = [277.18, 349.23, 415.30, 523.25, 622.25, 830.61];
    notes.forEach((freq, i) => {
      const delay = i * 0.14;
      this._tone(freq, 0.85, "sine", 0.038, delay);
      this._tone(Math.min(freq * 2, 1100), 0.45, "triangle", 0.010, delay);
    });
  }

  playGolfPutt() {
    // Soft club strike followed by hollow stainless cup drop
    this._tone(168, 0.07, "sine", 0.036, 0);
    this._tone(420, 0.09, "triangle", 0.018, 0.85);
    this._tone(580, 0.14, "sine", 0.022, 0.92);
  }
}

export const sfx = new SoundEngine();
