/** An opt-in procedural sound bed. No remote audio and no autoplay violation. */
export function createSound() {
  let context,
    master,
    rain,
    purr,
    nextNote = 0,
    noteIndex = 0,
    enabled = false,
    disposed = false;
  const sources = [];
  async function toggle() {
    if (disposed) return false;
    if (!context) {
      const Audio = window.AudioContext || window.webkitAudioContext;
      if (!Audio) return false;
      context = new Audio();
      master = context.createGain();
      master.gain.value = 0;
      master.connect(context.destination);
      const buffer = context.createBuffer(1, context.sampleRate * 3, context.sampleRate),
        data = buffer.getChannelData(0);
      let sample = 0;
      for (let i = 0; i < data.length; i++) {
        sample = (sample + (Math.random() * 2 - 1) * 0.025) / 1.025;
        data[i] = sample * 3;
      }
      const source = context.createBufferSource();
      source.buffer = buffer;
      source.loop = true;
      const filter = context.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.value = 1500;
      rain = context.createGain();
      rain.gain.value = 0;
      source.connect(filter).connect(rain).connect(master);
      source.start();
      sources.push(source);
      const osc = context.createOscillator();
      osc.type = 'sine';
      osc.frequency.value = 29;
      purr = context.createGain();
      purr.gain.value = 0;
      osc.connect(purr).connect(master);
      osc.start();
      sources.push(osc);
    }
    enabled = !enabled;
    try {
      await context.resume();
      if (disposed || !context) return false;
      master.gain.setTargetAtTime(enabled ? 0.35 : 0, context.currentTime, 0.25);
      return enabled;
    } catch {
      enabled = false;
      return false;
    }
  }
  return {
    toggle,
    update(time, { wet = 0, record = 0, petting = 0, cold = 0 } = {}) {
      if (!context || !enabled || context.state !== 'running' || disposed) return;
      rain.gain.setTargetAtTime(wet * 0.15 + cold * 0.09, context.currentTime, 0.2);
      purr.gain.setTargetAtTime(
        petting * (0.025 + Math.sin(time * 2.2) * 0.008),
        context.currentTime,
        0.2,
      );
      if (record && context.currentTime > nextNote) {
        const frequencies = [174.61, 220, 261.63, 329.63, 293.66, 220, 196, 261.63],
          now = context.currentTime;
        const osc = context.createOscillator(),
          gain = context.createGain();
        osc.type = 'sine';
        osc.frequency.value = frequencies[noteIndex++ % frequencies.length];
        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(0.08, now + 0.035);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 1.5);
        osc.connect(gain).connect(master);
        osc.start();
        osc.stop(now + 1.6);
        osc.onended = () => {
          osc.disconnect();
          gain.disconnect();
        };
        nextNote = now + 0.55;
      }
    },
    pause() {
      if (context?.state === 'running') context.suspend().catch(() => {});
    },
    resume() {
      if (enabled && !disposed) context?.resume().catch(() => {});
    },
    destroy() {
      disposed = true;
      enabled = false;
      sources.forEach((s) => {
        try {
          s.stop();
          s.disconnect();
        } catch {
          /* already ended */
        }
      });
      if (context) {
        master.disconnect();
        context.close();
      }
      context = null;
    },
  };
}
