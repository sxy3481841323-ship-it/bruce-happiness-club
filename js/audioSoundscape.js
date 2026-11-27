export function createSoundscapeController(ensureCtxFn, isMutedFn) {
  const noiseCache = new WeakMap();
  let ctx = null;
  let master = null;
  let desiredScene = "none";
  let desiredOpts = { floor: "1f", sulking: false };
  let hifiOn = false;
  let vinylMode = false;
  let sceneNodes = null;
  let sceneTimers = [];
  let hifiNodes = null;
  let hifiTimer = null;
  let vinylTimer = null;
  let stopped = false;

  const now = () => (ctx ? ctx.currentTime : 0);
  const safe = (fn) => { try { return fn(); } catch (e) { return null; } };

  function _ensureNoiseBuffers(c) {
    let cached = noiseCache.get(c);
    if (cached) return cached;
    const len = Math.floor(c.sampleRate * 2);
    const mk = (fill) => {
      const b = c.createBuffer(1, len, c.sampleRate);
      const d = b.getChannelData(0);
      fill(d);
      return b;
    };
    const white = mk((d) => { for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1; });
    const pink = mk((d) => {
      let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
      for (let i = 0; i < len; i++) {
        const w = Math.random() * 2 - 1;
        b0 = 0.99886 * b0 + w * 0.0555179;
        b1 = 0.99332 * b1 + w * 0.0750759;
        b2 = 0.96900 * b2 + w * 0.1538520;
        b3 = 0.86650 * b3 + w * 0.3104856;
        b4 = 0.55000 * b4 + w * 0.5329522;
        b5 = -0.7616 * b5 - w * 0.0168980;
        d[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + w * 0.5362) * 0.11;
        b6 = w * 0.115926;
      }
    });
    const brown = mk((d) => {
      let last = 0;
      for (let i = 0; i < len; i++) {
        const w = Math.random() * 2 - 1;
        last = (last + 0.02 * w) / 1.02;
        d[i] = last * 3.5;
      }
    });
    cached = { white, pink, brown };
    noiseCache.set(c, cached);
    return cached;
  }

  function _ensureCtx() {
    if (stopped) return null;
    if (!ctx) {
      const c = safe(ensureCtxFn);
      if (!c) return null;
      ctx = c;
      master = ctx.createGain();
      master.gain.value = 0.0001;
      master.connect(ctx.destination);
      _ensureNoiseBuffers(ctx);
    }
    if (ctx.state === "suspended") safe(() => ctx.resume());
    return ctx;
  }

  function _ramp(param, val, t = 0.22) {
    if (!param) return;
    safe(() => {
      const n = now();
      param.cancelScheduledValues(n);
      param.setValueAtTime(Math.max(0.0001, param.value || 0.0001), n);
      param.linearRampToValueAtTime(Math.max(0.0001, val), n + t);
    });
  }

  function playNoiseBurst(type, freq, q, dur, gain, filterType = "bandpass") {
    if (isMutedFn()) return;
    const c = _ensureCtx();
    if (!c) return;
    const buf = _ensureNoiseBuffers(c)[type];
    const src = c.createBufferSource();
    src.buffer = buf;
    src.loop = true;
    const f = c.createBiquadFilter();
    f.type = filterType;
    f.frequency.value = freq;
    f.Q.value = q;
    const g = c.createGain();
    const t = now();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.linearRampToValueAtTime(gain, t + 0.004);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    src.connect(f).connect(g).connect(master);
    src.start(t);
    src.stop(t + dur + 0.02);
  }

  function playTone(freq, dur, gain, type = "sine", dest = null, glideTo = null) {
    if (isMutedFn()) return;
    const c = _ensureCtx();
    if (!c) return;
    const o = c.createOscillator();
    o.type = type;
    const g = c.createGain();
    const t = now();
    o.frequency.setValueAtTime(freq, t);
    if (glideTo) o.frequency.exponentialRampToValueAtTime(glideTo, t + dur * 0.6);
    g.gain.setValueAtTime(0.0001, t);
    g.gain.linearRampToValueAtTime(gain, t + 0.01);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g).connect(dest || master);
    o.start(t);
    o.stop(t + dur + 0.02);
  }

  function _clearTimers(arr) {
    arr.forEach((id) => {
      clearTimeout(id);
      clearInterval(id);
    });
    arr.length = 0;
  }

  function _stopScene() {
    _clearTimers(sceneTimers);
    const prev = sceneNodes;
    sceneNodes = null;
    if (prev) {
      safe(() => {
        const t = now();
        prev.gain.gain.cancelScheduledValues(t);
        prev.gain.gain.setValueAtTime(Math.max(0.0001, prev.gain.gain.value), t);
        prev.gain.gain.linearRampToValueAtTime(0.0001, t + 0.22);
        setTimeout(() => safe(() => {
          prev.sources.forEach((s) => { try { s.stop(); } catch (e) {} });
          prev.gain.disconnect();
        }), 300);
      });
    }
  }

  function _stopHifi() {
    if (hifiTimer) { clearTimeout(hifiTimer); hifiTimer = null; }
    const prev = hifiNodes;
    hifiNodes = null;
    if (prev) {
      safe(() => {
        const t = now();
        prev.gain.gain.cancelScheduledValues(t);
        prev.gain.gain.setValueAtTime(Math.max(0.0001, prev.gain.gain.value), t);
        prev.gain.gain.linearRampToValueAtTime(0.0001, t + 0.6);
        setTimeout(() => safe(() => prev.gain.disconnect()), 700);
      });
    }
  }

  function _stopVinyl() {
    if (vinylTimer) { clearTimeout(vinylTimer); vinylTimer = null; }
  }

  function _hearthMul() {
    let m = desiredOpts.floor === "2f" ? 0.35 : 1.0;
    if (desiredOpts.sulking) m *= 0.6;
    return m;
  }

  function _startPenthouse() {
    const c = _ensureCtx();
    if (!c) return;
    const buf = _ensureNoiseBuffers(c);
    const gain = c.createGain();
    gain.gain.value = 0.0001;
    gain.connect(master);
    const rumble = c.createBufferSource();
    rumble.buffer = buf.brown;
    rumble.loop = true;
    const lp = c.createBiquadFilter();
    lp.type = "lowpass";
    lp.frequency.value = 115;
    lp.Q.value = 0.7;
    const rg = c.createGain();
    rg.gain.value = 0.09 * _hearthMul();
    rumble.connect(lp).connect(rg).connect(gain);
    rumble.start();
    const air = c.createBufferSource();
    air.buffer = buf.pink;
    air.loop = true;
    const bp = c.createBiquadFilter();
    bp.type = "bandpass";
    bp.frequency.value = 420;
    bp.Q.value = 0.6;
    const ag = c.createGain();
    ag.gain.value = 0.02 * _hearthMul();
    air.connect(bp).connect(ag).connect(gain);
    air.start();
    sceneNodes = { gain, sources: [rumble, air], hearthGain: rg, airGain: ag };
    _ramp(gain.gain, 0.14, 0.6);
    const crackle = () => {
      if (desiredScene !== "penthouse" || isMutedFn()) return;
      const f = 1300 + Math.random() * 1900;
      const dur = 0.010 + Math.random() * 0.016;
      playNoiseBurst("pink", f, 3.5, dur, 0.012 * _hearthMul());
      sceneTimers.push(setTimeout(crackle, 220 + Math.random() * 700));
    };
    sceneTimers.push(setTimeout(crackle, 400));
  }

  function _startCafe() {
    const c = _ensureCtx();
    if (!c) return;
    const buf = _ensureNoiseBuffers(c);
    const gain = c.createGain();
    gain.gain.value = 0.0001;
    gain.connect(master);
    const surf = c.createBufferSource();
    surf.buffer = buf.pink;
    surf.loop = true;
    const bp = c.createBiquadFilter();
    bp.type = "bandpass";
    bp.frequency.value = 180;
    bp.Q.value = 0.9;
    const sg = c.createGain();
    sg.gain.value = 0.11;
    surf.connect(bp).connect(sg).connect(gain);
    surf.start();
    const breeze = c.createBufferSource();
    breeze.buffer = buf.white;
    breeze.loop = true;
    const hp = c.createBiquadFilter();
    hp.type = "highpass";
    hp.frequency.value = 2400;
    const bg = c.createGain();
    bg.gain.value = 0.012;
    breeze.connect(hp).connect(bg).connect(gain);
    breeze.start();
    sceneNodes = { gain, sources: [surf, breeze], sweepFilter: bp };
    _ramp(gain.gain, 0.13, 0.8);
    let up = true;
    const sweep = () => {
      if (desiredScene !== "cafe") return;
      const t = now();
      safe(() => bp.frequency.setTargetAtTime(up ? 740 : 180, t, 1.4));
      up = !up;
    };
    sceneTimers.push(setInterval(sweep, 4200));
  }

  function _startWarehouse() {
    const c = _ensureCtx();
    if (!c) return;
    const buf = _ensureNoiseBuffers(c);
    const gain = c.createGain();
    gain.gain.value = 0.0001;
    gain.connect(master);
    const air = c.createBufferSource();
    air.buffer = buf.pink;
    air.loop = true;
    const bp = c.createBiquadFilter();
    bp.type = "bandpass";
    bp.frequency.value = 900;
    bp.Q.value = 0.4;
    const ag = c.createGain();
    ag.gain.value = 0.035;
    air.connect(bp).connect(ag).connect(gain);
    air.start();
    sceneNodes = { gain, sources: [air] };
    _ramp(gain.gain, 0.10, 0.9);
    const overtone = () => {
      if (desiredScene !== "warehouse" || isMutedFn()) return;
      const f = Math.random() < 0.5 ? 660 : 990;
      playTone(f, 1.4, 0.008, "sine");
      sceneTimers.push(setTimeout(overtone, 4000 + Math.random() * 3000));
    };
    sceneTimers.push(setTimeout(overtone, 3000));
  }

  function _startHifi() {
    const c = _ensureCtx();
    if (!c || desiredScene !== "penthouse" || isMutedFn()) return;
    if (hifiNodes) return;
    const gain = c.createGain();
    gain.gain.value = 0.0001;
    gain.connect(master);
    hifiNodes = { gain };
    _ramp(gain.gain, 0.045, 1.2);
    const chords = [
      [174.61, 261.63, 329.63, 392.00],
      [164.81, 246.94, 329.63, 392.00],
      [146.83, 220.00, 293.66, 349.23],
      [130.81, 196.00, 261.63, 329.63]
    ];
    let idx = 0;
    const playChord = () => {
      if (!hifiOn || desiredScene !== "penthouse" || isMutedFn() || !hifiNodes) return;
      const notes = chords[idx % chords.length];
      idx++;
      const t = now();
      notes.forEach((f, i) => {
        const o = c.createOscillator();
        o.type = i === 0 ? "sine" : "triangle";
        o.frequency.value = f;
        const lp = c.createBiquadFilter();
        lp.type = "lowpass";
        lp.frequency.value = 1400;
        const g = c.createGain();
        g.gain.setValueAtTime(0.0001, t);
        g.gain.linearRampToValueAtTime(0.012, t + 0.4);
        g.gain.exponentialRampToValueAtTime(0.0001, t + 3.4);
        o.connect(lp).connect(g).connect(hifiNodes.gain);
        o.start(t);
        o.stop(t + 3.6);
      });
      hifiTimer = setTimeout(playChord, 3750);
    };
    playChord();
    if (vinylMode) _startVinyl();
  }

  function _startVinyl() {
    if (!ctx || !hifiNodes) return;
    if (vinylTimer) return;
    const crackle = () => {
      if (!vinylMode || !hifiOn || isMutedFn()) return;
      playNoiseBurst("white", 1800 + Math.random() * 2200, 4, 0.008 + Math.random() * 0.01, 0.006);
      vinylTimer = setTimeout(crackle, 90 + Math.random() * 260);
    };
    crackle();
  }

  function _applyScene() {
    if (stopped) return;
    _stopScene();
    _stopHifi();
    _stopVinyl();
    if (isMutedFn()) return;
    const c = _ensureCtx();
    if (!c) return;
    _ramp(master.gain, 0.16, 0.35);
    if (desiredScene === "penthouse") {
      _startPenthouse();
      if (hifiOn) _startHifi();
    } else if (desiredScene === "cafe") {
      _startCafe();
    } else if (desiredScene === "warehouse") {
      _startWarehouse();
    }
  }

  return {
    setSceneAmbience(sceneId, opts = {}) {
      desiredScene = sceneId || "none";
      desiredOpts = { floor: opts.floor || "1f", sulking: Boolean(opts.sulking) };
      _applyScene();
    },
    clearSceneAmbience(expectedSceneId) {
      if (desiredScene !== expectedSceneId) return;
      desiredScene = "none";
      _stopScene();
      _stopHifi();
      _stopVinyl();
    },
    setFloor(floorId) {
      desiredOpts.floor = floorId === "2f" ? "2f" : "1f";
      if (sceneNodes && sceneNodes.hearthGain) {
        safe(() => sceneNodes.hearthGain.gain.setTargetAtTime(0.09 * _hearthMul(), now(), 0.4));
        safe(() => sceneNodes.airGain.gain.setTargetAtTime(0.02 * _hearthMul(), now(), 0.4));
      }
    },
    toggleHifi(forceBool) {
      hifiOn = typeof forceBool === "boolean" ? forceBool : !hifiOn;
      if (hifiOn && desiredScene === "penthouse" && !isMutedFn()) _startHifi();
      else if (!hifiOn) { _stopHifi(); _stopVinyl(); }
      return hifiOn;
    },
    isHifiOn() { return hifiOn; },
    setVinylMode(active) {
      vinylMode = Boolean(active);
      if (vinylMode) {
        hifiOn = true;
        if (desiredScene === "penthouse" && !isMutedFn()) { _startHifi(); _startVinyl(); }
      } else {
        _stopVinyl();
      }
    },
    stokeFireplace() {
      if (!ctx || isMutedFn()) return;
      for (let i = 0; i < 3; i++) {
        setTimeout(() => {
          playNoiseBurst("pink", 1400 + Math.random() * 1600, 3, 0.02 + Math.random() * 0.01, 0.02 * _hearthMul());
          playNoiseBurst("brown", 200, 1.2, 0.18, 0.015 * _hearthMul(), "lowpass");
        }, i * 90);
      }
    },
    playConciergeBell() {
      playTone(880, 0.55, 0.05, "sine");
      setTimeout(() => playTone(1318.5, 0.55, 0.045, "sine"), 140);
      setTimeout(() => playTone(1760, 0.4, 0.015, "sine"), 150);
    },
    playGlassPour() {
      playTone(2349, 0.18, 0.03, "sine");
      setTimeout(() => playTone(2793, 0.22, 0.025, "sine"), 40);
      if (!ctx || isMutedFn()) return;
      const buf = _ensureNoiseBuffers(ctx);
      const src = ctx.createBufferSource();
      src.buffer = buf.white;
      src.loop = true;
      const bp = ctx.createBiquadFilter();
      bp.type = "bandpass";
      bp.frequency.value = 4200;
      bp.Q.value = 1.2;
      const g = ctx.createGain();
      const t = now();
      g.gain.setValueAtTime(0.0001, t);
      g.gain.linearRampToValueAtTime(0.02, t + 0.05);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.62);
      src.connect(bp).connect(g).connect(master);
      src.start(t);
      src.stop(t + 0.65);
    },
    playVinylDrop() {
      playTone(112, 0.18, 0.04, "sine", null, 62);
      playNoiseBurst("brown", 400, 1.5, 0.25, 0.02, "lowpass");
    },
    playChauffeurReady() {
      if (isMutedFn()) return;
      const c = _ensureCtx();
      if (!c) return;
      _ramp(master.gain, 0.16, 0.15);
      const lp = c.createBiquadFilter();
      lp.type = "lowpass";
      lp.frequency.value = 900;
      lp.connect(master);
      playTone(329.63, 0.35, 0.04, "triangle", lp);
      setTimeout(() => playTone(440, 0.45, 0.04, "triangle", lp), 180);
    },
    syncMute(muted) {
      if (!master) { if (!muted) _applyScene(); return; }
      if (muted) {
        _ramp(master.gain, 0.0001, 0.3);
        _stopHifi();
        _stopVinyl();
      } else {
        _ramp(master.gain, 0.16, 0.4);
        _applyScene();
      }
    },
    unlock() {
      const c = _ensureCtx();
      if (!c) return;
      if (!isMutedFn()) _ramp(master.gain, 0.16, 0.4);
      if (desiredScene !== "none" && !sceneNodes) _applyScene();
      else if (hifiOn && desiredScene === "penthouse" && !hifiNodes) _startHifi();
    },
    stopAll() {
      stopped = true;
      _stopScene();
      _stopHifi();
      _stopVinyl();
      if (master) {
        _ramp(master.gain, 0.0001, 0.2);
        setTimeout(() => safe(() => master.disconnect()), 300);
      }
      if (ctx) safe(() => ctx.suspend());
    }
  };
}
