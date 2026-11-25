import * as THREE from 'three';
import { createBruceModel } from './bruceModel.js';
import { createMaterials } from './materials.js';
import { createWorld } from './scenes/world.js';
import { getScene } from './scenes/index.js';
import { createAtmosphere, createLighting, createPostProcess } from './effects.js';
import { createSound } from './sound.js';
import { clamp, damp, disposeTree, ease, lerp, smooth, vec } from './math.js';

const scrollLocks = new WeakMap();
function lockScroll(doc) {
  let lock = scrollLocks.get(doc);
  if (!lock) {
    lock = { count: 0, html: doc.documentElement.style.overflow, body: doc.body.style.overflow };
    scrollLocks.set(doc, lock);
  }
  lock.count++;
  doc.documentElement.style.overflow = doc.body.style.overflow = 'hidden';
  return () => {
    if (--lock.count === 0) {
      doc.documentElement.style.overflow = lock.html;
      doc.body.style.overflow = lock.body;
      scrollLocks.delete(doc);
    }
  };
}

const ACTION_LABELS = {
  brush: '轻轻顺毛',
  dryer: '吹风机',
  towel: '擦干爪子',
  blanket: '披上毛毯',
  vinyl: '播放黑胶',
  ball: '抛出网球',
  speaker: '音箱',
  apple: '选取苹果',
  grapes: '葡萄',
  bowl: 'BRUCE 陶瓷碗',
  curtain: '拉下遮阳帘',
  cushion: '拍松软垫',
  vacuum: '吸尘器',
  welcome: 'PAWS WELCOME',
  noDogs: 'NO DOGS',
  leash: '放松牵引绳',
  shrub: '内侧草地',
  scooter: '电瓶车',
  friend: '摇尾巴的狗友',
  angry: '需要空间的狗狗',
  biscuit: '小饼干',
  lantern0: '第一盏灯影',
  lantern1: '第二盏灯影',
  lantern2: '第三盏灯影',
  bruce: '布鲁斯',
};

/** The director owns time, cameras and resources; it never writes game state. */
export class CinematicDirector {
  constructor(container, options) {
    if (!container || container.nodeType !== 1)
      throw new TypeError('A container element is required.');
    this.config = getScene(options.activityId);
    this.options = options;
    this.content = options.content || {};
    this.happiness = Number.isFinite(options.happiness) ? options.happiness : 100;
    this.notificationOffset = Math.floor(
      (options.random || Math.random)() * (this.content.phone_notifications?.length || 1),
    );
    this.destroyed = false;
    this.listeners = [];
    this.time = 0;
    this.phaseTime = 0;
    this.interactionTime = 0;
    this.phase = this.happiness < 80 ? 'locked' : 'intro';
    this.step = 0;
    this.action = null;
    this.demoCursor = 0;
    this.autoplay = !!options.autoplay;
    this.completed = false;
    this.result = null;
    this.cold = 0;
    this.warmth = 0;
    this.record = 0;
    this.blanket = 0;
    this.curtain = 0;
    this.brushProgress = 0;
    this.warned = false;
    this.warning = false;
    this.warnSince = 0;
    this.restTime = 0;
    this.demoStroke = false;
    this.leashOffset = 0;
    this.pet = 0;
    this.walking = 0;
    this.shake = 0;
    this.quietSince = null;
    this.bridgeWait = 0;
    this.litLanterns = new Set();
    this.pointer = { down: false, target: null, x: 0, y: 0, startX: 0, startY: 0, lastMotion: -10 };
    this.reduced =
      options.reducedMotion ?? window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    this.lowQuality = options.quality === 'low';
    this.host = document.createElement('section');
    this.host.setAttribute('aria-label', '布鲁斯互动演出');
    this.shadow = this.host.attachShadow({ mode: 'open' });
    this.shadow.innerHTML = `
      <link rel="stylesheet" href="${new URL('./cinematic.css', import.meta.url).href}">
      <div class="stage">
        <canvas tabindex="0" aria-label="布鲁斯三维互动场景，空格执行当前提示，Escape 退出"></canvas>
        <div class="shade"></div>
        <div class="hud">
          <div class="top"><div><button class="pill exit" type="button">退出演出</button><div class="title"><small></small><h1></h1></div></div>
          <div class="top-right"><div class="pill score"><span class="owner"></span><span>幸福 <strong></strong></span></div><button class="pill sound" type="button" aria-label="开启环境音" aria-pressed="false">♪</button></div></div>
          <button class="phone" type="button" tabindex="-1" aria-hidden="true" aria-label="查看手机通知"><span class="phone-header"><span class="app-icon">▤</span><span class="app-name"></span><span class="now">now</span></span><span class="phone-text"></span><div class="phone-home"></div></button>
          <div class="caption-wrap"><p class="beat"></p><p class="caption" aria-live="polite"></p><p class="hint"></p><div class="progress"><span></span></div></div>
          <div class="lucky"><small>LUCKY MOMENT</small><h2>高位交换</h2><p></p></div>
          <div class="result" hidden><small></small><div class="delta"></div><p class="line"></p><p class="secondary"></p><div class="result-actions"><button class="pill replay" type="button">再陪它一会儿</button><button class="pill done" type="button">离开演出</button></div></div>
          <div class="accessible-actions" aria-label="场景道具"></div>
        </div>
      </div>`;
    container.append(this.host);
    this.unlockScroll = lockScroll(container.ownerDocument);
    this.el = (selector) => this.shadow.querySelector(selector);
    this.canvas = this.el('canvas');
    this.el('h1').textContent = this.config.title;
    this.el('.title small').textContent = this.config.location;
    this.el('.owner').textContent = options.owner === 'Meya' ? 'Meya & Bruce' : 'Alex & Bruce';
    this.el('.score strong').textContent = this.happiness;
    this._listen(this.el('.exit'), 'click', () => this.exit());
    this._listen(this.el('.done'), 'click', () => this.exit());
    this._listen(this.el('.replay'), 'click', () => this.restart());
    this._listen(this.el('.phone'), 'click', () => {
      if (this.phase === 'interaction') this.finish('phone_fail');
    });
    try {
      this.renderer = new THREE.WebGLRenderer({
        canvas: this.canvas,
        antialias: true,
        alpha: false,
        powerPreference: 'high-performance',
      });
      this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
      this.renderer.toneMappingExposure = 0.98;
      this.renderer.outputColorSpace = THREE.SRGBColorSpace;
      this.renderer.shadowMap.enabled = true;
      this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      this.renderer.info.autoReset = false;
      this.renderer.setPixelRatio(
        Math.min(
          window.devicePixelRatio || 1,
          this.lowQuality ? 0.8 : window.innerWidth < 600 ? 1.5 : 1.75,
        ),
      );
      if (this.lowQuality) this.renderer.shadowMap.enabled = false;
      this.scene = new THREE.Scene();
      this.camera = new THREE.PerspectiveCamera(39, 1, 0.1, 100);
      this.materials = createMaterials();
      this.world = createWorld(this.scene, this.materials, this.config);
      this.bruce = createBruceModel(this.materials, {
        onModeChange: (mode) => {
          this.host.dataset.model = mode;
        },
      });
      this.scene.add(this.bruce.root);
      this.host.dataset.model = 'procedural';
      this.bruce.root.userData.action = 'bruce';
      this.world.targets.set('bruce', this.bruce.root);
      this.lighting = createLighting(
        this.scene,
        this.renderer,
        this.config,
        window.innerWidth < 600 || this.lowQuality,
      );
      this.atmosphere = createAtmosphere(this.scene, this.config, window.innerWidth < 600);
      this.post = createPostProcess(this.renderer, 1, 1);
      this.post.uniforms.uReduced.value = this.reduced ? 1 : 0;
      this.sound = createSound();
      this._listen(this.el('.sound'), 'click', async () => {
        const enabled = await this.sound.toggle();
        if (!this.destroyed) {
          this.el('.sound').setAttribute('aria-pressed', String(enabled));
          this.el('.sound').setAttribute('aria-label', enabled ? '关闭环境音' : '开启环境音');
          this.el('.sound').style.opacity = enabled ? '1' : '.65';
        }
      });
      this.raycaster = new THREE.Raycaster();
      this.pointerNdc = new THREE.Vector2();
      this.lookTarget = vec(this.config.camera.target);
      this.camera.position.copy(this._cameraPosition(this.config.camera.from));
      this.camera.lookAt(this.lookTarget);
      this._setupInput();
      this._makeAccessibleActions();
      this._setupSwapGeometry();
      this.resizeObserver = new ResizeObserver(() => this.resize());
      this.resizeObserver.observe(this.host);
      this.resize();
      this._listen(window, 'resize', () => this.resize());
      this._listen(document, 'visibilitychange', () => {
        this.pointer.down = false;
        if (document.hidden) this.sound.pause();
        else this.sound.resume();
        this.lastFrame = null;
      });
      this._listen(this.canvas, 'webglcontextlost', (e) => {
        e.preventDefault();
        this.contextLost = true;
        cancelAnimationFrame(this.frame);
        this.sound.pause();
        this._caption('画面暂时休息了。', '点击“重新载入画面”恢复演出。');
        this._showResult('画面连接中断', '', '可以重新载入画面，或退出后重进。', '');
        this.el('.replay').textContent = '重新载入画面';
        this.el('.replay').hidden = false;
      });
      this._caption(this.phase === 'locked' ? '它把背转了过去。' : this.config.opening, '');
      this._beat(this.phase === 'locked' ? '冷战中' : '开场');
      this.frame = requestAnimationFrame((now) => this._frame(now));
    } catch (error) {
      this._disposeGraphics();
      const fallback = document.createElement('div');
      fallback.className = 'error';
      const title = document.createElement('h2');
      title.textContent = '暂时无法打开三维演出';
      const text = document.createElement('p');
      text.textContent =
        '此浏览器未能启动 WebGL 2。请开启硬件加速，或换一个支持 WebGL 2 的浏览器再试。';
      const exit = document.createElement('button');
      exit.className = 'pill';
      exit.textContent = '退出演出';
      this._listen(exit, 'click', () => this.exit());
      fallback.append(title, text, exit);
      this.el('.stage').replaceChildren(fallback);
      this.error = error;
    }
  }

  _listen(target, type, handler, options) {
    target.addEventListener(type, handler, options);
    this.listeners.push(() => target.removeEventListener(type, handler, options));
  }
  _caption(line, hint = '') {
    if (this.caption !== line) {
      this.caption = line;
      this.el('.caption').textContent = line;
    }
    this.el('.hint').textContent = hint;
  }
  _beat(text) {
    this.el('.beat').textContent =
      this.autoplay && this.phase !== 'locked' ? `自动演出 · ${text}` : text;
  }
  _progress(value) {
    this.el('.progress span').style.width = `${clamp(value, 0, 1) * 100}%`;
  }
  _cameraPosition(array) {
    const point = vec(array),
      target = vec(this.config.camera.target),
      portrait = this.host.clientWidth / Math.max(this.host.clientHeight, 1) < 0.85;
    if (portrait) point.sub(target).multiplyScalar(1.45).add(target);
    return point;
  }
  resize() {
    if (this.destroyed || !this.renderer || !this.post) return;
    const width = this.host.clientWidth || window.innerWidth,
      height = this.host.clientHeight || window.innerHeight;
    this.camera.aspect = width / Math.max(height, 1);
    this.camera.fov = this.camera.aspect < 0.85 ? 51 : 39;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height, false);
    const size = this.renderer.getDrawingBufferSize(new THREE.Vector2());
    this.post.resize(size.x, size.y);
  }

  _setupInput() {
    this._listen(this.canvas, 'pointerdown', (e) => {
      if (this.phase !== 'interaction' || this.autoplay) return;
      this.canvas.focus({ preventScroll: true });
      this.pointer.down = true;
      this.pointer.startX = this.pointer.x = e.clientX;
      this.pointer.startY = this.pointer.y = e.clientY;
      this.pointer.target = this._pick(e);
      this.pointer.lastMotion = this.time;
      this.canvas.setPointerCapture(e.pointerId);
      if (this.pointer.target !== 'ball' && this.pointer.target !== 'leash')
        this.perform(this.pointer.target);
    });
    this._listen(this.canvas, 'pointermove', (e) => {
      const rect = this.canvas.getBoundingClientRect(),
        dx = e.clientX - this.pointer.x,
        dy = e.clientY - this.pointer.y;
      this.pointer.x = e.clientX;
      this.pointer.y = e.clientY;
      this.pointerNdc.set(
        ((e.clientX - rect.left) / rect.width) * 2 - 1,
        -((e.clientY - rect.top) / rect.height) * 2 + 1,
      );
      if (Math.hypot(dx, dy) > 1) this.pointer.lastMotion = this.time;
      if (this.phase !== 'interaction' || this.autoplay) return;
      if (this.pointer.down && this.pointer.target === 'leash') {
        this.leashOffset = clamp(((e.clientX - this.pointer.startX) / rect.width) * 4, -1.4, 0.8);
        if (this.leashOffset < -0.35 && this.step === 0) this.perform('sniff');
      }
      this.canvas.style.cursor = this._pick(e)
        ? this.pointer.down
          ? 'grabbing'
          : 'grab'
        : 'default';
      if (this.pointer.down && this.config.mode === 'brush' && this.pointer.target === 'bruce') {
        const hit = this._hit(e);
        if (hit) this.atmosphere.emit(hit.point, 2);
      }
    });
    const release = (e) => {
      if (this.pointer.down && this.pointer.target === 'ball' && this.phase === 'interaction') {
        this.throwDirection = clamp(
          (e.clientX - this.pointer.startX) / Math.max(this.host.clientWidth, 1),
          -0.7,
          0.7,
        );
        this.perform('throw');
      }
      this.pointer.down = false;
      this.pointer.target = null;
      if (this.canvas.hasPointerCapture(e.pointerId))
        this.canvas.releasePointerCapture(e.pointerId);
    };
    this._listen(this.canvas, 'pointerup', release);
    this._listen(this.canvas, 'pointercancel', (e) => {
      this.pointer.down = false;
      this.pointer.target = null;
      if (this.canvas.hasPointerCapture(e.pointerId))
        this.canvas.releasePointerCapture(e.pointerId);
    });
    this._listen(window, 'blur', () => {
      this.pointer.down = false;
      this.pointer.target = null;
    });
    this._listen(this.shadow, 'keydown', (e) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        this.exit();
      }
      if (
        (e.key === ' ' || e.key === 'Enter') &&
        e.composedPath()[0] === this.canvas &&
        this.phase === 'interaction'
      ) {
        e.preventDefault();
        const target = this._currentTarget();
        if (this.config.mode === 'brush') this.perform(this.warning ? 'rest' : 'stroke');
        else this.perform(target === 'ball' ? 'throw' : target);
      }
    });
  }
  _hit(e) {
    const rect = this.canvas.getBoundingClientRect();
    this.pointerNdc.set(
      ((e.clientX - rect.left) / rect.width) * 2 - 1,
      -((e.clientY - rect.top) / rect.height) * 2 + 1,
    );
    this.raycaster.setFromCamera(this.pointerNdc, this.camera);
    return this.raycaster.intersectObjects(
      [...this.world.targets.values()].filter((o) => o.visible),
      true,
    )[0];
  }
  _pick(e) {
    const hit = this._hit(e);
    let object = hit?.object;
    while (object && !object.userData.action) object = object.parent;
    return object?.userData.action || null;
  }
  _makeAccessibleActions() {
    const group = this.el('.accessible-actions');
    for (const id of this.world.targets.keys()) {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = ACTION_LABELS[id] || id;
      this._listen(button, 'click', () => this.perform(id === 'ball' ? 'throw' : id));
      group.append(button);
    }
  }
  _currentTarget() {
    switch (this.config.mode) {
      case 'brush':
        return 'bruce';
      case 'fetch':
        return 'ball';
      case 'sequence':
        return this.config.actions[this.step];
      case 'nap':
        return this.config.actions[this.step];
      case 'kitchen':
        return this.step === 0 ? 'apple' : 'bowl';
      case 'cafe':
        return 'welcome';
      case 'window':
        return this.step === 0 ? 'welcome' : 'biscuit';
      case 'walk':
        return this.step === 1 ? 'bruce' : 'shrub';
      case 'lawn':
        return 'friend';
      case 'bridge':
        return `lantern${this.step}`;
      default:
        return null;
    }
  }
  _startInteraction() {
    this.phase = 'interaction';
    this.phaseTime = 0;
    this.interactionTime = 0;
    this._beat('陪伴');
    this._caption(
      this.config.instruction,
      this.autoplay
        ? '正在自动演示；可在预览菜单切换为亲自互动。'
        : '触摸画面中的道具，也可以用 Tab 选择道具。',
    );
    this.world.highlight(this._currentTarget());
  }

  _startAction(name, duration, done) {
    this.action = {
      name,
      duration,
      start: this.time,
      done,
      origin: this.bruce.root.position.clone(),
      rotation: this.bruce.root.rotation.y,
    };
    this.world.indicator.visible = false;
    this._progress(0);
  }
  _advanceStep() {
    this.step++;
    this._progress(this.step / Math.max(this.config.actions?.length || 3, 1));
    const hint = this.config.steps?.[this.step];
    if (hint) this._caption(hint);
    this.world.highlight(this._currentTarget());
  }

  /** All pointer, keyboard and demo input uses this same action path. */
  perform(id) {
    if (!id || this.destroyed || this.phase !== 'interaction' || this.action) return false;
    if (['dryer', 'speaker', 'vacuum', 'grapes', 'noDogs', 'angry', 'scooter'].includes(id)) {
      this.failureProp = id;
      this.finish('hazard_fail');
      return true;
    }
    const mode = this.config.mode;
    if (mode === 'brush') {
      if (id === 'stroke' || id === 'bruce' || id === 'brush') {
        if (id === 'stroke' || id === 'brush') this.demoStroke = true;
        return true;
      }
      if (id === 'rest') {
        this.demoStroke = false;
        this.pointer.down = false;
        return true;
      }
    }
    if (mode === 'sequence') {
      if (!this.config.actions.includes(id)) return false;
      if (id !== this.config.actions[this.step]) {
        this.finish('hazard_fail');
        return true;
      }
      this._caption(
        id === 'towel'
          ? '一只爪子，再一只。'
          : id === 'blanket'
            ? '它把下巴放了下来。'
            : '针尖落下，雨声退到身后。',
      );
      this._startAction(id, 2.7, () => {
        if (id === 'vinyl') this.finish('win');
        else this._advanceStep();
      });
      return true;
    }
    if (mode === 'fetch' && (id === 'throw' || id === 'ball')) {
      this._caption('去找吧。', '');
      this.bruce.setMood('excited');
      this.ballOrigin = this.world.props.ball.position.clone();
      this.ballLanding = vec([this.throwDirection ? this.throwDirection * 3 : -1.75, 0.055, -1.65]);
      this.ballVelocity = this.ballLanding.clone().sub(this.ballOrigin).multiplyScalar(1.4);
      this.ballVelocity.y = 2.7;
      this._startAction('fetch', 6.8, () => this.finish('win'));
      return true;
    }
    if (mode === 'nap' && this.config.actions.includes(id)) {
      if (id !== this.config.actions[this.step]) return false;
      this._caption(id === 'curtain' ? '让光再软一点。' : '它找到了最舒服的那一角。');
      this._startAction(id, 2, () => {
        this._advanceStep();
        if (this.step === 2) {
          this.quietSince = this.time;
          this.bruce.setMood('sleep');
          this.world.highlight(null);
        }
      });
      return true;
    }
    if (mode === 'kitchen') {
      if (id === 'apple' && this.step === 0) {
        this._caption('一小块就够了。', '轻触 BRUCE 碗，把苹果放进去。');
        this._startAction('apple', 1.6, () => this._advanceStep());
        return true;
      }
      if (id === 'bowl' && this.step === 1) {
        this._caption('它先闻了闻，才小心舔了一口。');
        this._startAction('feed', 2.6, () => this.finish('win'));
        return true;
      }
    }
    if ((mode === 'cafe' || mode === 'window') && id === 'welcome' && this.step === 0) {
      this._caption('这扇门，欢迎你们一起。');
      this._startAction('enter', 4, () => {
        if (mode === 'cafe') this.finish('win');
        else this._advanceStep();
      });
      return true;
    }
    if (mode === 'window' && id === 'biscuit' && this.step === 1) {
      this._caption('橱窗里，留下了一枚湿鼻印。');
      this._startAction('feed', 2.8, () => this.finish('win'));
      return true;
    }
    if (mode === 'walk') {
      if ((id === 'sniff' || id === 'shrub' || id === 'leash') && this.step === 0) {
        this._caption('这片草丛，有一封它想读的信。');
        this._startAction('sniff', 2.9, () => this._advanceStep());
        return true;
      }
      if ((id === 'praise' || id === 'bruce') && this.step === 1) {
        this._caption('“Beautiful scarf.”', '它回头看你，尾巴先回答了。');
        this.bruce.setMood('excited');
        this._startAction('praise', 2.8, () => {
          this._advanceStep();
          this._caption('车铃近了，先靠内侧等一等。', '轻触草地，把它带回身边。');
          this.bruce.setMood('warn');
        });
        return true;
      }
      if ((id === 'safe' || id === 'shrub' || id === 'leash') && this.step === 2) {
        this._caption('等它过去，再慢慢走。');
        this._startAction('safe', 3.4, () => this.finish('win'));
        return true;
      }
    }
    if (mode === 'lawn' && id === 'friend') {
      this._caption(['慢慢靠近，先打个招呼。', '尾巴摇起来了。', '下次还在这里见。'][this.step]);
      this._startAction('friend', 2.8, () => {
        this._advanceStep();
        if (this.step === 3) this.finish('win');
        else this._caption(`再和摇尾巴的朋友打个招呼。`, `已经互相闻过 ${this.step} 次。`);
      });
      return true;
    }
    if (mode === 'bridge' && id.startsWith('lantern')) {
      if (this.litLanterns.has(id)) return false;
      if (this.step === 2 && this.time < this.bridgeWait) {
        this.finish('hazard_fail');
        return true;
      }
      this.litLanterns.add(id);
      const lamp = this.world.props[id];
      lamp.scale.setScalar(1.25);
      this.atmosphere.emit(lamp.position, 12);
      this._startAction('lantern', 1.5, () => {
        this._advanceStep();
        if (this.step === 3) this.finish('win');
        else if (this.step === 2) {
          this.bridgeWait = this.time + 2;
          this._caption('车铃响了。先停手，等它经过。');
          this.bruce.setMood('warn');
        }
      });
      return true;
    }
    return false;
  }

  _updateAction(dt) {
    const a = this.action;
    if (!a) return;
    const t = clamp((this.time - a.start) / a.duration, 0, 1),
      e = ease(t),
      props = this.world.props,
      root = this.bruce.root;
    this._progress(t);
    this.pet = 0;
    this.walking = 0;
    switch (a.name) {
      case 'towel': {
        const p = props.towel;
        p.position.copy(p.userData.base).lerp(vec([0, 0.17, 0.76]), Math.sin(Math.PI * t));
        p.rotation.z = Math.sin(t * 24) * 0.12;
        this.pet = 0.5;
        this.bruce.setMood('happy');
        break;
      }
      case 'blanket':
        this.blanket = smooth(t);
        break;
      case 'vinyl':
        this.record = smooth(t);
        this.bruce.setMood('sleep');
        break;
      case 'curtain':
        this.curtain = e;
        break;
      case 'cushion':
        props.cushion.scale.y = 1 - Math.sin(t * Math.PI * 4) * 0.14;
        this.bruce.setMood('sleep');
        break;
      case 'apple':
        props.apple.position.y = props.apple.userData.base.y + Math.sin(t * Math.PI) * 0.45;
        props.apple.rotation.z = t * Math.PI * 0.2;
        break;
      case 'feed': {
        const food = props.apple || props.biscuit;
        if (food) {
          const to = root.localToWorld(vec([0, 0.5, 1.04]));
          food.position.copy(food.userData.base).lerp(to, smooth(t));
          food.scale.setScalar(1 - smooth((t - 0.65) / 0.35) * 0.95);
        }
        this.bruce.setMood('curious');
        break;
      }
      case 'fetch': {
        const seconds = t * a.duration;
        if (seconds < 3.3) {
          props.ball.position.addScaledVector(this.ballVelocity, dt);
          this.ballVelocity.y -= 9.81 * dt;
          if (props.ball.position.y <= 0.025) {
            props.ball.position.y = 0.025;
            this.ballVelocity.y = Math.abs(this.ballVelocity.y) * 0.45;
            this.ballVelocity.x *= 0.68;
            this.ballVelocity.z *= 0.68;
            if (this.ballVelocity.y < 0.12) this.ballVelocity.y = 0;
          }
          props.ball.rotation.x += this.ballVelocity.length() * dt * 5;
          if (seconds > 1.4) this.ballLanding.copy(props.ball.position).setY(0);
        }
        if (seconds > 0.35 && seconds < 3.3) {
          root.position.copy(a.origin).lerp(this.ballLanding, ease((seconds - 0.35) / 2.95));
          root.position.y = 0;
          root.rotation.y = damp(root.rotation.y, -2.2, 4, dt);
          this.walking = 1;
        }
        if (seconds >= 3.3 && seconds < 3.7) {
          this.bruce.setMood('curious');
          this._caption('沙发角，一对长耳朵先探了出来。');
          props.ball.position.copy(root.localToWorld(vec([0, 0.61, 1.13])));
        }
        if (seconds >= 3.7) {
          const q = ease((seconds - 3.7) / 3.1);
          root.position.copy(this.ballLanding).lerp(vec([0, 0, 0.28]), q);
          root.position.y = 0;
          root.rotation.y = damp(root.rotation.y, 0.12, 4, dt);
          this.walking = 1;
          props.ball.position.copy(root.localToWorld(vec([0, 0.61, 1.13])));
          if (seconds > 4) this._caption('找到了。它要亲自送回来。');
        }
        break;
      }
      case 'enter':
        root.position.copy(a.origin).lerp(vec([-1.3, 0, -1.4]), e);
        root.rotation.y = damp(root.rotation.y, -2.4, 3, dt);
        this.walking = t < 0.72 ? 0.65 : 0;
        if (t > 0.72) {
          this.bruce.setMood('happy');
          this._caption('店员留了一碗清水，还有一块小饼干。');
          if (props.bowl) props.bowl.visible = true;
          if (props.biscuit) props.biscuit.visible = true;
        }
        break;
      case 'sniff':
        root.position.copy(a.origin).lerp(vec([-0.7, 0, 0.25]), Math.sin((t * Math.PI) / 2));
        root.rotation.y = damp(root.rotation.y, -0.8, 3, dt);
        this.bruce.setMood('curious');
        this.walking = t < 0.35 ? 0.5 : 0;
        break;
      case 'praise':
        this.pet = 0.6;
        this.bruce.setMood('excited');
        break;
      case 'safe':
        root.position.copy(a.origin).lerp(vec([-0.7, 0, 0.15]), smooth(t));
        this.walking = t < 0.3 ? 0.4 : 0;
        if (props.scooter) props.scooter.position.z = lerp(-4, 6, t);
        this.bruce.setMood('happy');
        break;
      case 'friend':
        root.position.copy(a.origin).lerp(vec([-0.72, 0, 0.05]), Math.sin(t * Math.PI));
        root.rotation.y = Math.sin(t * Math.PI) * -0.8;
        this.pet = 0.4;
        this.walking = Math.sin(t * Math.PI) * 0.4;
        this.bruce.setMood('happy');
        break;
      case 'lantern':
        this.warmth = Math.max(this.warmth, 0.1 + this.step * 0.12);
        break;
    }
    if (t >= 1) {
      this.action = null;
      a.done?.();
    }
  }

  _updateInteraction(dt) {
    this.interactionTime += dt;
    if (this.autoplay) {
      const event = this.config.auto[this.demoCursor];
      if (event && this.interactionTime >= event.at && !this.action) {
        if (this.perform(event.action)) this.demoCursor++;
      }
    }
    this._updatePhone();
    if (this.config.mode === 'brush') {
      const stroking =
        this.demoStroke ||
        (this.pointer.down &&
          this.pointer.target === 'bruce' &&
          this.time - this.pointer.lastMotion < 0.2);
      this.pet = stroking && !this.warning ? 1 : 0;
      if (this.warning) {
        this.bruce.setMood('warn');
        if (stroking && this.time - this.warnSince > 0.85) this.finish('hazard_fail');
        if (!stroking) this.restTime += dt;
        else this.restTime = 0;
        if (this.restTime > 0.8) {
          this.warning = false;
          this.bruce.setMood('happy');
          this._caption('它又把背靠过来了。', '继续轻轻顺毛。');
        }
      } else if (stroking) {
        this.bruce.setMood('happy');
        this.brushProgress += dt * 0.17;
        this._progress(this.brushProgress);
        const p = this.bruce.root.localToWorld(
          vec([Math.sin(this.time * 2) * 0.16, 0.84, Math.sin(this.time * 1.7) * 0.5]),
        );
        this.atmosphere.emit(p, 1);
        if (this.brushProgress >= 0.43 && !this.warned) {
          this.warning = this.warned = true;
          this.warnSince = this.time;
          this._caption('耳朵贴平了。先停一停。', '松手，给它一点时间。');
        }
        if (this.brushProgress >= 1) this.finish('win');
      }
    }
    if (this.config.mode === 'nap' && this.quietSince !== null) {
      this._progress((this.time - this.quietSince) / 6);
      if (this.time - this.quietSince >= 6) this.finish('win');
    }
    if (this.config.mode === 'walk' && this.step === 2 && !this.action) {
      this.shake = 0.08;
      if (this.world.props.scooter)
        this.world.props.scooter.position.z = -3 + Math.sin(this.time * 0.8) * 0.4;
    }
    if (
      this.config.mode === 'bridge' &&
      this.step === 2 &&
      this.time >= this.bridgeWait &&
      this.bridgeWait > 0 &&
      !this.action
    ) {
      this.bruce.setMood('happy');
      this._caption('车铃远了。可以点亮最后一盏灯了。');
    }
    if (this.interactionTime > this.config.duration && !this.action) this.finish('hazard_fail');
  }

  _updatePhone() {
    const notifications = this.content.phone_notifications || [];
    if (!notifications.length) return;
    const first = this.config.phoneAt,
      cycle = this.config.mode === 'nap' ? 5.5 : 8;
    const since = this.interactionTime - first,
      visible = since >= 0 && since % cycle < 4.3;
    const n = Math.floor(Math.max(0, since) / cycle);
    const notification = notifications[(this.notificationOffset + n) % notifications.length];
    this.el('.app-name').textContent = notification.app;
    this.el('.phone-text').textContent = notification.text;
    this.el('.phone').classList.toggle('visible', visible);
    this.el('.phone').setAttribute('aria-hidden', String(!visible));
    this.el('.phone').tabIndex = visible ? 0 : -1;
  }

  finish(outcome) {
    if (this.phase !== 'interaction' || this.completed) return;
    this.pointer.down = false;
    this.demoStroke = false;
    this.action = null;
    this.phase = 'outro';
    this.phaseTime = 0;
    this.outroOrigin = this.bruce.root.position.clone();
    this.outroCamera = this.camera.position.clone();
    this.outroRotation = this.bruce.root.rotation.y;
    const delta =
      outcome === 'win' ? this.config.win : -Math.min(this.config.loss * -1, this.happiness);
    const lines = this.content.activities?.[this.options.activityId]?.[`${outcome}_lines`] || [];
    const rng = this.options.random || Math.random;
    const summaryLine =
      lines[Math.floor(rng() * lines.length)] ||
      (outcome === 'win' ? '布鲁斯又靠近了你一点。' : '它低下头，慢慢把背转了过去。');
    const triggerSwapCandidate =
      outcome === 'win' && this.happiness + delta >= 80 && rng() < this.config.swap;
    this.result = Object.freeze({ outcome, delta, triggerSwapCandidate, summaryLine });
    this.bruce.setMood(outcome === 'win' ? this.config.ending : 'sulk');
    this.world.highlight(null);
    this._hidePhone();
    this._beat(outcome === 'win' ? '余温' : '失落');
    this._caption(
      outcome === 'win'
        ? this.config.closing
        : outcome === 'phone_fail'
          ? '你看向屏幕。它没有再等。'
          : this.failureProp === 'noDogs'
            ? '门里的人轻轻摇头。它退回你身边。'
            : '它只是想，离你近一点。',
    );
  }
  _hidePhone() {
    this.el('.phone').classList.remove('visible');
    this.el('.phone').setAttribute('aria-hidden', 'true');
    this.el('.phone').tabIndex = -1;
  }

  _updateOutro(dt) {
    const t = clamp(this.phaseTime / 3.5, 0, 1),
      won = this.result?.outcome === 'win';
    this.cold = damp(this.cold, won ? 0 : 1, 6, dt);
    this.warmth = damp(this.warmth, won ? 1 : 0, 2, dt);
    this.pet = 0;
    this.walking = 0;
    this.shake = 0;
    if (won) {
      if (this.config.ending === 'excited') {
        this.bruce.root.rotation.y = this.reduced
          ? damp(this.bruce.root.rotation.y, 0, 3, dt)
          : lerp(this.outroRotation, Math.PI * 2, smooth(t));
        this.walking = Math.sin(t * Math.PI) * 0.75;
      } else this.bruce.root.rotation.y = damp(this.bruce.root.rotation.y, 0, 2, dt);
    } else {
      this.bruce.root.position
        .copy(this.outroOrigin)
        .add(vec([-0.45 * ease(t), 0, (this.failureProp === 'noDogs' ? 0.65 : -0.7) * ease(t)]));
      this.walking = t > 0.2 && t < 0.65 ? 0.32 : 0;
    }
    this._progress(t);
    if (t >= 1) this._complete();
  }
  _complete() {
    if (this.completed || this.destroyed) return;
    this.completed = true;
    this.phase = 'result';
    this.phaseTime = 0;
    const score = clamp(this.happiness + this.result.delta, 0, 9999),
      locked = score < 80;
    this.el('.score strong').textContent = score;
    this._caption('', '');
    this.el('.caption-wrap').hidden = true;
    this._showResult(
      this.result.outcome === 'win'
        ? '陪伴高光时刻'
        : locked
          ? '幸福跌破 80 · 冷战中'
          : '一段小小的失落',
      `${this.result.delta >= 0 ? '+' : ''}${this.result.delta}`,
      this.result.summaryLine,
      locked
        ? '布鲁斯需要先休息。回到零食柜，哄它回到 80 分。'
        : this.result.triggerSwapCandidate
          ? '幸运时刻，正在揭晓。'
          : `这一刻的幸福指数 · ${score}`,
    );
    try {
      const callback = this.options.onComplete?.({ ...this.result });
      Promise.resolve(callback)
        .then((data) => {
          if (
            !this.destroyed &&
            this.result.triggerSwapCandidate &&
            Number.isFinite(data?.newScore)
          )
            this.revealSwap(data);
        })
        .catch((error) => {
          if (!this.destroyed) {
            this.callbackError = error;
            this.el('.result .secondary').textContent = '结算暂未同步，请稍后重试。';
          }
        });
    } catch (error) {
      this.callbackError = error;
      this.el('.result .secondary').textContent = '结算暂未同步，请稍后重试。';
    }
  }
  _showResult(title, delta, line, secondary) {
    const result = this.el('.result');
    result.hidden = false;
    result.querySelector('small').textContent = title;
    result.querySelector('.delta').textContent = delta;
    result.querySelector('.line').textContent = line;
    result.querySelector('.secondary').textContent = secondary;
    this.el('.replay').hidden =
      this.happiness < 80 || this.happiness + (this.result?.delta || 0) < 80;
    result.classList.add('visible');
  }

  _setupSwapGeometry() {
    this.swapRings = new THREE.Group();
    this.scene.add(this.swapRings);
    this.swapRings.visible = false;
    for (let i = 0; i < 5; i++) {
      const ring = new THREE.Mesh(
        new THREE.TorusGeometry(1.1 + i * 0.25, 0.008 + i * 0.002, 6, 100),
        new THREE.MeshBasicMaterial({
          color: '#f6dca1',
          transparent: true,
          opacity: 0.6,
          depthWrite: false,
        }),
      );
      ring.position.y = 0.85;
      ring.rotation.set(Math.PI / 2 + i * 0.35, i * 0.7, 0);
      this.swapRings.add(ring);
    }
  }
  /** Only a real /api/swap response supplies scores; the renderer never invents one. */
  revealSwap(data) {
    if (
      this.destroyed ||
      !this.result?.triggerSwapCandidate ||
      !Number.isFinite(data?.newScore) ||
      this.swapData
    )
      return false;
    this.swapData = { ...data };
    this.phase = 'swap';
    this.phaseTime = 0;
    this.el('.result').hidden = true;
    this.el('.lucky').classList.add('visible');
    this.el('.lucky p').textContent = data.topBonus
      ? '已经站在最高处。布鲁斯又送来一点好运。'
      : `这一束光，来自 ${String(data.targetNickname || '一位新朋友')}。`;
    this.swapRings.visible = true;
    this.bruce.setMood('excited');
    return true;
  }

  _updateCamera(dt) {
    let desired,
      target = vec(this.config.camera.target);
    if (this.phase === 'intro' || this.phase === 'locked') {
      const t = this.reduced ? 1 : ease(this.phaseTime / 2.5);
      desired = this._cameraPosition(this.config.camera.from).lerp(
        this._cameraPosition(this.config.camera.to),
        t,
      );
    } else if (this.phase === 'outro' && this.result?.outcome !== 'win') {
      const t = smooth(this.phaseTime / 0.55);
      const close = this._cameraPosition([1.65, 1.35, 2.7]);
      desired = this.outroCamera.clone().lerp(close, this.reduced ? 0.3 : t);
      desired.addScaledVector(vec([0.3, 0.3, 1]), smooth((this.phaseTime - 0.9) / 2.6));
      target = this.bruce.root.position.clone().add(vec([0, 0.65, 0.45]));
    } else if (this.phase === 'outro' && !this.reduced) {
      const base = this._cameraPosition(this.config.camera.to),
        a = smooth(this.phaseTime / 3.5) * 0.35;
      const subject = this.bruce.root.position.clone().add(vec([0, 0.5, 0.2]));
      if (['cafe', 'window'].includes(this.config.mode))
        base.lerp(this._cameraPosition([1.4, 1.9, 4.4]), smooth(this.phaseTime / 3.5) * 0.7);
      target.lerp(subject, 0.65);
      desired = base
        .sub(target)
        .applyAxisAngle(vec([0, 1, 0]), a)
        .add(target);
    } else if (this.phase === 'swap') {
      desired = this._cameraPosition([3.3, 2.8, 5.2]);
      target = vec([0, 0.8, 0]);
    } else if (this.action?.name === 'fetch' && !this.reduced) {
      const follow = this.bruce.root.position;
      desired = this._cameraPosition([2.7 + follow.x * 0.35, 1.25, 4.3 + follow.z * 0.3]);
      target = follow.clone().add(vec([0, 0.55, 0.3]));
    } else {
      desired = this._cameraPosition(this.config.camera.to);
      if (this.config.mode === 'walk') desired.x += this.bruce.root.position.x * 0.3;
    }
    if (this.phase === 'interaction' && !this.reduced && !this.action) {
      desired.x += Math.sin(this.time * 0.6) * 0.018;
      desired.y += Math.sin(this.time * 0.9) * 0.012;
    }
    this.camera.position.lerp(desired, 1 - Math.exp(-dt * (this.phase === 'intro' ? 12 : 4)));
    this.lookTarget.lerp(target, 1 - Math.exp(-dt * 4));
    this.camera.lookAt(this.lookTarget);
    this.post.uniforms.uFocus.value = this.camera.position.distanceTo(
      this.bruce.root.position.clone().add(vec([0, 0.7, 0.4])),
    );
  }

  _frame(now) {
    if (this.destroyed || this.contextLost) return;
    const dt = this.lastFrame == null ? 0 : clamp((now - this.lastFrame) / 1000, 0, 2);
    this.lastFrame = now;
    if (!document.hidden) {
      // Keep film time independent of frame rate, while warning/rope logic uses
      // bounded steps. A slow frame cannot jump over a dog's stop signal.
      const ticks = Math.ceil(dt / 0.05),
        tickDt = ticks ? dt / ticks : 0;
      for (let tick = 0; tick < ticks; tick++) {
        const dt = tickDt;
        this.time += dt;
        this.phaseTime += dt;
        if (this.phase === 'intro') {
          if (this.config.environment === 'street') {
            const p = ease(this.phaseTime / 2.5);
            this.bruce.root.position.x = lerp(-0.55, 0, p);
            this.bruce.root.rotation.y = -0.25 * (1 - p);
            this.walking = this.phaseTime < 1.8 ? 0.65 : 0.22;
          }
          this.shake = this.config.rain && this.phaseTime > 0.5 && this.phaseTime < 1.7 ? 0.8 : 0;
          this.bruce.setMood(this.config.mode === 'nap' ? 'sleep' : 'curious');
          this._progress(this.phaseTime / 2.5);
          if (this.phaseTime >= 2.5) {
            this.shake = 0;
            this.walking = 0;
            this.bruce.setMood('happy');
            this._startInteraction();
          }
        } else if (this.phase === 'interaction') {
          this._updateInteraction(dt);
          this._updateAction(dt);
        } else if (this.phase === 'outro') this._updateOutro(dt);
        else if (this.phase === 'locked') {
          this.cold = damp(this.cold, 1, 3, dt);
          this.bruce.setMood('sulk');
          if (this.phaseTime > 3.5) {
            this.phase = 'locked_result';
            this.el('.caption-wrap').hidden = true;
            this._showResult(
              '冷战中 · 低于 80 分',
              String(this.happiness),
              '布鲁斯暂时不想陪玩。先去零食急救柜，让它回到 80 分。',
              '它需要先回到 80 分，再一起出门。',
            );
          }
        } else if (this.phase === 'swap') {
          const t = clamp(this.phaseTime / 4.5, 0, 1);
          this.warmth = 1;
          this.swapRings.rotation.y += dt * 0.7;
          this.swapRings.children.forEach((ring, i) => {
            ring.rotation.z += dt * (0.2 + i * 0.12);
            ring.material.opacity = Math.sin(t * Math.PI) * 0.7;
          });
          if (t > 0.45)
            this.el('.lucky h2').textContent =
              `${this.happiness + this.result.delta}  ·  ${this.swapData.newScore}`;
          if (t >= 1) {
            this.phase = 'result';
            this.el('.lucky').classList.remove('visible');
            this.swapRings.visible = false;
            this.el('.score strong').textContent = this.swapData.newScore;
            this._showResult(
              this.swapData.topBonus ? '榜首幸运时刻' : '高位交换已确认',
              String(this.swapData.newScore),
              this.result.summaryLine,
              this.swapData.topBonus
                ? '额外奖励已由服务器确认。'
                : `与 ${String(this.swapData.targetNickname || '新朋友')} 交换幸福指数，结果已由服务器确认。`,
            );
          }
        }
        if (this.destroyed) return;
      }
      this._updateCamera(dt);
      this.bruce.update(dt, this.time, {
        gaze: [this.pointerNdc.x, -this.pointerNdc.y],
        walking: this.walking,
        petting: this.pet,
        shake: this.shake,
        resting:
          this.config.mode === 'brush' && ['intro', 'interaction'].includes(this.phase) ? 1 : 0,
        jump:
          this.phase === 'outro' &&
          this.result?.outcome === 'win' &&
          this.config.ending === 'excited' &&
          !this.reduced
            ? (this.phaseTime % 1.2) / 1.2
            : 0,
        halo: this.warmth,
      });
      if (this.config.rain && this.shake > 0.2)
        this.atmosphere.emit(this.bruce.root.localToWorld(vec([0, 0.75, 0])), 5, 1);
      this.world.update(this.time, dt, this.bruce, {
        record: this.record,
        blanket: this.blanket,
        curtain: this.curtain,
        cold: this.cold,
        leashOffset: this.leashOffset,
      });
      this.lighting.update(this.cold, this.warmth, this.bruce);
      this.atmosphere.update(this.time, dt, this.cold, this.warmth);
      this.sound.update(this.time, {
        wet: this.config.rain ? 1 : 0,
        record: this.record,
        petting: this.pet,
        cold: this.cold,
      });
      this.post.uniforms.uTime.value = this.time;
      this.post.uniforms.uCold.value = this.cold;
      this.post.uniforms.uWarm.value = this.warmth;
      this.post.uniforms.uFade.value = smooth(this.time / 0.8);
      this.post.uniforms.uFlash.value =
        this.phase === 'swap' && !this.reduced
          ? Math.max(0, 1 - Math.abs(this.phaseTime - 2) * 2.8) * 0.25
          : 0;
      this.renderer.info.reset();
      this.post.render(this.scene, this.camera);
      if (!this.warmed) {
        this.warmed = true;
        this.lastFrame = null;
      }
    }
    this.frame = requestAnimationFrame((t) => this._frame(t));
  }

  setAutoplay(enabled) {
    this.autoplay = !!enabled;
    this.demoStroke = false;
    this.pointer.down = false;
    // A demo begins from a fresh shot so already-used props cannot invalidate it.
    this.restart();
  }
  restart() {
    if (this.destroyed) return;
    const container = this.host.parentElement;
    const happiness =
      this.completed && this.result
        ? (this.swapData?.newScore ?? clamp(this.happiness + this.result.delta, 0, 9999))
        : this.happiness;
    const options = { ...this.options, happiness, autoplay: this.autoplay };
    this.destroy();
    this.options.onRestart?.(options);
    if (!this.options.onRestart) this.replacement = new CinematicDirector(container, options);
  }
  getSnapshot() {
    return {
      activityId: this.options.activityId,
      phase: this.phase,
      time: this.time,
      interactionTime: this.interactionTime,
      step: this.step,
      action: this.action?.name || null,
      warning: this.warning,
      brushProgress: this.brushProgress,
      model: this.bruce?.mode,
      autoplay: this.autoplay,
      completed: this.completed,
      result: this.result ? { ...this.result } : null,
      renderer: this.renderer
        ? {
            geometries: this.renderer.info.memory.geometries,
            textures: this.renderer.info.memory.textures,
            calls: this.renderer.info.render.calls,
          }
        : null,
      error: this.error?.message || this.callbackError?.message || null,
    };
  }
  exit() {
    if (this.destroyed) return;
    const callback = this.options.onExit;
    this.destroy();
    callback?.();
  }
  _disposeGraphics() {
    this.bruce?.destroy();
    this.sound?.destroy();
    this.post?.destroy();
    this.lighting?.destroy();
    if (this.scene) disposeTree(this.scene);
    // Some material variants are intentionally unused by a given environment.
    if (this.materials)
      for (const material of Object.values(this.materials)) {
        for (const value of Object.values(material)) if (value?.isTexture) value.dispose();
        material.dispose();
      }
    this.renderer?.renderLists.dispose();
    this.renderer?.dispose();
    this.renderer?.forceContextLoss();
  }
  destroy() {
    if (this.replacement) {
      this.replacement.destroy();
      return;
    }
    if (this.destroyed) return;
    this.destroyed = true;
    cancelAnimationFrame(this.frame);
    this.resizeObserver?.disconnect();
    this.listeners.forEach((remove) => remove());
    this.listeners = [];
    this._disposeGraphics();
    this.host.remove();
    this.unlockScroll?.();
    this.options.onDestroy?.();
  }
}
