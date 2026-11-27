import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { createLivingBruce } from "./bruceLiving.js";
import { mountBruceChatBar } from "./bruceChatUi.js";
import { FLOOR_PRESETS, computeDuplexCameraPose } from "./duplexCamMath.js";
import { createOldMoneyTv } from "./oldMoneyTv.js";
import { createTerraceVista } from "./terraceVista.js";
import { createLuckyMeteorController } from "./luckyMeteor.js";
import { sfx } from "../audio.js";
import { feedback } from "../juice.js";

const ACTIVITY_DEFS = {
  home_brush: {
    id: "home_brush",
    floor: "1f",
    title: "露台阳光顺毛",
    win: 11,
    fail: -13,
    swapProb: 0,
    camPos: new THREE.Vector3(2.8, 2.8, 8.8),
    camTarget: new THREE.Vector3(1.4, 1.15, 3.8),
  },
  home_rain_vinyl: {
    id: "home_rain_vinyl",
    floor: "2f",
    title: "阁楼黑胶时光",
    win: 12,
    fail: -12,
    swapProb: 0,
    camPos: new THREE.Vector3(-4.4, 12.1, -4.4),
    camTarget: new THREE.Vector3(-10.8, 10.3, -9.8),
  },
  home_hide_seek: {
    id: "home_hide_seek",
    floor: "1f",
    title: "客厅抛球寻宝",
    win: 12,
    fail: -14,
    swapProb: 0.12,
    camPos: new THREE.Vector3(4.8, 4.2, 10.4),
    camTarget: new THREE.Vector3(1.4, 1.0, 2.4),
  },
};

const HOTSPOTS = [
  {
    id: "home_brush",
    kind: "act",
    title: "阳光顺毛",
    sub: "+11 分 · 丝毛护理",
    pos: [2.2, 1.6, 3.8],
    icon: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 19l11-11"/><path d="M13 5l6 6"/><path d="M11 7l5 5"/><path d="M9 9l5 5"/><path d="M18 3v2M21 6h-2"/></svg>`,
  },
  {
    id: "home_rain_vinyl",
    kind: "act",
    title: "阁楼黑胶",
    sub: "+12 分 · 2F 午后 33RPM",
    pos: [-12.0, 11.2, -10.8],
    icon: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2.2"/><path d="M18 5l-3 5" stroke-linecap="round"/></svg>`,
  },
  {
    id: "home_hide_seek",
    kind: "act",
    title: "客厅抛球",
    sub: "+12 分 · 12% 换分",
    pos: [5.0, 1.0, 2.8],
    icon: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="8"/><path d="M6.5 7.5c3 3 3 6 0 9M17.5 7.5c-3 3-3 6 0 9"/></svg>`,
  },
  {
    id: "street",
    kind: "teleport",
    title: "出门 · 海岸烘焙室",
    sub: "手冲吧台与海平线",
    code: "OUT·01",
    pos: [-14.0, 3.6, 2.2],
    icon: `<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 10l2-5h12l2 5"/><path d="M5 10v9h14v-9"/><path d="M10 19v-5h4v5"/></svg>`,
  },
  {
    id: "warehouse",
    kind: "teleport",
    title: "出门 · ELOWEN 有机市集",
    sub: "野生帝王鲑与冷柜鲜食",
    code: "ELW·02",
    pos: [-13.9, 1.85, 6.4],
    icon: `<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="9" cy="19" r="1.5"/><circle cx="17" cy="19" r="1.5"/><path d="M3 5h3l2.2 10h9.8l2-7H7"/></svg>`,
  },
  {
    id: "global",
    kind: "teleport",
    title: "传送 · 环球旅行",
    sub: "北欧 / 海岸 / 游艇",
    code: "FLY·04",
    pos: [-14.0, 13.5, -4.6],
    icon: `<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 2l2.6 7.4L22 12l-7.4 2.6L12 22l-2.6-7.4L2 12l7.4-2.6z"/></svg>`,
  },
];

function pickRandom(arr, fallback = "") {
  if (!Array.isArray(arr) || !arr.length) return fallback;
  return arr[Math.floor(Math.random() * arr.length)];
}

const DEFAULT_HUB_COPY = {
  thought_bubbles: {
    idle_happy: [
      "落地窗外的蓝天白云洒在洞石地毯上，晒得奶油毛暖洋洋的。",
      "双层挑空大客厅今天风好轻，点右侧按钮还能陪我上二楼阁楼！",
      "酒红丝巾刚整理好，随时准备出门巡街或者晒露台太阳。",
    ],
    idle_sulk: [
      "哼，幸福指数跌破 80 了，我现在只认零食说话。",
      "把头扭过去十秒钟，除非拿牛肉干来哄我。",
    ],
    floor_1f_greet: [
      "哒哒哒踩着暖光楼梯跑回一楼挑空客厅啦！落地窗外一片蔚蓝！",
      "羊羔绒沙发和洞石茶几晒得好暖和，今天在一楼陪我丢球吧？",
    ],
    floor_2f_greet: [
      "欢迎登上二楼阳光阁楼！玻璃护栏外面视野超棒，还有我的丝绒窝～",
      "二楼摆着黑胶唱片机和巨幅帆船赛油画，靠在这里晒太阳最惬意了。",
    ],
    terrace_greet: [
      "穿过敞开的玻璃移门出来啦！坐在这张软绵绵的羊羔绒沙发上看海落日好舒服。",
      "夕阳把海面染成香槟金色，海鸥从栏杆外掠过，海风吹起酒红丝巾了～",
    ],
    lucky_meteor: [
      "快看海平线上那道流星！布鲁斯摇着尾巴替你许愿，幸运指数加了一个吉利数字！",
      "暮色里流星悄然掠过，这一定是今天最治愈的幸运时刻。",
    ],
    tv_art_swap: [
      "点击切换私享频道——古典帆船赛、拍场名作、草地马术还是烛光室内乐？",
      "亚麻声学格栅下方流淌着画面与乐声，这间客厅就是本汪的私人放映厅。",
    ],
    patron_card_depart: [
      "对纹大理石壁灯亮起，白兰地皮托盘上，07号卡片静候。",
      "白兰花影里，皮托盘托着07号卡，门厅灯已暖。",
      "门厅灯光转暖，白兰地皮托盘上07号卡泛着微光。"
    ],
    concierge_call: [
      "轻按黄铜对讲器，B1 司机车已备妥，随时可以出发。",
      "晚间餐点已备好，布鲁斯正凑在依云玻璃水瓶旁嗅闻。",
      "大理石桌旁轻点一下，管家与司机均已在岗候命。"
    ],
    hifi_toggle: [
      "轻触烟色玻璃穹顶，哈曼音室暖晕如环抱般亮起。",
      "半透声学穹顶透出微光，低音在人字拼橡木地上轻漾。",
      "指尖轻叩音柱，360度暖光环与澄澈中频温柔铺开。"
    ],
    fireplace_warm: [
      "劈好的橡木柴在火膛里轻响，橙色余烬缓缓跳跃。",
      "布鲁斯蜷在罗马洞石壁炉边，歪头看跃动的橡木火光。",
      "壁炉里的实木新炭正旺，琥珀暖意漫过整面石沿。"
    ],
    butler_water_lines: [
      "管家旋开冰镇燧石玻璃瓶盖，水珠沿瓶身滑落，在洞石桌面上洇开一小片深色。",
      "水晶杯壁凝着细密水雾，布鲁斯踱过来，酒红围巾角轻轻扫过胡桃木桌沿。",
      "他把杯子往桌心推了推，布鲁斯低头嗅了嗅杯口，围巾穗子垂在洞石上。",
      "冰水注入杯中发出细响，布鲁斯歪头看着气泡上升，酒红围巾映着窗光。"
    ],
    butler_pantry_lines: [
      "管家拉开冷藏抽屉，冷气漫过指尖，布鲁斯在脚边仰头等着那几片切好的肉。",
      "瓷碟里码着薄切冷肉，布鲁斯鼻尖凑近碟沿，围巾一角搭在胡桃木柜门上。"
    ],
    chauffeur_cafe_lines: [
      "B1 门廊传来短促信号，车已泊在楼下，海岸烘焙室的香气正温着等候。",
      "司机发来消息：车头朝外，暖风已开，准备出发前往海岸烘焙室。"
    ],
    chauffeur_market_lines: [
      "B1 门廊里司机靠着车门，手边备好冷柜冰袋，只等拿上 07 号宅卡出发 ELOWEN。",
      "地下门廊回声很轻，07 号宅卡从玄关托盘拾起，司机已准备驶向 ELOWEN 市集。"
    ],
    chauffeur_marina_lines: [
      "司机接通白帆游艇码头泊位长，柚木栈桥晒得暖烘烘，海风正好。",
      "泊位长传来消息：海风清透，私家浮桥与单桅帆船正待靠岸登船。"
    ],
    hifi_on_lines: [
      "烟色玻璃穹顶亮起暖光，电钢琴的爵士音符不紧不慢地铺满客厅。",
      "哈曼烟色玻璃罩微微发热，琴键声像午后光线一样缓缓漫过胡桃木地板。"
    ],
    hifi_off_lines: [
      "声场缓缓收拢，最后一个琴音沉入午后，客厅只剩窗外的海风。",
      "烟色玻璃穹顶暗下去，电钢琴余韵散尽，布鲁斯在洞石地面上趴平身子。"
    ],
    lamp_toggle: [
      "香槟金钓鱼灯一亮，整个大理石客厅瞬间温柔起来啦。",
      "啪嗒切换客厅光影模式！你喜欢亮堂日光还是暖灯氛围？",
    ],
    click_poke: [
      "干嘛戳我软乎乎的耳朵，顺毛要从头顶开始！",
      "嘿嘿，被你抓到一只刚晒暖的奶油腊肠犬。",
      "再来一下我就要原地起跳转圈圈了哦！",
    ],
    click_poke_sulk: [
      "别戳啦，冷战期的小狗很有原则的……除非加肉。",
      "尾巴才没有偷偷动一下，哼。",
    ],
    petting_bliss: [
      "就是这个力度，耳朵后面再多顺两下～",
      "呼噜呼噜，奶油长毛都要顺滑到反光啦。",
    ],
    ear_warn: [
      "哎呀太快了！飞机耳预警，快松手让我缓一秒！",
    ],
    rain_cozy: [
      "羊绒毯铺在脚边，午后斜阳刚好落在黑胶唱机上。",
      "33 转头版爵士慢悠悠转起来，整个阁楼都是琥珀暖调。",
    ],
    ball_excited: [
      "看我的短腿冲刺！这颗网球归我了！",
    ],
    walk_call: [
      "听见喊我啦，四条小短腿这就哒哒哒走过来！",
      "橡木地板踩起来沙沙响，先过去巡视一下你的脚边。",
    ],
    walk_sulk: [
      "虽、虽然还在冷战，但我可以勉为其难挪过去几步看看……",
    ],
    roll_over: [
      "原地躺倒晒肚皮！四只小爪子在半空划水表示超开心！",
      "呼噜翻个身滚一滚，奶油长毛也要均匀晒到阳光。",
    ],
    lick_paw: [
      "先把右前爪认真舔得干干净净，精致腊肠绝不敷衍！",
      "舔舔小爪子，刚刚的牛肉香好像还留了一点点～",
    ],
    play_bow: [
      "前胸贴地、屁股高高撅起——本汪正式发出邀请信号！",
      "伸一个长长的懒腰，尾巴已经切换成高速马达模式啦！",
    ],
    airplane_ears: [
      "耳朵向后收平启动飞机耳模式，本汪有点小委屈了哦……",
    ],
  },
  portal_hover: {
    street: "阳光正好，去海岸烘焙室喝一杯山羊奶微泡吧。",
    warehouse: "玄关洞石托盘上的 07 号卡准备好了，去 ELOWEN 挑野生帝王鲑？",
    global: "二楼相框里藏着好多远方，下一站想带我去哪里？",
  },
};

export function mountLivingRoomHub(container, opts = {}) {
  let sulking = Boolean(opts.sulking);
  let content = opts.content || {};
  let happiness = opts.happiness ?? 100;
  let hubCopy = DEFAULT_HUB_COPY;

  document.body.classList.add("is-hub3d-view");
  document.body.classList.remove("is-hub3d-act");

  fetch("./data/hub_deepseek.json")
    .then((r) => (r.ok ? r.json() : null))
    .then((json) => {
      if (!destroyed && json?.thought_bubbles) {
        hubCopy = {
          ...DEFAULT_HUB_COPY,
          ...json,
          thought_bubbles: { ...DEFAULT_HUB_COPY.thought_bubbles, ...json.thought_bubbles },
          portal_hover: { ...DEFAULT_HUB_COPY.portal_hover, ...(json.portal_hover || {}) },
        };
      }
    })
    .catch(() => {});

  let destroyed = false;
  let rafId = null;
  let activeActId = null;
  let actCleanup = null;
  let camTween = null;

  const timers = new Set();
  const cleanups = [];
  const particles = [];

  const later = (fn, ms) => {
    const id = setTimeout(() => {
      timers.delete(id);
      if (!destroyed) fn();
    }, ms);
    timers.add(id);
    return id;
  };

  container.innerHTML = `
    <div class="hub3d-wrap">
      <div class="hub3d-stage">
        <canvas class="hub3d-canvas"></canvas>
        <div class="hub3d-vignette ${sulking ? "is-sulk" : ""}"></div>
        <canvas class="hub3d-fx-canvas" aria-hidden="true"></canvas>
        <div class="hub3d-viewfinder" aria-hidden="true">
          <span class="vf-corner vf-tl"></span>
          <span class="vf-corner vf-tr"></span>
          <span class="vf-corner vf-bl"></span>
          <span class="vf-corner vf-br"></span>
          <span class="vf-stamp">PH·01 · SUNLIT DUPLEX · 1F/2F</span>
        </div>
        <div class="hub3d-pins"></div>
        <div class="hub3d-floor-switch" role="group" aria-label="楼层视角切换">
          <button type="button" class="floor-pill" data-floor="2f">
            <span class="floor-pill-code">2F · LOFT</span>
            <span class="floor-pill-name">阳光阁楼</span>
          </button>
          <button type="button" class="floor-pill is-active" data-floor="1f">
            <span class="floor-pill-code">1F · SALON</span>
            <span class="floor-pill-name">挑空客厅</span>
          </button>
          <button type="button" class="floor-pill" data-floor="terrace">
            <span class="floor-pill-code">1F · TERRACE</span>
            <span class="floor-pill-name">露台看海</span>
          </button>
        </div>
        <div class="hub3d-tv-osd" id="hub3d-tv-osd" aria-live="polite">
          <div class="tv-osd-code" id="tv-osd-code">CH 01 · REGATTA</div>
          <div class="tv-osd-title" id="tv-osd-title">地中海古典 J-Class 帆船赛</div>
        </div>
        <div class="hub3d-lucky-toast" id="hub3d-lucky-toast" role="status" aria-live="polite">
          <span class="lucky-star-badge" aria-hidden="true">✦</span>
          <div class="lucky-toast-body">
            <div class="lucky-toast-title">幸运时刻 · 流星掠过海平线</div>
            <div class="lucky-toast-sub" id="hub3d-lucky-sub">布鲁斯仰头许愿 · 幸福指数 +18</div>
          </div>
        </div>
        <div class="hub3d-keyholder">
          <button type="button" class="keyholder-btn" aria-expanded="false">
            <span class="keyholder-fob" aria-hidden="true">🔑</span>
            <span>出门钥匙夹</span>
            <span class="keyholder-count">4</span>
          </button>
          <div class="keyholder-tray" role="menu" aria-label="出门传送目的地">
            <div class="keyholder-tray-head">
              <span>OUTING KEY HOLDER</span>
              <span>内线 / 出门</span>
            </div>
          </div>
        </div>
        <div class="hub3d-concierge-popover" id="hub3d-concierge-popover" role="dialog" aria-label="管家与专车内线" aria-hidden="true">
          <div class="concierge-head">
            <div>
              <div class="concierge-kicker" id="concierge-floor-label">HOUSE CONCIERGE · 1F SALON</div>
              <div class="concierge-title">宅邸管家与 B1 车队内线</div>
            </div>
            <button type="button" class="concierge-close" id="btn-concierge-close" aria-label="关闭内线面板">×</button>
          </div>
          <div class="concierge-grid">
            <button type="button" class="concierge-action-btn" data-concierge="water">
              <span class="concierge-act-main">
                <span class="concierge-act-name">管家侍水 · 现开冰镇依云</span>
                <span class="concierge-act-sub">燧石玻璃瓶注入水晶杯 · 唤布鲁斯凑近桌旁</span>
              </span>
              <span class="concierge-act-tag">SERVICE</span>
            </button>
            <button type="button" class="concierge-action-btn" data-concierge="hifi" id="btn-concierge-hifi">
              <span class="concierge-act-main">
                <span class="concierge-act-name">哈曼声场 · 午后爵士四和弦</span>
                <span class="concierge-act-sub">烟色琉璃音室暖晕 · 控制客厅与阁楼漫反射乐声</span>
              </span>
              <span class="concierge-act-tag" id="concierge-hifi-tag">STANDBY</span>
            </button>
            <button type="button" class="concierge-action-btn" data-concierge="mood" id="btn-concierge-mood">
              <span class="concierge-act-main">
                <span class="concierge-act-name">光影情景 · 落日夕照 ⇄ 暮色微醺</span>
                <span class="concierge-act-sub">点亮落地灯与露台灯笼 · 暮色下流星邂逅率翻倍</span>
              </span>
              <span class="concierge-act-tag" id="concierge-mood-tag">SUNSET</span>
            </button>
            <button type="button" class="concierge-action-btn" data-concierge="tv" id="btn-concierge-tv">
              <span class="concierge-act-main">
                <span class="concierge-act-name">墙面放映 · 切换老钱私享频道</span>
                <span class="concierge-act-sub">帆船赛实况 / 拍场名作预展 / 马术大奖赛 / 室内大提琴</span>
              </span>
              <span class="concierge-act-tag" id="concierge-tv-tag">CH 01</span>
            </button>
            <button type="button" class="concierge-action-btn" data-concierge="chauffeur-cafe">
              <span class="concierge-act-main">
                <span class="concierge-act-name">B1 专车 · 海岸烘焙室</span>
                <span class="concierge-act-sub">司机已就位 · 前往山羊奶微泡吧台</span>
              </span>
              <span class="concierge-act-tag">OUT·01</span>
            </button>
            <button type="button" class="concierge-action-btn" data-concierge="chauffeur-market">
              <span class="concierge-act-main">
                <span class="concierge-act-name">B1 专车 · 携 07 号卡赴 ELOWEN</span>
                <span class="concierge-act-sub">先入玄关拾起宅卡 · 直达有机买手食集</span>
              </span>
              <span class="concierge-act-tag">ELW·02</span>
            </button>
            <button type="button" class="concierge-action-btn" data-concierge="chauffeur-marina">
              <span class="concierge-act-main">
                <span class="concierge-act-name">私人泊位 · 游艇与远航专线</span>
                <span class="concierge-act-sub">联络泊位长 · 查看白帆码头与远途航线</span>
              </span>
              <span class="concierge-act-tag">FLY·04</span>
            </button>
            <button type="button" class="concierge-pantry-cta hidden" id="btn-concierge-pantry">
              布鲁斯低于 80 分 · 前往私厨鲜食冷柜挑一份手感鲜食 →
            </button>
          </div>
        </div>
        <div class="hub3d-speech" aria-live="polite">
          <span class="speech-cue"></span>
          <span class="speech-line"></span>
        </div>
        <div class="hub3d-tricks-bar" role="toolbar" aria-label="与布鲁斯互动动作">
          <button type="button" class="trick-pill" data-trick="walk">
            <svg class="trick-ico" viewBox="0 0 24 24" width="13" height="13" fill="currentColor" aria-hidden="true"><circle cx="7" cy="8.5" r="1.8"/><circle cx="12" cy="6.5" r="1.8"/><circle cx="17" cy="8.5" r="1.8"/><path d="M12 11.2c-3 0-5.2 2.4-5.2 4.7 0 1.4 1 2.4 2.4 2.4.9 0 1.8-.35 2.8-.35s1.9.35 2.8.35c1.4 0 2.4-1 2.4-2.4 0-2.3-2.2-4.7-5.2-4.7z"/></svg>
            <span>唤过来</span>
          </button>
          <button type="button" class="trick-pill" data-trick="roll_over">肚皮打滚</button>
          <button type="button" class="trick-pill" data-trick="lick_paw">舔小爪子</button>
          <button type="button" class="trick-pill" data-trick="play_bow">伸个懒腰</button>
          <button type="button" class="trick-pill" data-trick="airplane_ears">委屈飞机耳</button>
          <button type="button" class="trick-pill is-ai-chat" id="hub3d-btn-chat">✦ 逗它说话</button>
        </div>
        <button type="button" class="hub3d-reset-btn">⌖ 归中视角</button>

        <div class="hub3d-act-overlay">
          <div class="hub3d-act-top">
            <button type="button" class="hub3d-glass-pill" id="hub3d-btn-back">回到客厅全景</button>
            <button type="button" class="hub3d-glass-pill" id="hub3d-btn-auto">自动演示</button>
          </div>
          <div class="hub3d-act-prompt"></div>
          <div class="hub3d-act-body"></div>
        </div>

        <div class="hub3d-swap-banner">
          <div style="font-size:12px;letter-spacing:0.1em;color:#FFE7A8;margin-bottom:4px;">高位交换 · 幸运降临</div>
          <div class="hub3d-swap-num">100</div>
          <div class="hub3d-swap-msg" style="font-size:13.5px;margin-top:4px;"></div>
        </div>

        <section class="hub3d-settle" aria-live="polite">
          <div class="hub3d-settle-head">
            <span class="hub3d-settle-title" style="font-size:12px;color:rgba(255,244,218,0.8)"></span>
            <span class="hub3d-settle-delta"></span>
          </div>
          <p class="hub3d-settle-line"></p>
          <p class="hub3d-settle-status"></p>
          <div class="hub3d-settle-actions">
            <button type="button" class="th-btn-primary" id="hub3d-btn-replay">再来一次</button>
            <button type="button" class="th-btn-ghost" id="hub3d-btn-done">回到客厅全景</button>
          </div>
        </section>

        <div class="hub3d-loading">
          <span>正在走进布鲁斯的阳光客厅……</span>
        </div>
      </div>
      <p class="hub3d-hint">轻点地面唤布鲁斯 · 点桌面对讲机呼管家与专车 · 点壁炉/哈曼音响/画框皆可互动</p>
    </div>
  `;

  const stageEl = container.querySelector(".hub3d-stage");
  const canvas = container.querySelector(".hub3d-canvas");
  const fxCanvas = container.querySelector(".hub3d-fx-canvas");
  const vignetteEl = container.querySelector(".hub3d-vignette");
  const pinsLayer = container.querySelector(".hub3d-pins");
  const floorSwitchEl = container.querySelector(".hub3d-floor-switch");
  const floorButtons = Array.from(container.querySelectorAll(".floor-pill[data-floor]"));
  const keyholderEl = container.querySelector(".hub3d-keyholder");
  const keyholderBtn = container.querySelector(".keyholder-btn");
  const keyholderTray = container.querySelector(".keyholder-tray");
  const conciergePopoverEl = container.querySelector("#hub3d-concierge-popover");
  const conciergeFloorLabelEl = container.querySelector("#concierge-floor-label");
  const conciergeCloseBtn = container.querySelector("#btn-concierge-close");
  const conciergeHifiBtn = container.querySelector("#btn-concierge-hifi");
  const conciergeHifiTag = container.querySelector("#concierge-hifi-tag");
  const conciergeMoodTag = container.querySelector("#concierge-mood-tag");
  const conciergeTvTag = container.querySelector("#concierge-tv-tag");
  const conciergePantryBtn = container.querySelector("#btn-concierge-pantry");
  const tvOsdEl = container.querySelector("#hub3d-tv-osd");
  const tvOsdCodeEl = container.querySelector("#tv-osd-code");
  const tvOsdTitleEl = container.querySelector("#tv-osd-title");
  const luckyToastEl = container.querySelector("#hub3d-lucky-toast");
  const luckySubEl = container.querySelector("#hub3d-lucky-sub");
  const speechEl = container.querySelector(".hub3d-speech");
  const speechCueEl = speechEl?.querySelector(".speech-cue");
  const speechLineEl = speechEl?.querySelector(".speech-line");
  const resetBtn = container.querySelector(".hub3d-reset-btn");
  const loadingEl = container.querySelector(".hub3d-loading");
  const actOverlay = container.querySelector(".hub3d-act-overlay");
  const actPromptEl = container.querySelector(".hub3d-act-prompt");
  const actBodyEl = container.querySelector(".hub3d-act-body");
  const btnActBack = container.querySelector("#hub3d-btn-back");
  const btnActAuto = container.querySelector("#hub3d-btn-auto");
  const settleEl = container.querySelector(".hub3d-settle");
  const btnReplay = container.querySelector("#hub3d-btn-replay");
  const btnDone = container.querySelector("#hub3d-btn-done");
  const swapBanner = container.querySelector(".hub3d-swap-banner");
  const swapNumEl = container.querySelector(".hub3d-swap-num");
  const swapMsgEl = container.querySelector(".hub3d-swap-msg");

  let activeFloor = opts.restoreAnchor?.floor && FLOOR_PRESETS[opts.restoreAnchor.floor]
    ? opts.restoreAnchor.floor
    : "1f";
  const getFloorOverview = (fl = activeFloor) => {
    const preset = FLOOR_PRESETS[fl] || FLOOR_PRESETS["1f"];
    return {
      preset,
      cam: new THREE.Vector3(...preset.camPos),
      target: new THREE.Vector3(...preset.target),
    };
  };

  // Create Three.js renderer + scene + camera
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.12;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(sulking ? 0x2b3b4e : 0xdbeeff);

  // Procedural warm sunlit interior IBL so metallic brass/walnut/chrome gleams naturally
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envScene = new THREE.Scene();
  envScene.background = new THREE.Color(0xf6f1e8);
  const envRoom = new THREE.Mesh(
    new THREE.BoxGeometry(26, 18, 26),
    new THREE.MeshBasicMaterial({ color: 0xf2ebe0, side: THREE.BackSide }),
  );
  const envSky = new THREE.Mesh(
    new THREE.PlaneGeometry(24, 16),
    new THREE.MeshBasicMaterial({ color: 0xd9ecff }),
  );
  envSky.position.set(0, 6, -12.5);
  envScene.add(envRoom, envSky);
  const envRT = pmrem.fromScene(envScene, 0.04);
  scene.environment = envRT.texture;
  pmrem.dispose();
  envRoom.geometry.dispose();
  envRoom.material.dispose();
  envSky.geometry.dispose();
  envSky.material.dispose();

  // Preload 4K sunny sky, rainy sky, and 3 clickable Gallery Frame Art TV paintings
  const texLoader = new THREE.TextureLoader();
  const loadSrgbTex = (url, flipY = false) => {
    const t = texLoader.load(url);
    t.colorSpace = THREE.SRGBColorSpace;
    t.flipY = flipY;
    return t;
  };
  const sunnySkyTex = loadSrgbTex("./assets/textures/sky_sunset.jpg", false);
  const rainySkyTex = loadSrgbTex("./assets/textures/sky_rainy.jpg", false);
  const patronCardTex = loadSrgbTex("./assets/textures/patron_card.jpg", false);
  const flameTex = loadSrgbTex("./assets/textures/fireplace_flame.png", true);
  const oldMoneyTv = createOldMoneyTv();
  const terraceVista = createTerraceVista(scene);
  let tvOsdTimer = null;
  let luckyToastTimer = null;
  let duskMode = false;
  let salonLampOn = false;
  let skyCycloramaMat = null;
  let tvScreenMesh = null;
  let tvScreenMat = null;
  let arcLampMesh = null;
  const lampClickMeshes = [];
  let patronCardMesh = null;
  let patronCardMat = null;
  let fireplaceEmberMesh = null;
  const conciergeMeshes = [];
  const hifiMeshes = [];
  const hifiHaloMats = [];
  const fireplaceMeshes = [];
  let departSkipFn = null;

  const initOv = getFloorOverview(activeFloor);
  const camera = new THREE.PerspectiveCamera(48, 16 / 10, 0.2, 320);
  if (Array.isArray(opts.restoreAnchor?.camPos)) camera.position.fromArray(opts.restoreAnchor.camPos);
  else camera.position.copy(initOv.cam);

  const controls = new OrbitControls(camera, canvas);
  if (Array.isArray(opts.restoreAnchor?.target)) controls.target.fromArray(opts.restoreAnchor.target);
  else controls.target.copy(initOv.target);
  controls.enableDamping = true;
  controls.dampingFactor = 0.07;
  controls.enablePan = false;
  controls.minDistance = 3.2;
  controls.maxDistance = 24.0;
  controls.minPolarAngle = 0.48;
  controls.maxPolarAngle = 1.56;
  controls.minAzimuthAngle = -Infinity;
  controls.maxAzimuthAngle = Infinity;
  controls.update();

  // Warm sunset & dusk penthouse lighting
  const hemiLight = new THREE.HemisphereLight(0xfff1dc, 0xcab8a2, 1.45);
  scene.add(hemiLight);

  const ambientLight = new THREE.AmbientLight(0xfff3e2, 0.72);
  scene.add(ambientLight);

  const sunLight = new THREE.DirectionalLight(0xffcf94, 2.25);
  sunLight.position.set(-4, 15, -28);
  sunLight.target.position.set(2, 0, 2);
  sunLight.castShadow = true;
  sunLight.shadow.mapSize.set(1024, 1024);
  sunLight.shadow.camera.near = 2;
  sunLight.shadow.camera.far = 56;
  sunLight.shadow.camera.left = -18;
  sunLight.shadow.camera.right = 18;
  sunLight.shadow.camera.top = 18;
  sunLight.shadow.camera.bottom = -18;
  sunLight.shadow.bias = -0.0005;
  scene.add(sunLight, sunLight.target);

  const warmLampLight = new THREE.PointLight(0xffb969, 0.9, 24, 1.35);
  warmLampLight.position.set(11.75, 3.68, 4.70);
  scene.add(warmLampLight);

  // Grand Foyer console & bronze mirror warm wash light
  const foyerSpotLight = new THREE.PointLight(0xffe6bf, 1.55, 14, 1.3);
  foyerSpotLight.position.set(-12.2, 4.8, 6.6);
  scene.add(foyerSpotLight);

  // Dynamic Wood-Burning Fireplace Rig (1F Hearth: X=14.02, Y=1.70, Z=-3.5..-0.1)
  const fireplaceLight = new THREE.PointLight(0xff7d2b, 2.35, 17, 1.35);
  fireplaceLight.position.set(13.25, 2.08, -1.8);
  scene.add(fireplaceLight);

  const flameGroup = new THREE.Group();
  const flameGeo = new THREE.PlaneGeometry(0.62, 0.72);
  const flameMats = [];
  const flameRibbons = [];
  const flameZList = [-3.42, -2.90, -2.36, -1.80, -1.24, -0.70, -0.18];
  for (let i = 0; i < flameZList.length; i++) {
    const fm = new THREE.MeshBasicMaterial({
      map: flameTex,
      transparent: true,
      opacity: 0.88,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      side: THREE.DoubleSide,
      toneMapped: false,
    });
    const mesh = new THREE.Mesh(flameGeo, fm);
    const fz = flameZList[i];
    const fx = 13.68 + ((i % 2 === 0 ? -1 : 1) * 0.05);
    mesh.position.set(fx, 1.98, fz);
    mesh.rotation.y = -Math.PI * 0.5 + (i % 3 - 1) * 0.16;
    flameGroup.add(mesh);
    flameMats.push(fm);
    flameRibbons.push({
      mesh,
      mat: fm,
      baseX: fx,
      baseZ: fz,
      phase: i * 1.17,
      speed: 5.8 + (i % 3) * 1.4,
      baseScale: 0.88 + (i % 3) * 0.14,
    });
  }
  scene.add(flameGroup);

  const sparkCount = 28;
  const sparkPos = new Float32Array(sparkCount * 3);
  const sparkMeta = [];
  for (let i = 0; i < sparkCount; i++) {
    const sx = 13.56 + ((i * 0.11) % 0.34);
    const sy = 1.66 + ((i * 0.27) % 0.72);
    const sz = -3.70 + ((i * 0.43) % 3.80);
    sparkPos[i * 3] = sx;
    sparkPos[i * 3 + 1] = sy;
    sparkPos[i * 3 + 2] = sz;
    sparkMeta.push({ baseX: sx, baseZ: sz, speed: 0.48 + (i % 5) * 0.14, phase: i * 0.73 });
  }
  const sparkGeo = new THREE.BufferGeometry();
  sparkGeo.setAttribute("position", new THREE.BufferAttribute(sparkPos, 3));
  const sparkMat = new THREE.PointsMaterial({
    color: 0xffa63d,
    size: 0.068,
    transparent: true,
    opacity: 0.88,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });
  const sparkPoints = new THREE.Points(sparkGeo, sparkMat);
  scene.add(sparkPoints);

  // Subtle floating sunlit dust motes in the double-height atrium
  const moteCount = 42;
  const motePos = new Float32Array(moteCount * 3);
  for (let i = 0; i < moteCount; i++) {
    motePos[i * 3] = -10 + ((i * 2.13) % 21);
    motePos[i * 3 + 1] = 1.2 + ((i * 2.47) % 13.5);
    motePos[i * 3 + 2] = -13 + ((i * 1.97) % 19);
  }
  const moteGeo = new THREE.BufferGeometry();
  moteGeo.setAttribute("position", new THREE.BufferAttribute(motePos, 3));
  const moteMat = new THREE.PointsMaterial({
    color: 0xfff3cf,
    size: 0.14,
    transparent: true,
    opacity: 0.52,
    depthWrite: false,
  });
  const motePoints = new THREE.Points(moteGeo, moteMat);
  scene.add(motePoints);

  // Rain streaks right outside the double-height curtain wall (for <80 sulk or rainVinyl)
  const rainCount = 96;
  const rainPos = new Float32Array(rainCount * 3);
  for (let i = 0; i < rainCount; i++) {
    rainPos[i * 3] = -14 + ((i * 2.71) % 28);
    rainPos[i * 3 + 1] = 0.5 + ((i * 3.17) % 17.5);
    rainPos[i * 3 + 2] = -15.6 + ((i * 0.37) % 1.4);
  }
  const rainGeo = new THREE.BufferGeometry();
  rainGeo.setAttribute("position", new THREE.BufferAttribute(rainPos, 3));
  const rainMat = new THREE.PointsMaterial({
    color: 0xbcd8f8,
    size: 0.17,
    transparent: true,
    opacity: 0.68,
    depthWrite: false,
  });
  const rainPoints = new THREE.Points(rainGeo, rainMat);
  rainPoints.visible = sulking;
  scene.add(rainPoints);

  // 3D Tennis ball for fetch activity
  const ballGeo = new THREE.SphereGeometry(0.38, 24, 18);
  const ballMat = new THREE.MeshStandardMaterial({ color: 0xd9ef42, roughness: 0.72, metalness: 0.0 });
  const tennisBall = new THREE.Mesh(ballGeo, ballMat);
  tennisBall.castShadow = true;
  tennisBall.visible = false;
  scene.add(tennisBall);

  // 3D Golden swap halo rings around Bruce
  const swapRingsGroup = new THREE.Group();
  swapRingsGroup.position.set(initOv.preset.brucePos[0], initOv.preset.brucePos[1] + 1.1, initOv.preset.brucePos[2]);
  swapRingsGroup.visible = false;
  const swapRingGeos = [];
  const swapRingMats = [];
  for (let i = 0; i < 4; i++) {
    const rg = new THREE.TorusGeometry(1.6 + i * 0.34, 0.04, 10, 64);
    const rm = new THREE.MeshBasicMaterial({ color: 0xf7d788, transparent: true, opacity: 0.75 });
    const mesh = new THREE.Mesh(rg, rm);
    mesh.rotation.set(Math.PI * 0.42 + i * 0.3, i * 0.6, 0);
    swapRingsGroup.add(mesh);
    swapRingGeos.push(rg);
    swapRingMats.push(rm);
  }
  scene.add(swapRingsGroup);

  // Living 86-bone Bruce positioned cleanly on 1F sunlit rug (or restored anchor)
  const bruce = createLivingBruce({ modelUrl: "./assets/models/bruce_rigged.glb", height: 2.55 });
  if (Array.isArray(opts.restoreAnchor?.brucePos)) bruce.root.position.fromArray(opts.restoreAnchor.brucePos);
  else bruce.root.position.set(...initOv.preset.brucePos);
  bruce.root.rotation.y = Number.isFinite(opts.restoreAnchor?.bruceRot)
    ? opts.restoreAnchor.bruceRot
    : initOv.preset.bruceRot;
  bruce.setMood(sulking ? "sulk" : "happy");
  scene.add(bruce.root);

  // Champagne-gold floor click ripple indicator for Walk-to navigation
  const rippleGeo = new THREE.RingGeometry(0.16, 0.24, 32);
  rippleGeo.rotateX(-Math.PI / 2);
  const rippleMat = new THREE.MeshBasicMaterial({
    color: 0xf4d48c,
    transparent: true,
    opacity: 0,
    depthWrite: false,
    side: THREE.DoubleSide,
  });
  const rippleMesh = new THREE.Mesh(rippleGeo, rippleMat);
  rippleMesh.position.set(initOv.preset.brucePos[0], initOv.preset.floorY + 0.025, initOv.preset.brucePos[2]);
  rippleMesh.visible = false;
  scene.add(rippleMesh);
  let rippleAge = -1;

  function triggerFloorRipple(x, z) {
    const fy = getFloorOverview().preset.floorY;
    rippleMesh.position.set(x, fy + 0.025, z);
    rippleMesh.scale.setScalar(0.6);
    rippleMesh.visible = true;
    rippleAge = 0;
  }

  // Load Two-Floor Luxury Penthouse Duplex GLB
  let roomRoot = null;
  const gltfLoader = new GLTFLoader();
  const roomReady = new Promise((resolve) => {
    gltfLoader.load(
      "./assets/models/penthouse_duplex.glb",
      (gltf) => {
        if (destroyed) return;
        roomRoot = gltf.scene;
        roomRoot.traverse((obj) => {
          if (!obj.isMesh) return;
          if (obj.name === "SkyCyclorama" || obj.material?.name === "SkyCycloramaSunny") {
            obj.castShadow = false;
            obj.receiveShadow = false;
            skyCycloramaMat = new THREE.MeshBasicMaterial({
              map: sulking ? rainySkyTex : sunnySkyTex,
              side: THREE.DoubleSide,
              toneMapped: false,
            });
            obj.material?.dispose?.();
            obj.material = skyCycloramaMat;
            return;
          }
          if (obj.name === "GalleryTVScreen") {
            obj.castShadow = false;
            obj.receiveShadow = false;
            tvScreenMesh = obj;
            tvScreenMat = new THREE.MeshBasicMaterial({
              map: oldMoneyTv.texture,
              toneMapped: false,
            });
            obj.material?.dispose?.();
            obj.material = tvScreenMat;
            return;
          }
          if (obj.name === "EntryPatronCard") {
            obj.castShadow = false;
            patronCardMesh = obj;
            patronCardMat = new THREE.MeshBasicMaterial({
              map: patronCardTex,
              side: THREE.DoubleSide,
              toneMapped: false,
            });
            obj.material?.dispose?.();
            obj.material = patronCardMat;
            return;
          }
          if (/^ArcLamp/i.test(obj.name)) {
            if (obj.name === "ArcLampBulb") arcLampMesh = obj;
            lampClickMeshes.push(obj);
          }
          if (obj.name === "FireplaceEmbers") {
            fireplaceEmberMesh = obj;
            fireplaceMeshes.push(obj);
          } else if (obj.name === "FireplaceLogs") {
            fireplaceMeshes.push(obj);
          } else if (/^Concierge(Pager|Screen)/i.test(obj.name)) {
            conciergeMeshes.push(obj);
          } else if (/^(HiFiTower|HiFiGlassDome|HiFiHaloRing|LoftAuraSpeaker)/i.test(obj.name)) {
            hifiMeshes.push(obj);
            if (/HaloRing/i.test(obj.name) && obj.material?.clone) {
              obj.material = obj.material.clone();
              hifiHaloMats.push(obj.material);
            }
          }
          const isGlass = /Glass/i.test(obj.name) || /Glass/i.test(obj.material?.name || "");
          obj.castShadow = !isGlass;
          obj.receiveShadow = !isGlass;
          const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
          mats.forEach((m) => {
            if (!m) return;
            if (m.map) m.map.colorSpace = THREE.SRGBColorSpace;
            if (m.emissiveMap) m.emissiveMap.colorSpace = THREE.SRGBColorSpace;
            m.needsUpdate = true;
          });
        });
        terraceVista.attachRoomRoot(roomRoot);
        terraceVista.setMood({ sulking, dusk: duskMode });
        scene.add(roomRoot);
        resolve(true);
      },
      undefined,
      (err) => {
        console.warn("penthouse_duplex.glb load error:", err);
        resolve(false);
      },
    );
  });

  Promise.all([roomReady, bruce.ready]).then(() => {
    if (!destroyed) {
      loadingEl.classList.add("is-hidden");
      later(() => {
        if (!activeActId) sayBruce(sulking ? "idle_sulk" : "idle_happy", 4400);
      }, 900);
    }
  });

  const SPEECH_CUES = {
    idle_happy: "BRUCE · 摇尾轻哼",
    idle_sulk: "BRUCE · 背身冷战中",
    floor_1f_greet: "BRUCE · 一楼阳光厅",
    floor_2f_greet: "BRUCE · 二楼私享阁楼",
    terrace_greet: "BRUCE · 夕照观海露台",
    lucky_meteor: "LUCKY · 海平线流星时刻",
    tv_art_swap: "BRUCE · 私享频道",
    patron_card_depart: "BRUCE · 玄关出发",
    concierge_call: "BRUCE · 管家专线",
    butler_water_lines: "CONCIERGE · 管家侍水",
    butler_pantry_lines: "CONCIERGE · 私厨备餐",
    chauffeur_cafe_lines: "CHAUFFEUR · B1 专车",
    chauffeur_market_lines: "CHAUFFEUR · B1 专车",
    chauffeur_marina_lines: "MARINA · 私人泊位",
    hifi_toggle: "BRUCE · 声学琉璃",
    hifi_on_lines: "HARMAN · 爵士声场开启",
    hifi_off_lines: "HARMAN · 声场静默",
    fireplace_warm: "BRUCE · 炉火微醺",
    lamp_toggle: "BRUCE · 暖光氛围",
    click_poke: "BRUCE · 歪头看你",
    click_poke_sulk: "BRUCE · 别扭哼声",
    petting_bliss: "BRUCE · 眯眼享受",
    ear_warn: "BRUCE · 飞机耳预警",
    rain_cozy: "BRUCE · 午后慢转",
    ball_excited: "BRUCE · 短腿蓄力",
    walk_call: "BRUCE · 小短腿巡步",
    walk_sulk: "BRUCE · 缓慢挪步",
    roll_over: "BRUCE · 翻肚皮打滚",
    lick_paw: "BRUCE · 精致舔爪",
    play_bow: "BRUCE · 撅屁股邀玩",
    airplane_ears: "BRUCE · 委屈飞机耳",
  };

  let speechTimer = null;
  let lastSpeechText = "";
  let lastSpeechAt = 0;
  function sayBruce(categoryOrText, durationMs = 3800, customCue = "") {
    if (!speechEl || !speechLineEl || destroyed) return;
    const pool = hubCopy?.thought_bubbles?.[categoryOrText];
    let text = "";
    if (Array.isArray(pool) && pool.length) {
      text = pickRandom(pool, "");
      if (text === lastSpeechText && pool.length > 1) {
        const idx = pool.indexOf(text);
        text = pool[(idx + 1) % pool.length];
      }
    } else {
      text = String(categoryOrText || "");
    }
    if (!text) return;
    lastSpeechText = text;
    lastSpeechAt = performance.now();
    if (speechCueEl) {
      speechCueEl.textContent = customCue || SPEECH_CUES[categoryOrText] || (sulking ? "BRUCE · 冷战低气压" : "BRUCE · 阳光低语");
    }
    speechLineEl.textContent = text;
    speechEl.classList.toggle("is-sulk", Boolean(sulking));
    speechEl.classList.add("is-visible");
    if (speechTimer) {
      clearTimeout(speechTimer);
      timers.delete(speechTimer);
    }
    speechTimer = later(() => {
      speechEl.classList.remove("is-visible");
      speechTimer = null;
    }, durationMs);
  }

  const idleTimerId = setInterval(() => {
    if (
      !destroyed &&
      !activeActId &&
      loadingEl.classList.contains("is-hidden") &&
      performance.now() - lastSpeechAt >= 6800 &&
      !bruce.isWalking?.() &&
      !bruce.getActiveAction?.()
    ) {
      sayBruce(sulking ? "idle_sulk" : "idle_happy", 5200);
    }
  }, 7000);
  cleanups.push(() => clearInterval(idleTimerId));

  // Folding keyholder toggle + House Concierge & B1 Chauffeur Intercom
  const syncConciergeUi = () => {
    if (conciergeFloorLabelEl) {
      conciergeFloorLabelEl.textContent =
        activeFloor === "terrace"
          ? "HOUSE CONCIERGE · 1F OCEAN TERRACE"
          : activeFloor === "2f"
            ? "HOUSE CONCIERGE · 2F LOFT"
            : "HOUSE CONCIERGE · 1F SALON";
    }
    const hifiActive = sfx.isHifiOn();
    conciergeHifiBtn?.classList.toggle("is-active", hifiActive);
    if (conciergeHifiTag) conciergeHifiTag.textContent = hifiActive ? "PLAYING · JAZZ" : "STANDBY";
    if (conciergeMoodTag) conciergeMoodTag.textContent = duskMode ? "DUSK LAMP" : "SUNSET";
    if (conciergeTvTag) conciergeTvTag.textContent = oldMoneyTv.getChannel().code;
    conciergePantryBtn?.classList.toggle("hidden", !sulking);
    stageEl.dataset.soundscapeDiag = JSON.stringify({
      scene: "penthouse",
      floor: activeFloor,
      hifiOn: hifiActive,
      duskMode,
      muted: sfx.muted,
    });
  };

  function showTvOsd(ch) {
    if (tvOsdCodeEl) tvOsdCodeEl.textContent = `${ch.code} · ${ch.tag}`;
    if (tvOsdTitleEl) tvOsdTitleEl.textContent = ch.title;
    if (tvOsdEl) {
      tvOsdEl.classList.add("is-visible");
      if (tvOsdTimer) clearTimeout(tvOsdTimer);
      tvOsdTimer = later(() => tvOsdEl.classList.remove("is-visible"), 3400);
    }
  }

  function cycleTvChannel(elapsed = performance.now() / 1000) {
    const ch = oldMoneyTv.nextChannel(elapsed);
    syncConciergeUi();
    showTvOsd(ch);
    return ch;
  }

  function toggleSunsetDuskMood() {
    duskMode = !duskMode;
    salonLampOn = duskMode;
    applyAtmosphere(sulking, false);
    return duskMode;
  }

  const meteorCtrl = createLuckyMeteorController(scene, {
    skyZ: -96,
    isPaused: () => Boolean(activeActId) || !loadingEl.classList.contains("is-hidden"),
    getContext: () => ({ sulking, zone: activeFloor, dusk: duskMode }),
    async onTrigger({ bonus }) {
      sfx.playConciergeBell();
      later(() => sfx.playSuccess(), 160);
      if (!sulking) bruce.triggerHappyHop();
      sayBruce("lucky_meteor", 4800, "LUCKY · 幸运时刻");
      const applied = await opts.onLuckyBonus?.(bonus);
      const shownBonus = applied?.bonus ?? bonus;
      if (luckySubEl) {
        luckySubEl.textContent = applied?.newScore
          ? `布鲁斯仰头摇尾许愿 · 幸福指数 +${shownBonus}（当前 ${applied.newScore}）`
          : `布鲁斯仰头摇尾许愿 · 幸福指数 +${shownBonus}`;
      }
      if (luckyToastEl) {
        luckyToastEl.classList.add("is-visible");
        if (luckyToastTimer) clearTimeout(luckyToastTimer);
        luckyToastTimer = later(() => luckyToastEl.classList.remove("is-visible"), 5200);
      }
    },
  });

  const setConciergeOpen = (open, sourceFloor = activeFloor) => {
    if (open) {
      setKeyholderOpen(false);
      if (conciergeFloorLabelEl) {
        const fl = sourceFloor === "2f" ? "2F LOFT" : "1F SALON";
        conciergeFloorLabelEl.textContent = `HOUSE CONCIERGE · ${fl}`;
      }
      syncConciergeUi();
    }
    conciergePopoverEl?.classList.toggle("is-open", Boolean(open));
    conciergePopoverEl?.setAttribute("aria-hidden", open ? "false" : "true");
  };

  conciergeCloseBtn?.addEventListener("click", (e) => {
    e.stopPropagation();
    sfx.playTap();
    setConciergeOpen(false);
  });

  conciergePantryBtn?.addEventListener("click", (e) => {
    e.stopPropagation();
    sfx.playTap();
    setConciergeOpen(false);
    opts.onOpenShop?.();
  });

  let yachtDepartBusy = false;
  async function departToYachtMarina(preloadOpts = {}) {
    if (destroyed || activeActId || yachtDepartBusy) return false;
    yachtDepartBusy = true;
    const marinaBtn = conciergePopoverEl?.querySelector('[data-concierge="chauffeur-marina"]');
    const marinaTag = marinaBtn?.querySelector(".concierge-act-tag");
    if (marinaTag) marinaTag.textContent = "PRELOADING…";
    sfx.playChauffeurReady();
    sayBruce("B1 司机正在备车，已接通白帆泊位长，正在预载柚木浮桥与单桅帆船……", 8000, "CHAUFFEUR · B1 备车预载");
    try {
      await (opts.onPreloadYacht ? opts.onPreloadYacht(preloadOpts) : Promise.resolve());
      if (destroyed) return false;
      opts.onSavePenthouseAnchor?.({
        floor: activeFloor,
        camPos: camera.position.toArray(),
        target: controls.target.toArray(),
        brucePos: bruce.root.position.toArray(),
        bruceRot: bruce.root.rotation.y,
      });
      setConciergeOpen(false);
      yachtDepartBusy = false;
      if (marinaTag) marinaTag.textContent = "FLY·04";
      opts.onTeleportYacht?.();
      return true;
    } catch (err) {
      yachtDepartBusy = false;
      if (marinaTag) marinaTag.textContent = "FLY·04";
      controls.enabled = true;
      sfx.playFail();
      sayBruce("泊位预载暂未接通，请稍后再试，客厅一切已为你保留。", 4200, "CHAUFFEUR · 预载中断");
      return false;
    }
  }

  conciergePopoverEl?.querySelectorAll("[data-concierge]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      if (destroyed || activeActId) return;
      const action = btn.getAttribute("data-concierge");
      feedback("small", e.clientX, e.clientY);
      const rect = stageEl.getBoundingClientRect();

      if (action === "water") {
        setConciergeOpen(false);
        sfx.playConciergeBell();
        later(() => sfx.playGlassPour(), 320);
        const is2F = activeFloor === "2f";
        flyCamera(
          is2F ? new THREE.Vector3(-8.2, 11.65, 0.95) : new THREE.Vector3(0.45, 2.35, 1.55),
          is2F ? new THREE.Vector3(-5.85, 10.55, 3.25) : new THREE.Vector3(1.10, 0.88, -1.92),
          880,
          () => {
            if (!is2F) walkBruceTo(1.15, 0.15, { silent: true });
            else walkBruceTo(-6.3, 0.95, { silent: true });
            later(() => bruce.playAction("lick_paw"), 650);
          },
        );
        spawnFxParticles(rect.width * 0.56, rect.height * 0.54, "water", 16);
        sayBruce("butler_water_lines", 4600, "CONCIERGE · 管家侍水");
      } else if (action === "hifi") {
        const on = sfx.toggleHifi();
        syncConciergeUi();
        sfx.playTap();
        spawnFxParticles(rect.width * 0.65, rect.height * 0.45, on ? "note" : "warm", 14);
        sayBruce(on ? "hifi_on_lines" : "hifi_off_lines", 4200, on ? "HARMAN · 爵士声场开启" : "HARMAN · 声场静默");
      } else if (action === "mood") {
        const nextDusk = toggleSunsetDuskMood();
        sfx.playTap();
        spawnFxParticles(rect.width * 0.62, rect.height * 0.42, "warm", 14);
        sayBruce(nextDusk ? "暮色微醺，落地灯与露台灯笼一并点亮啦。" : "回到黄金夕照时刻，落日正洒在海面上。", 4200, "LIGHT · 光影情景");
      } else if (action === "tv") {
        const ch = cycleTvChannel();
        sfx.playTap();
        spawnFxParticles(rect.width * 0.72, rect.height * 0.36, "gold", 12);
        sayBruce(`已为你切到「${ch.title}」，坐下来陪我一起看吧～`, 4200, `TV · ${ch.code}`);
      } else if (action === "chauffeur-cafe") {
        setConciergeOpen(false);
        sfx.playChauffeurReady();
        sayBruce("chauffeur_cafe_lines", 3400, "CHAUFFEUR · B1 专车就绪");
        flyCamera(new THREE.Vector3(-8.8, 4.3, 4.8), new THREE.Vector3(-14.6, 3.6, 2.2), 880, () => {
          later(() => opts.onTeleportStreet?.(), 650);
        });
      } else if (action === "chauffeur-market") {
        setConciergeOpen(false);
        sfx.playChauffeurReady();
        sayBruce("chauffeur_market_lines", 3600, "CHAUFFEUR · 持 07 号卡出发");
        later(() => triggerPatronCardDeparture(), 380);
      } else if (action === "chauffeur-marina") {
        departToYachtMarina();
      }
    });
  });

  const setKeyholderOpen = (open) => {
    if (open) setConciergeOpen(false);
    keyholderEl?.classList.toggle("is-open", open);
    keyholderBtn?.setAttribute("aria-expanded", open ? "true" : "false");
  };
  keyholderBtn?.addEventListener("click", (e) => {
    e.stopPropagation();
    sfx.playTap();
    setKeyholderOpen(!keyholderEl?.classList.contains("is-open"));
  });
  const onDocClickCloseKey = (e) => {
    if (keyholderEl && !keyholderEl.contains(e.target)) {
      setKeyholderOpen(false);
    }
    if (conciergePopoverEl && !conciergePopoverEl.contains(e.target)) {
      setConciergeOpen(false);
    }
  };
  document.addEventListener("click", onDocClickCloseKey);
  cleanups.push(() => document.removeEventListener("click", onDocClickCloseKey));

  // Build breathing brass dots (in-scene activities) & keyholder passes (teleports)
  const pinItems = HOTSPOTS.filter((s) => s.kind === "act").map((spot) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "hub3d-pin hub3d-dot";
    btn.setAttribute("data-spot", spot.id);
    btn.setAttribute("aria-label", `${spot.title}（${spot.sub}）`);
    btn.innerHTML = `
      <span class="dot-core">${spot.icon}</span>
      <span class="dot-popover">
        <span class="dot-title">${spot.title}</span>
        <span class="dot-sub">${spot.sub}</span>
      </span>
    `;
    pinsLayer.appendChild(btn);
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      setKeyholderOpen(false);
      feedback("small", e.clientX, e.clientY);
      sfx.playTap();
      handleHotspotClick(spot);
    });
    return { spot, btn, world: new THREE.Vector3(...spot.pos) };
  });

  if (keyholderTray) {
    const conciergeQuick = document.createElement("button");
    conciergeQuick.type = "button";
    conciergeQuick.className = "keyholder-item";
    conciergeQuick.setAttribute("data-spot", "concierge");
    conciergeQuick.innerHTML = `
      <span class="stub-main">
        <span class="stub-icon"><svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 17h14"/><path d="M7 17a5 5 0 0 1 10 0"/><path d="M12 12V9"/><circle cx="12" cy="8" r="1"/></svg></span>
        <span class="stub-text">
          <span class="stub-title">内线 · 管家与 B1 车队</span>
          <span class="stub-sub">侍水 / 哈曼声场 / 专车直达</span>
        </span>
      </span>
      <span class="stub-code">INT·00</span>
    `;
    keyholderTray.appendChild(conciergeQuick);
    conciergeQuick.addEventListener("click", (e) => {
      e.stopPropagation();
      feedback("small", e.clientX, e.clientY);
      sfx.playConciergeBell();
      setConciergeOpen(true, activeFloor);
      sayBruce("concierge_call", 3600, "BRUCE · 管家专线");
    });
  }

  HOTSPOTS.filter((s) => s.kind === "teleport").forEach((spot) => {
    if (!keyholderTray) return;
    const item = document.createElement("button");
    item.type = "button";
    item.className = "keyholder-item";
    item.setAttribute("data-spot", spot.id);
    item.innerHTML = `
      <span class="stub-main">
        <span class="stub-icon">${spot.icon}</span>
        <span class="stub-text">
          <span class="stub-title">${spot.title}</span>
          <span class="stub-sub">${spot.sub}</span>
        </span>
      </span>
      <span class="stub-code">${spot.code}</span>
    `;
    keyholderTray.appendChild(item);
    item.addEventListener("click", (e) => {
      e.stopPropagation();
      setKeyholderOpen(false);
      feedback("small", e.clientX, e.clientY);
      sfx.playTap();
      handleHotspotClick(spot);
    });
    item.addEventListener("pointerenter", () => {
      const hoverLine = hubCopy?.portal_hover?.[spot.id];
      if (hoverLine && !activeActId) sayBruce(hoverLine, 3400, "BRUCE · 门边张望");
    });
  });

  function applyAtmosphere(sulkMode, rainMode = false) {
    sulking = Boolean(sulkMode);
    vignetteEl.classList.toggle("is-sulk", sulking);
    rainPoints.visible = sulking || rainMode;
    motePoints.visible = !sulking && !rainMode;

    if (skyCycloramaMat) {
      skyCycloramaMat.map = sulking || rainMode ? rainySkyTex : sunnySkyTex;
      skyCycloramaMat.color.setHex(sulking || rainMode ? 0xffffff : duskMode ? 0x6a5b7a : 0xffffff);
      skyCycloramaMat.needsUpdate = true;
    }

    if (sulking) {
      scene.background.setHex(0x283546);
      hemiLight.color.setHex(0x9ab4d2);
      hemiLight.groundColor.setHex(0x45505e);
      hemiLight.intensity = 0.95;
      sunLight.intensity = 0.3;
      ambientLight.intensity = 0.52;
      warmLampLight.intensity = 0.4;
      renderer.toneMappingExposure = 0.98;
      bruce.setMood("sulk");
    } else if (rainMode) {
      scene.background.setHex(0x36475b);
      hemiLight.color.setHex(0xc4d6ea);
      hemiLight.groundColor.setHex(0x6e6258);
      hemiLight.intensity = 1.1;
      sunLight.intensity = 0.55;
      ambientLight.intensity = 0.62;
      warmLampLight.intensity = 1.2;
      renderer.toneMappingExposure = 1.04;
    } else if (duskMode) {
      scene.background.setHex(0x1f283d);
      hemiLight.color.setHex(0x9c88a4);
      hemiLight.groundColor.setHex(0x3e3228);
      hemiLight.intensity = 0.54;
      sunLight.color.setHex(0xff8e52);
      sunLight.intensity = 0.56;
      ambientLight.intensity = 0.34;
      warmLampLight.position.set(11.75, 3.68, 4.70);
      warmLampLight.intensity = 6.2;
      renderer.toneMappingExposure = 1.00;
      if (!activeActId) bruce.setMood("happy");
    } else {
      scene.background.setHex(0xebd8c4);
      hemiLight.color.setHex(0xfff1dc);
      hemiLight.groundColor.setHex(0xcab8a2);
      hemiLight.intensity = 1.45;
      sunLight.color.setHex(0xffcf94);
      sunLight.intensity = 2.25;
      ambientLight.intensity = 0.72;
      warmLampLight.position.set(11.75, 3.68, 4.70);
      warmLampLight.intensity = salonLampOn ? 2.8 : 0.9;
      renderer.toneMappingExposure = 1.12;
      if (!activeActId) bruce.setMood("happy");
    }
    terraceVista.setMood({ sulking: sulking || rainMode, dusk: duskMode });
    speechEl?.classList.toggle("is-sulk", sulking);

    pinItems.forEach(({ spot, btn }) => {
      const subEl = btn.querySelector(".dot-sub");
      if (subEl) subEl.textContent = sulking ? "先哄好布鲁斯" : spot.sub;
    });
    sfx.setSceneAmbience("penthouse", { floor: activeFloor, sulking: Boolean(sulkMode) });
    syncConciergeUi();
  }

  function flyCamera(toPos, toTarget, durationMs = 740, onDone = null) {
    camTween = {
      fromPos: camera.position.clone(),
      toPos: toPos.clone(),
      fromTarget: controls.target.clone(),
      toTarget: toTarget.clone(),
      start: performance.now(),
      duration: durationMs,
      onDone,
    };
  }

  function switchFloor(targetFloor, { animate = true, greet = true } = {}) {
    const fl = FLOOR_PRESETS[targetFloor] ? targetFloor : "1f";
    activeFloor = fl;
    const ov = getFloorOverview(fl);
    floorButtons.forEach((btn) => btn.classList.toggle("is-active", btn.getAttribute("data-floor") === fl));
    floorPlane.constant = -ov.preset.floorY;
    walkSpotCursor = 0;
    rippleMesh.visible = false;
    bruce.stopWalk();
    bruce.root.position.set(...ov.preset.brucePos);
    bruce.root.rotation.y = ov.preset.bruceRot;

    if (animate) {
      flyCamera(ov.cam, ov.target, 860);
    } else {
      camTween = null;
      camera.position.copy(ov.cam);
      controls.target.copy(ov.target);
      controls.update();
    }

    if (greet && !activeActId && loadingEl.classList.contains("is-hidden")) {
      if (!sulking) bruce.triggerHappyHop();
      sayBruce(
        fl === "terrace" ? "terrace_greet" : fl === "2f" ? "floor_2f_greet" : "floor_1f_greet",
        4400,
      );
    }
    meteorCtrl.notifyZone(fl);
    sfx.setFloorAmbience(fl);
    syncConciergeUi();
  }

  floorButtons.forEach((btn) => {
    const onFloorClick = (e) => {
      e.stopPropagation();
      if (activeActId) return;
      const target = btn.getAttribute("data-floor");
      sfx.playTap();
      feedback("small", e.clientX, e.clientY);
      switchFloor(target, { animate: true, greet: true });
    };
    btn.addEventListener("click", onFloorClick);
    cleanups.push(() => btn.removeEventListener("click", onFloorClick));
  });

  resetBtn.addEventListener("click", () => {
    sfx.playTap();
    const ov = getFloorOverview(activeFloor);
    flyCamera(ov.cam, ov.target, 620);
  });

  function spawnFxParticles(x, y, kind = "gold", count = 10) {
    for (let i = 0; i < count; i++) {
      const a = Math.random() * Math.PI * 2;
      const spd = 40 + Math.random() * 100;
      particles.push({
        x,
        y,
        vx: Math.cos(a) * spd,
        vy: Math.sin(a) * spd - (kind === "note" ? 45 : 20),
        life: 0,
        maxLife: 0.55 + Math.random() * 0.4,
        r: kind === "warm" ? 5 + Math.random() * 5 : 2.5 + Math.random() * 3,
        kind,
      });
    }
  }

  function exitInRoomActivity() {
    sfx.setVinylMode(false);
    actCleanup?.();
    actCleanup = null;
    activeActId = null;
    document.body.classList.remove("is-hub3d-act");
    tennisBall.visible = false;
    swapRingsGroup.visible = false;
    swapBanner.classList.remove("is-visible");
    settleEl.classList.remove("is-visible");
    vignetteEl.classList.remove("is-warn");
    actOverlay.classList.remove("is-active");
    actBodyEl.innerHTML = "";
    pinsLayer.classList.remove("is-hidden");
    resetBtn.style.display = "";
    controls.enabled = true;
    bruce.stopWalk();
    bruce.setPetting(0);
    if (!salonLampOn) warmLampLight.intensity = 0.0;
    const ov = getFloorOverview(activeFloor);
    bruce.root.position.set(...ov.preset.brucePos);
    bruce.root.rotation.y = ov.preset.bruceRot;
    applyAtmosphere(sulking, false);
    flyCamera(ov.cam, ov.target, 700);
  }

  btnActBack.addEventListener("click", () => {
    sfx.playTap();
    exitInRoomActivity();
  });

  btnReplay.addEventListener("click", () => {
    if (sulking || !activeActId) return;
    sfx.playTap();
    startInRoomActivity(activeActId, false);
  });

  btnDone.addEventListener("click", () => {
    sfx.playTap();
    if (sulking) {
      exitInRoomActivity();
      opts.onOpenShop?.();
    } else {
      exitInRoomActivity();
    }
  });

  let ballAnim = null;

  function startInRoomActivity(actId, autoplay = false) {
    const def = ACTIVITY_DEFS[actId];
    if (!def) return;

    actCleanup?.();
    activeActId = actId;
    const targetFloor = def.floor || "1f";
    activeFloor = targetFloor;
    floorButtons.forEach((btn) => btn.classList.toggle("is-active", btn.getAttribute("data-floor") === targetFloor));
    const ov = getFloorOverview(targetFloor);
    floorPlane.constant = -ov.preset.floorY;

    bruce.stopWalk();
    if (actId === "home_rain_vinyl") {
      bruce.root.position.set(-8.4, 9.24, -7.4);
      bruce.root.rotation.y = 0.72;
      warmLampLight.position.set(-11.8, 12.0, -10.2);
    } else {
      bruce.root.position.set(...ov.preset.brucePos);
      bruce.root.rotation.y = ov.preset.bruceRot;
    }
    document.body.classList.add("is-hub3d-act");
    if (speechTimer) {
      clearTimeout(speechTimer);
      timers.delete(speechTimer);
      speechTimer = null;
    }
    speechEl?.classList.remove("is-visible");
    controls.enabled = false;
    pinsLayer.classList.add("is-hidden");
    resetBtn.style.display = "none";
    settleEl.classList.remove("is-visible");
    swapBanner.classList.remove("is-visible");
    swapRingsGroup.visible = false;
    actBodyEl.innerHTML = "";
    btnActAuto.textContent = autoplay ? "手动玩" : "自动演示";

    applyAtmosphere(false, false);
    if (actId === "home_rain_vinyl") {
      sunLight.color.setHex(0xffd796);
      sunLight.intensity = 1.85;
      warmLampLight.intensity = 1.1;
    }
    flyCamera(def.camPos, def.camTarget, 700, () => {
      if (!destroyed && activeActId === actId) {
        actOverlay.classList.add("is-active");
      }
    });

    let finished = false;
    const actTimers = new Set();
    const actListeners = [];

    const actLater = (fn, ms) => {
      const id = later(() => {
        actTimers.delete(id);
        if (!finished && activeActId === actId) fn();
      }, ms);
      actTimers.add(id);
      return id;
    };

    const listen = (el, ev, fn, o) => {
      el.addEventListener(ev, fn, o);
      actListeners.push(() => el.removeEventListener(ev, fn, o));
    };

    listen(btnActAuto, "click", () => {
      sfx.playTap();
      startInRoomActivity(actId, !autoplay);
    });

    // Phone temptation banner
    let phoneEl = null;
    let phoneCount = 0;
    const triggerPhone = (autoTap = false) => {
      if (finished || phoneCount >= 2 || phoneEl) return;
      phoneCount += 1;
      const note = pickRandom(content?.phone_notifications) || { app: "CHAT", text: "NEW MESSAGE · 99+" };
      const banner = document.createElement("button");
      banner.type = "button";
      banner.className = "hub3d-phone-banner";
      banner.innerHTML = `
        <span class="hub3d-phone-app"></span>
        <span class="hub3d-phone-body">
          <span class="hub3d-phone-title"></span>
          <span class="hub3d-phone-text"></span>
        </span>
      `;
      banner.querySelector(".hub3d-phone-app").textContent = String(note.app || "CHAT").slice(0, 4);
      banner.querySelector(".hub3d-phone-title").textContent = `${note.app || "CHAT"} · NOW`;
      banner.querySelector(".hub3d-phone-text").textContent = note.text || "NEW MESSAGE";
      actOverlay.appendChild(banner);
      phoneEl = banner;

      listen(banner, "click", (e) => {
        e.stopPropagation();
        sfx.playPhoneBuzz();
        conclude("phone_fail");
      });

      requestAnimationFrame(() => banner.classList.add("is-shown"));
      sfx.playPhoneBuzz();

      if (autoTap) {
        actLater(() => {
          sfx.playPhoneBuzz();
          conclude("phone_fail");
        }, 900);
        return;
      }

      actLater(() => {
        banner.classList.remove("is-shown");
        actLater(() => {
          banner.remove();
          if (phoneEl === banner) phoneEl = null;
        }, 340);
      }, 2500);
    };

    const conclude = async (outcome) => {
      if (finished) return;
      finished = true;
      actTimers.forEach((t) => clearTimeout(t));
      actTimers.clear();
      actListeners.forEach((fn) => fn());
      actListeners.length = 0;
      vignetteEl.classList.remove("is-warn");
      bruce.setPetting(0);
      if (phoneEl) {
        phoneEl.remove();
        phoneEl = null;
      }
      actBodyEl.innerHTML = "";
      actPromptEl.textContent = "";

      const isWin = outcome === "win";
      const delta = isWin ? def.win : def.fail;
      if (isWin) {
        sfx.playSuccess();
        bruce.setMood("excited");
        if (actId === "home_hide_seek") {
          bruce.playAction("play_bow");
        } else if (Math.random() < 0.55) {
          bruce.playAction("roll_over");
        } else {
          bruce.triggerHappyHop();
        }
        const r = stageEl.getBoundingClientRect();
        spawnFxParticles(r.width * 0.5, r.height * 0.48, "gold", 22);
      } else {
        sfx.playFail();
        bruce.setMood("sulk");
        bruce.playAction("airplane_ears");
      }

      const actCopy = content?.activities?.[actId] || {};
      const pool =
        outcome === "win"
          ? actCopy.win_lines
          : outcome === "phone_fail"
            ? actCopy.phone_fail_lines
            : actCopy.hazard_fail_lines;
      const summaryLine = pickRandom(
        pool,
        isWin ? "布鲁斯眯眼摇着尾巴，乖乖靠在你膝边。" : "布鲁斯耷拉着耳朵，默默躲回了角落。",
      );

      settleEl.querySelector(".hub3d-settle-title").textContent =
        outcome === "win" ? "陪伴成功" : outcome === "phone_fail" ? "被手机抢走了" : "踩到雷点了";
      const deltaEl = settleEl.querySelector(".hub3d-settle-delta");
      deltaEl.textContent = `${delta >= 0 ? "+" : ""}${delta}`;
      deltaEl.classList.toggle("is-neg", delta < 0);
      settleEl.querySelector(".hub3d-settle-line").textContent = summaryLine;
      const statusEl = settleEl.querySelector(".hub3d-settle-status");
      statusEl.textContent = "正在同步幸福指数……";

      const projected = Math.max(0, happiness + delta);
      btnReplay.hidden = projected < 80;
      btnDone.textContent = projected < 80 ? "去私厨鲜食柜" : "回到客厅全景";
      settleEl.classList.add("is-visible");

      const triggerSwapCandidate = isWin && Math.random() < def.swapProb;
      try {
        const swap = await opts.onSettle?.({
          activityId: actId,
          title: def.title,
          outcome,
          delta,
          triggerSwapCandidate,
          summaryLine,
        });
        if (destroyed || activeActId !== actId) return;

        const finalScore = Number.isFinite(swap?.newScore) ? swap.newScore : opts.getHappiness?.() ?? projected;
        happiness = finalScore;
        sulking = finalScore < 80;
        btnReplay.hidden = sulking;

        if (sulking) {
          applyAtmosphere(true, false);
          statusEl.textContent = `幸福指数跌至 ${finalScore}（<80），布鲁斯正生闷气`;
          btnDone.textContent = "去私厨鲜食柜";
        } else {
          statusEl.textContent = `当前幸福指数 · ${finalScore}`;
          btnDone.textContent = "回到客厅全景";
        }

        if (Number.isFinite(swap?.newScore)) {
          settleEl.classList.remove("is-visible");
          swapRingsGroup.visible = true;
          swapBanner.classList.add("is-visible");
          swapMsgEl.textContent = swap.topBonus
            ? "已经站在最高处，再送你 +6"
            : `这一束光来自 ${swap.targetNickname || "一位新朋友"}`;
          sfx.playSwapCelebration();

          const fromV = swap.oldScore ?? projected;
          const toV = swap.newScore;
          const t0 = performance.now();
          const rollStep = (now) => {
            if (destroyed || activeActId !== actId) return;
            const p = Math.min(1, (now - t0) / 1000);
            swapNumEl.textContent = String(Math.round(fromV + (toV - fromV) * (1 - Math.pow(1 - p, 3))));
            if (p < 1) requestAnimationFrame(rollStep);
          };
          requestAnimationFrame(rollStep);

          later(() => {
            if (destroyed || activeActId !== actId) return;
            swapBanner.classList.remove("is-visible");
            swapRingsGroup.visible = false;
            statusEl.textContent = `高位换分完成 · 当前幸福指数 ${swap.newScore}`;
            settleEl.classList.add("is-visible");
          }, 3200);
        }
      } catch (_) {
        if (!destroyed && activeActId === actId) {
          statusEl.textContent = "结算暂未同步，请稍后重试";
        }
      }
    };

    actLater(() => triggerPhone(false), 1800 + Math.random() * 1400);

    // Build specific in-room interaction
    if (actId === "home_brush") {
      actPromptEl.textContent = "在布鲁斯身上按住轻轻来回顺毛";
      actBodyEl.innerHTML = `
        <div class="hub3d-brush-zone"></div>
        <div class="hub3d-progress"><div class="hub3d-progress-fill"></div></div>
        <button type="button" class="hub3d-hazard-btn">DRYER · 吹风机</button>
      `;
      const zone = actBodyEl.querySelector(".hub3d-brush-zone");
      const fill = actBodyEl.querySelector(".hub3d-progress-fill");
      const dryer = actBodyEl.querySelector(".hub3d-hazard-btn");

      listen(dryer, "click", (e) => {
        e.stopPropagation();
        conclude("hazard_fail");
      });

      let progress = 0;
      const TARGET = 2000;
      let warning = false;
      let warnedOnce = false;
      let warnMove = 0;
      let dragging = false;
      let lastPos = null;
      let lastTapAt = 0;
      let blissStage = 0;

      const stroke = (dx, dy, cx, cy) => {
        const d = Math.hypot(dx, dy);
        if (d < 1) return;
        if (warning) {
          warnMove += d;
          if (warnMove > 65) conclude("hazard_fail");
          return;
        }
        progress = Math.min(TARGET, progress + d);
        fill.style.width = `${(progress / TARGET) * 100}%`;
        bruce.setPetting(1);
        bruce.setMood("excited");
        if (blissStage === 0 && progress >= TARGET * 0.14) {
          blissStage = 1;
          sayBruce("petting_bliss", 3000);
        } else if (blissStage === 1 && progress >= TARGET * 0.72) {
          blissStage = 2;
          sayBruce("petting_bliss", 3000);
        }
        const rect = stageEl.getBoundingClientRect();
        spawnFxParticles(cx - rect.left, cy - rect.top, "gold", 3);
        const now = performance.now();
        if (now - lastTapAt > 280) {
          lastTapAt = now;
          sfx.playTap();
        }
        if (!warnedOnce && progress >= TARGET * 0.42) {
          warnedOnce = true;
          warning = true;
          warnMove = 0;
          bruce.setMood("warn");
          sayBruce("ear_warn", 2600);
          vignetteEl.classList.add("is-warn");
          actPromptEl.textContent = "飞机耳预警！先松手等 1 秒";
          actLater(() => {
            warning = false;
            bruce.setMood("happy");
            vignetteEl.classList.remove("is-warn");
            actPromptEl.textContent = "布鲁斯放松了，继续顺毛";
          }, 1400);
        }
        if (progress >= TARGET) conclude("win");
      };

      listen(actOverlay, "pointerdown", (e) => {
        if (autoplay || e.target === dryer || e.target.closest(".hub3d-phone-banner") || e.target.closest(".hub3d-act-top")) return;
        const r = zone.getBoundingClientRect();
        if (e.clientX >= r.left - 40 && e.clientX <= r.right + 40 && e.clientY >= r.top - 40 && e.clientY <= r.bottom + 40) {
          dragging = true;
          lastPos = { x: e.clientX, y: e.clientY };
        }
      });
      listen(actOverlay, "pointermove", (e) => {
        if (autoplay || !dragging || !lastPos) return;
        stroke(e.clientX - lastPos.x, e.clientY - lastPos.y, e.clientX, e.clientY);
        lastPos = { x: e.clientX, y: e.clientY };
      });
      listen(window, "pointerup", () => {
        dragging = false;
        lastPos = null;
        bruce.setPetting(0);
      });

      if (autoplay) {
        const autoStep = () => {
          if (finished || activeActId !== actId) return;
          if (warning) {
            actLater(autoStep, 450);
            return;
          }
          const r = stageEl.getBoundingClientRect();
          stroke(440, 30, r.left + r.width * 0.5, r.top + r.height * 0.5);
          actLater(autoStep, 650);
        };
        actLater(autoStep, 750);
      }
    } else if (actId === "home_rain_vinyl") {
      actPromptEl.textContent = "晴朗午后慢转：铺羊绒毯 → 抽头版黑胶 → 轻落唱针";
      actBodyEl.innerHTML = `
        <div class="hub3d-props-row">
          <button type="button" class="hub3d-prop-btn" data-prop="cashmere">CASHMERE · 羊绒毯</button>
          <button type="button" class="hub3d-prop-btn" data-prop="sleeve">SLEEVE · 选唱片</button>
          <button type="button" class="hub3d-prop-btn" data-prop="tonearm">TONEARM · 落唱针</button>
        </div>
      `;
      const order = ["cashmere", "sleeve", "tonearm"];
      let step = 0;

      const handleProp = (prop, btn) => {
        if (finished || btn.classList.contains("is-done")) return;
        if (prop !== order[step]) {
          conclude("hazard_fail");
          return;
        }
        btn.classList.add("is-done");
        step += 1;
        if (prop === "tonearm") {
          sfx.playVinylDrop();
          sfx.setVinylMode(true);
          syncConciergeUi();
        } else {
          sfx.playTap();
        }
        warmLampLight.intensity = 1.0 + step * 0.85;
        bruce.triggerHappyHop();
        const r = stageEl.getBoundingClientRect();
        spawnFxParticles(r.width * 0.5, r.height * 0.52, step === 3 ? "note" : "warm", 18);
        if (step <= 2) sayBruce("rain_cozy", 3000);
        if (step === 1) actPromptEl.textContent = "羊绒毯铺好了，从木盒里抽一张头版黑胶";
        else if (step === 2) actPromptEl.textContent = "斜阳落在唱片封面，轻落唱针吧";
        else actLater(() => conclude("win"), 600);
      };

      actBodyEl.querySelectorAll("[data-prop]").forEach((btn) => {
        listen(btn, "click", (e) => {
          e.stopPropagation();
          if (!autoplay) handleProp(btn.getAttribute("data-prop"), btn);
        });
      });

      if (autoplay) {
        order.forEach((p, idx) => {
          actLater(() => {
            const btn = actBodyEl.querySelector(`[data-prop="${p}"]`);
            if (btn) handleProp(p, btn);
          }, 900 + idx * 1000);
        });
      }
    } else if (actId === "home_hide_seek") {
      actPromptEl.textContent = "按住网球向上甩出！丢到客厅地板上";
      actBodyEl.innerHTML = `
        <div class="hub3d-ball-btn">BALL</div>
        <button type="button" class="hub3d-hazard-btn">BLOWER · 高速吹风筒</button>
      `;
      const ballBtn = actBodyEl.querySelector(".hub3d-ball-btn");
      const speakerBtn = actBodyEl.querySelector(".hub3d-hazard-btn");

      listen(speakerBtn, "click", (e) => {
        e.stopPropagation();
        conclude("hazard_fail");
      });

      let dragging = false;
      let startY = 0;
      let startT = 0;
      let thrown = false;

      const throwBall3D = () => {
        if (thrown) return;
        thrown = true;
        ballBtn.style.display = "none";
        sfx.playTap();
        tennisBall.visible = true;
        tennisBall.position.set(3.8, 2.2, 6.6);
        ballAnim = {
          vx: -1.1,
          vy: 4.6,
          vz: -2.0,
          active: true,
        };
        bruce.setMood("excited");
        bruce.walkTo(0.2, 2.4, {
          speedScale: 1.25,
          onArrive: () => bruce.playAction("play_bow"),
        });
        sayBruce("ball_excited", 3000);
        actPromptEl.textContent = "布鲁斯扑过去捡球啦…别点弹出手机";
        actLater(() => triggerPhone(false), 700);
        actLater(() => conclude("win"), 3000);
      };

      listen(ballBtn, "pointerdown", (e) => {
        if (autoplay || thrown) return;
        e.stopPropagation();
        dragging = true;
        startY = e.clientY;
        startT = performance.now();
      });
      listen(window, "pointerup", (e) => {
        if (!dragging || thrown) return;
        dragging = false;
        const dy = e.clientY - startY;
        const dt = Math.max(16, performance.now() - startT);
        if (-dy / dt > 0.5 || dy < -80) {
          throwBall3D();
        } else {
          actPromptEl.textContent = "再用力往上甩一点！";
        }
      });

      if (autoplay) {
        actLater(throwBall3D, 900);
      }
    }

    actCleanup = () => {
      finished = true;
      actTimers.forEach((t) => clearTimeout(t));
      actTimers.clear();
      actListeners.forEach((fn) => fn());
      actListeners.length = 0;
      ballAnim = null;
      tennisBall.visible = false;
    };
  }

  function handleHotspotClick(spot) {
    if (spot.kind === "act") {
      if (sulking) {
        opts.onOpenShop?.();
        return;
      }
      startInRoomActivity(spot.id, false);
      return;
    }

    if (spot.id === "street") {
      flyCamera(new THREE.Vector3(-8.8, 4.3, 4.8), new THREE.Vector3(-14.6, 3.6, 2.2), 880, () => {
        later(() => opts.onTeleportStreet?.(), 850);
      });
      return;
    }

    if (spot.id === "warehouse") {
      triggerPatronCardDeparture();
      return;
    }

    if (spot.id === "global") {
      opts.onTeleportGlobal?.();
    }
  }

  function triggerPatronCardDeparture() {
    if (destroyed || activeActId || departSkipFn) return;
    if (activeFloor !== "1f") switchFloor("1f", { animate: false, greet: false });
    controls.enabled = false;
    setKeyholderOpen(false);
    sayBruce("patron_card_depart", 3600);
    let done = false;
    const finishDepart = () => {
      if (done || destroyed) return;
      done = true;
      departSkipFn = null;
      controls.enabled = true;
      opts.onTeleportWarehouse?.();
    };
    // Stage 1: Panoramic Grand Foyer Alcove sweep (950ms + 450ms pause)
    flyCamera(
      new THREE.Vector3(-9.5, 3.25, 6.55),
      new THREE.Vector3(-14.1, 2.55, 6.55),
      950,
      () => {
        later(() => {
          if (done || destroyed) return;
          // Stage 2: Macro push-in onto the tilted NO. 07 House Card in cognac leather tray (850ms + 1900ms dwell)
          flyCamera(
            new THREE.Vector3(-12.55, 2.36, 6.66),
            new THREE.Vector3(-13.90, 1.83, 6.44),
            850,
            () => {
              departSkipFn = finishDepart;
              later(finishDepart, 1900);
            },
          );
        }, 450);
      },
    );
  }

  // Pointer gaze tracking, raycast click on 3D Bruce / Gallery TV / Arched Lamp / Card, Click-to-Walk floor & Trick Bar
  const raycaster = new THREE.Raycaster();
  const ndc = new THREE.Vector2();
  const floorPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -initOv.preset.floorY);
  const floorHit = new THREE.Vector3();
  let walkSpotCursor = 0;
  let pokeCount = 0;
  let canvasDown = null;

  const trickButtons = Array.from(container.querySelectorAll(".trick-pill[data-trick]"));
  function highlightTrickBtn(trickId) {
    trickButtons.forEach((b) => b.classList.toggle("is-playing", b.getAttribute("data-trick") === trickId));
    later(() => {
      trickButtons.forEach((b) => {
        if (b.getAttribute("data-trick") === trickId) b.classList.remove("is-playing");
      });
    }, 2400);
  }

  function walkBruceTo(rawX, rawZ, { silent = false } = {}) {
    const b = getFloorOverview(activeFloor).preset.walkBounds;
    const tx = THREE.MathUtils.clamp(rawX, b.minX, b.maxX);
    const tz = THREE.MathUtils.clamp(rawZ, b.minZ, b.maxZ);
    triggerFloorRipple(tx, tz);
    bruce.walkTo(tx, tz, { speedScale: sulking ? 0.65 : 1.0 });
    if (!silent) sayBruce(sulking ? "walk_sulk" : "walk_call", 3400);
  }

  function runTrick(trickId) {
    if (destroyed || activeActId) return;
    highlightTrickBtn(trickId);
    if (trickId === "walk") {
      const spots = getFloorOverview(activeFloor).preset.walkSpots;
      walkSpotCursor = (walkSpotCursor + 1) % spots.length;
      const [wx, wz] = spots[walkSpotCursor];
      sfx.playTap();
      walkBruceTo(wx, wz);
      return;
    }
    if (trickId === "roll_over") sfx.playRollJoy();
    else if (trickId === "play_bow") sfx.playStretchSigh();
    else sfx.playTap();
    bruce.playAction(trickId);
    const rect = stageEl.getBoundingClientRect();
    spawnFxParticles(rect.width * 0.52, rect.height * 0.56, trickId === "airplane_ears" ? "water" : "gold", 14);
    sayBruce(trickId, 3800);
  }

  trickButtons.forEach((btn) => {
    const onTrickClick = (e) => {
      e.stopPropagation();
      setKeyholderOpen(false);
      feedback("small", e.clientX, e.clientY);
      runTrick(btn.getAttribute("data-trick"));
    };
    btn.addEventListener("click", onTrickClick);
    cleanups.push(() => btn.removeEventListener("click", onTrickClick));
  });

  const chatCleanup = mountBruceChatBar({
    stageEl,
    toggleBtn: container.querySelector("#hub3d-btn-chat"),
    getContext: () => ({
      scene: "living_room",
      sulking,
      happiness,
      owner: opts.player?.owner,
      nickname: opts.player?.nickname,
    }),
    onAiResponse(res, showDelta) {
      if (destroyed) return;
      sayBruce(res.reply, 5400, res.cue || "BRUCE · 灵动回应");
      const act = res.action;
      if (act === "walk") {
        runTrick("walk");
      } else if (act && act !== "idle") {
        bruce.playAction(act);
        highlightTrickBtn(act);
        if (act === "roll_over") sfx.playRollJoy();
        else if (act === "play_bow") sfx.playStretchSigh();
      }
      if (res.sincerityDelta) {
        opts.onSincerityDelta?.(res.sincerityDelta)?.then((applied) => {
          if (applied) showDelta?.(applied);
        });
      }
    },
  });
  cleanups.push(chatCleanup);

  const onCanvasDown = (e) => {
    if (activeActId) return;
    canvasDown = { x: e.clientX, y: e.clientY };
  };
  const onCanvasClick = (e) => {
    if (departSkipFn) {
      departSkipFn();
      return;
    }
    if (activeActId) return;
    const dist = canvasDown ? Math.hypot(e.clientX - canvasDown.x, e.clientY - canvasDown.y) : 0;
    canvasDown = null;
    if (dist >= 10) return;

    const r = canvas.getBoundingClientRect();
    if (!r.width || !r.height) return;
    ndc.x = ((e.clientX - r.left) / r.width) * 2 - 1;
    ndc.y = -((e.clientY - r.top) / r.height) * 2 + 1;
    raycaster.setFromCamera(ndc, camera);
    const bruceGroup = bruce.hitTarget || bruce.root.children[0];
    if (bruceGroup) {
      bruce.root.updateMatrixWorld(true);
      const hits = raycaster.intersectObject(bruceGroup, true);
      if (hits.length > 0) {
        feedback("small", e.clientX, e.clientY);
        const stageRect = stageEl.getBoundingClientRect();
        spawnFxParticles(e.clientX - stageRect.left, e.clientY - stageRect.top, sulking ? "water" : "gold", 14);
        if (sulking) {
          sfx.playTap();
          bruce.playAction("airplane_ears");
          highlightTrickBtn("airplane_ears");
          sayBruce("click_poke_sulk", 4200);
        } else {
          const cycle = ["roll_over", "play_bow", "lick_paw"];
          const chosen = cycle[pokeCount % cycle.length];
          pokeCount += 1;
          if (chosen === "roll_over") sfx.playRollJoy();
          else if (chosen === "play_bow") sfx.playStretchSigh();
          else sfx.playTap();
          bruce.playAction(chosen);
          highlightTrickBtn(chosen);
          sayBruce(chosen, 4000);
        }
        return;
      }
    }

    // Tactile collector pieces: Gallery Art TV, Champagne Arched Lamp, Entry NO.07 Card, Concierge Pagers, Harman Speakers & Firebox
    const interactiveMeshes = [
      tvScreenMesh,
      patronCardMesh,
      ...lampClickMeshes,
      ...conciergeMeshes,
      ...hifiMeshes,
      ...fireplaceMeshes,
    ].filter(Boolean);
    if (interactiveMeshes.length > 0) {
      const propHits = raycaster.intersectObjects(interactiveMeshes, false);
      if (propHits.length > 0) {
        const hitObj = propHits[0].object;
        feedback("small", e.clientX, e.clientY);
        sfx.playTap();
        const stageRect = stageEl.getBoundingClientRect();
        if (hitObj === patronCardMesh) {
          spawnFxParticles(e.clientX - stageRect.left, e.clientY - stageRect.top, "gold", 12);
          triggerPatronCardDeparture();
          return;
        }
        if (conciergeMeshes.includes(hitObj)) {
          sfx.playConciergeBell();
          spawnFxParticles(e.clientX - stageRect.left, e.clientY - stageRect.top, "gold", 14);
          const hitFloor = /2F/i.test(hitObj.name) ? "2f" : "1f";
          setConciergeOpen(true, hitFloor);
          sayBruce("concierge_call", 3800, "BRUCE · 管家专线");
          return;
        }
        if (hifiMeshes.includes(hitObj)) {
          const on = sfx.toggleHifi();
          syncConciergeUi();
          spawnFxParticles(e.clientX - stageRect.left, e.clientY - stageRect.top, on ? "note" : "warm", 14);
          sayBruce(on ? "hifi_on_lines" : "hifi_off_lines", 4000, on ? "HARMAN · 爵士声场开启" : "HARMAN · 声场静默");
          return;
        }
        if (fireplaceMeshes.includes(hitObj)) {
          sfx.stokeFireplace();
          spawnFxParticles(e.clientX - stageRect.left, e.clientY - stageRect.top, "warm", 16);
          sayBruce("fireplace_warm", 4000, "BRUCE · 炉火微醺");
          return;
        }
        if (hitObj === tvScreenMesh && tvScreenMat) {
          const ch = cycleTvChannel();
          spawnFxParticles(e.clientX - stageRect.left, e.clientY - stageRect.top, "gold", 12);
          sayBruce("tv_art_swap", 3800, `TV · ${ch.code}`);
          return;
        }
        if (lampClickMeshes.includes(hitObj)) {
          const nextDusk = toggleSunsetDuskMood();
          spawnFxParticles(e.clientX - stageRect.left, e.clientY - stageRect.top, "warm", 14);
          sayBruce(
            nextDusk ? "已点亮胡桃木落地灯，切换暮色微醺氛围。" : "切换回落日夕照客厅光线。",
            3800,
            "BRUCE · 暖光切换",
          );
          return;
        }
      }
    }

    // Floor raycast -> Click-to-Walk on active floor (1F rug or 2F mezzanine rug)
    if (raycaster.ray.direction.y < -0.04 && raycaster.ray.intersectPlane(floorPlane, floorHit)) {
      const b = getFloorOverview(activeFloor).preset.walkBounds;
      if (
        floorHit.x >= b.minX - 0.8 &&
        floorHit.x <= b.maxX + 0.8 &&
        floorHit.z >= b.minZ - 0.8 &&
        floorHit.z <= b.maxZ + 0.8
      ) {
        sfx.playTap();
        walkBruceTo(floorHit.x, floorHit.z);
        highlightTrickBtn("walk");
      }
    }
  };
  canvas.addEventListener("pointerdown", onCanvasDown);
  canvas.addEventListener("click", onCanvasClick);
  cleanups.push(() => {
    canvas.removeEventListener("pointerdown", onCanvasDown);
    canvas.removeEventListener("click", onCanvasClick);
  });

  const onPointerMove = (e) => {
    const r = stageEl.getBoundingClientRect();
    if (!r.width || !r.height) return;
    const nx = ((e.clientX - r.left) / r.width - 0.5) * 2;
    const ny = ((e.clientY - r.top) / r.height - 0.5) * 2;
    bruce.lookAtNormalized(nx, ny);
  };
  stageEl.addEventListener("pointermove", onPointerMove);
  cleanups.push(() => stageEl.removeEventListener("pointermove", onPointerMove));

  const onDoorOpened = () => {
    if (destroyed || activeActId) return;
    switchFloor("1f", { animate: false, greet: false });
    camera.position.set(-7.6, 5.2, 13.6);
    controls.target.set(1.8, 3.0, -1.6);
    controls.update();
    const ov = getFloorOverview("1f");
    flyCamera(ov.cam, ov.target, 900);
    if (!sulking) bruce.triggerHappyHop();
    sayBruce(sulking ? "idle_sulk" : "idle_happy", 4600);
  };
  window.addEventListener("bruce:door-opened", onDoorOpened);
  cleanups.push(() => window.removeEventListener("bruce:door-opened", onDoorOpened));

  const onKeyShortcut = (e) => {
    if (!destroyed && !activeActId && e.shiftKey && e.key?.toLowerCase() === "m") {
      meteorCtrl.triggerNow();
    }
  };
  window.addEventListener("keydown", onKeyShortcut);
  cleanups.push(() => window.removeEventListener("keydown", onKeyShortcut));

  // Main render loop
  let prevNow = performance.now();
  const projVec = new THREE.Vector3();
  const fxCtx = fxCanvas.getContext("2d");

  const tick = (now) => {
    if (destroyed) return;
    const dt = Math.min(0.05, (now - prevNow) / 1000);
    prevNow = now;
    const elapsed = now / 1000;

    // Resize renderer & fx canvas (+ adapt FOV on portrait iPad screens so all pins stay framed)
    const w = Math.max(300, stageEl.clientWidth);
    const h = Math.max(240, stageEl.clientHeight);
    const desiredFov = w / h < 0.95 ? 58 : w < 960 ? 52 : 48;
    if (canvas.width !== Math.round(w * renderer.getPixelRatio()) || canvas.height !== Math.round(h * renderer.getPixelRatio()) || camera.fov !== desiredFov) {
      renderer.setSize(w, h, false);
      camera.fov = desiredFov;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    if (fxCanvas.width !== Math.round(w * dpr) || fxCanvas.height !== Math.round(h * dpr)) {
      fxCanvas.width = Math.round(w * dpr);
      fxCanvas.height = Math.round(h * dpr);
    }

    // Duplex elevator arc tween (via duplexCamMath.js) or clamped OrbitControls
    if (camTween) {
      const p = Math.min(1, (now - camTween.start) / camTween.duration);
      const pose = computeDuplexCameraPose(
        camTween.fromPos,
        camTween.toPos,
        camTween.fromTarget,
        camTween.toTarget,
        p,
      );
      camera.position.set(pose.pos.x, pose.pos.y, pose.pos.z);
      controls.target.set(pose.target.x, pose.target.y, pose.target.z);
      controls.update();
      if (p >= 1) {
        const cb = camTween.onDone;
        camTween = null;
        cb?.();
      }
    } else {
      controls.update();
      const onBalconySide = activeFloor === "terrace" || controls.target.z < -15.4 || bruce.root.position.z < -15.4;
      if (onBalconySide) {
        camera.position.x = THREE.MathUtils.clamp(camera.position.x, -15.0, 15.0);
        camera.position.y = THREE.MathUtils.clamp(camera.position.y, 1.05, 14.5);
        camera.position.z = THREE.MathUtils.clamp(camera.position.z, -28.8, 14.8);
      } else {
        camera.position.x = THREE.MathUtils.clamp(camera.position.x, -14.0, 14.0);
        camera.position.y = THREE.MathUtils.clamp(camera.position.y, 1.4, 17.6);
        camera.position.z = THREE.MathUtils.clamp(camera.position.z, -15.1, 14.8);
      }
    }

    // Live animated TV channels, sunset ocean wave shimmer, wheeling 3D seagulls, & shooting stars
    oldMoneyTv.update(elapsed);
    terraceVista.update(dt, elapsed);
    meteorCtrl.update(dt);

    // Smooth vertical perch adjustment when Bruce walks onto/off the plush Terrace sunset sofa
    if (activeFloor === "terrace" || bruce.root.position.z < -15.6) {
      const bx = bruce.root.position.x;
      const bz = bruce.root.position.z;
      const onSofa = bx >= -0.45 && bx <= 3.25 && bz >= -23.25 && bz <= -21.75;
      const desiredY = onSofa ? 0.56 : 0.02;
      bruce.root.position.y = THREE.MathUtils.lerp(bruce.root.position.y, desiredY, Math.min(1, dt * 8.0));
    }

    // Dust motes / rain motion
    if (motePoints.visible) {
      const arr = moteGeo.attributes.position.array;
      for (let i = 0; i < moteCount; i++) {
        arr[i * 3 + 1] += dt * 0.28;
        if (arr[i * 3 + 1] > 14.5) arr[i * 3 + 1] = 1.2;
      }
      moteGeo.attributes.position.needsUpdate = true;
    }
    if (rainPoints.visible) {
      const arr = rainGeo.attributes.position.array;
      for (let i = 0; i < rainCount; i++) {
        arr[i * 3 + 1] -= dt * 11.5;
        if (arr[i * 3 + 1] < 0.5) arr[i * 3 + 1] = 17.8;
      }
      rainGeo.attributes.position.needsUpdate = true;
    }

    // Dynamic wood-burning fireplace flames, rising ember sparks, & hearth flicker
    const flicker =
      Math.sin(elapsed * 9.3) * 0.22 +
      Math.sin(elapsed * 17.1 + 1.4) * 0.14 +
      Math.cos(elapsed * 5.7) * 0.12;
    fireplaceLight.intensity = 2.30 + flicker * 0.95;
    if (fireplaceEmberMesh?.material) {
      fireplaceEmberMesh.material.emissiveIntensity = 0.95 + flicker * 0.35;
    }
    const hifiActive = sfx.isHifiOn();
    for (let i = 0; i < hifiHaloMats.length; i++) {
      hifiHaloMats[i].emissiveIntensity = hifiActive
        ? 1.85 + Math.sin(elapsed * 2.4 + i) * 0.45
        : 0.75;
    }
    for (let i = 0; i < flameRibbons.length; i++) {
      const f = flameRibbons[i];
      const w1 = Math.sin(elapsed * f.speed + f.phase);
      const w2 = Math.cos(elapsed * (f.speed * 1.43) + f.phase * 0.7);
      const hScale = f.baseScale * (0.94 + w1 * 0.20 + w2 * 0.10);
      f.mesh.scale.set(f.baseScale * (0.90 + w2 * 0.12), hScale, 1.0);
      f.mesh.position.y = 1.66 + 0.33 * hScale;
      f.mesh.position.z = f.baseZ + w2 * 0.035;
      f.mesh.position.x = f.baseX + w1 * 0.02;
      f.mat.opacity = 0.74 + Math.max(0, w1) * 0.24;
    }
    const spArr = sparkGeo.attributes.position.array;
    for (let i = 0; i < sparkCount; i++) {
      const m = sparkMeta[i];
      spArr[i * 3 + 1] += m.speed * dt;
      spArr[i * 3] = m.baseX + Math.sin(elapsed * 4.2 + m.phase) * 0.04;
      spArr[i * 3 + 2] = m.baseZ + Math.cos(elapsed * 3.1 + m.phase) * 0.06;
      if (spArr[i * 3 + 1] > 2.44) {
        spArr[i * 3 + 1] = 1.65 + (i % 3) * 0.04;
      }
    }
    sparkGeo.attributes.position.needsUpdate = true;

    // 3D Tennis ball physics bounce on 1F rug (y=0.42)
    if (ballAnim && ballAnim.active) {
      ballAnim.vy -= 14.0 * dt;
      tennisBall.position.x += ballAnim.vx * dt;
      tennisBall.position.y += ballAnim.vy * dt;
      tennisBall.position.z += ballAnim.vz * dt;
      if (tennisBall.position.y <= 0.42) {
        tennisBall.position.y = 0.42;
        ballAnim.vy = Math.abs(ballAnim.vy) * 0.56;
        ballAnim.vx *= 0.78;
        ballAnim.vz *= 0.78;
        if (ballAnim.vy < 0.35) ballAnim.active = false;
      }
    }

    if (swapRingsGroup.visible) {
      swapRingsGroup.position.set(bruce.root.position.x, bruce.root.position.y + 1.1, bruce.root.position.z);
      swapRingsGroup.rotation.y += dt * 1.4;
      swapRingsGroup.children.forEach((c, idx) => {
        c.rotation.z += dt * (0.6 + idx * 0.25);
      });
    }

    if (rippleAge >= 0) {
      rippleAge += dt;
      const p = rippleAge / 0.85;
      if (p >= 1) {
        rippleAge = -1;
        rippleMesh.visible = false;
      } else {
        rippleMesh.scale.setScalar(0.6 + p * 2.2);
        rippleMat.opacity = (1 - p) * 0.82;
      }
    }

    bruce.update(dt, elapsed);
    const rigDiag = bruce.getDiag?.();
    if (rigDiag) stageEl.dataset.rigDiag = JSON.stringify(rigDiag);
    const pDiag = {
      floor: activeFloor,
      duskMode,
      tvChannel: oldMoneyTv.getChannel(),
      camPos: camera.position.toArray().map((n) => +n.toFixed(2)),
      target: controls.target.toArray().map((n) => +n.toFixed(2)),
      brucePos: bruce.root.position.toArray().map((n) => +n.toFixed(2)),
      meteor: meteorCtrl.getState(),
      happiness,
    };
    window.__BRUCE_PENTHOUSE_DIAG__ = {
      ...pDiag,
      switchFloor: (fl) => switchFloor(fl, { animate: false, greet: false }),
      setOrbitPose: (pos, target) => {
        camTween = null;
        camera.position.fromArray(pos);
        controls.target.fromArray(target);
        controls.update();
      },
      nextTvChannel: () => cycleTvChannel(elapsed),
      toggleDusk: () => toggleSunsetDuskMood(),
      triggerMeteor: (b = null) => meteorCtrl.triggerNow(b),
    };
    if (Math.floor(elapsed * 2) !== Math.floor((elapsed - dt) * 2)) {
      stageEl.dataset.penthouseDiag = JSON.stringify(pDiag);
    }
    renderer.render(scene, camera);

    // Hide cinema subtitle when settle modal or swap celebration banner is shown
    const minPinTop = w < 640 ? 158 : 138;
    if (speechEl) {
      const hideForSettle = settleEl.classList.contains("is-visible") || swapBanner.classList.contains("is-visible");
      speechEl.style.display = hideForSettle ? "none" : "";
    }

    // Project 3D hotspots to 2D overlay (clamped safely away from floating HUD)
    if (!activeActId) {
      pinItems.forEach(({ world, btn }) => {
        projVec.copy(world).project(camera);
        if (projVec.z > 1 || projVec.z < -1) {
          btn.style.display = "none";
          return;
        }
        const sx = (projVec.x * 0.5 + 0.5) * w;
        const sy = (-projVec.y * 0.5 + 0.5) * h;
        if (sx < -60 || sx > w + 60 || sy < -40 || sy > h + 40) {
          btn.style.display = "none";
          return;
        }
        btn.style.display = "";
        const halfW = Math.max(52, (btn.offsetWidth || 120) * 0.5 + 12);
        btn.style.left = `${THREE.MathUtils.clamp(sx, halfW, Math.max(halfW, w - halfW - 110))}px`;
        btn.style.top = `${THREE.MathUtils.clamp(sy, minPinTop, h - 54)}px`;
      });
    }

    // 2D particle overlay
    fxCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
    fxCtx.clearRect(0, 0, w, h);
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.life += dt;
      if (p.life >= p.maxLife) {
        particles.splice(i, 1);
        continue;
      }
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      p.vy += (p.kind === "water" ? 200 : p.kind === "note" ? -30 : 35) * dt;
      fxCtx.save();
      fxCtx.globalAlpha = 1 - p.life / p.maxLife;
      if (p.kind === "water") {
        fxCtx.fillStyle = "#B8E4FF";
        fxCtx.beginPath();
        fxCtx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        fxCtx.fill();
      } else if (p.kind === "note") {
        fxCtx.fillStyle = "#FFE5A3";
        fxCtx.font = "bold 16px sans-serif";
        fxCtx.fillText("♪", p.x, p.y);
      } else {
        fxCtx.fillStyle = "#FFE39C";
        fxCtx.beginPath();
        fxCtx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        fxCtx.fill();
      }
      fxCtx.restore();
    }

    rafId = requestAnimationFrame(tick);
  };

  sfx.setSceneAmbience("penthouse", { floor: activeFloor, sulking });
  syncConciergeUi();
  rafId = requestAnimationFrame(tick);

  return {
    departToYacht: (o) => departToYachtMarina(o),
    setSulking(nextSulk) {
      applyAtmosphere(nextSulk, false);
    },
    setContext({ happiness: nextScore, content: nextContent }) {
      if (Number.isFinite(nextScore)) happiness = nextScore;
      if (nextContent) content = nextContent;
      if (!activeActId && loadingEl.classList.contains("is-hidden")) {
        sayBruce(sulking ? "idle_sulk" : "idle_happy", 5000);
      }
    },
    destroy() {
      if (destroyed) return;
      destroyed = true;
      sfx.setVinylMode(false);
      sfx.clearSceneAmbience("penthouse");
      delete window.__BRUCE_PENTHOUSE_DIAG__;
      document.body.classList.remove("is-hub3d-view", "is-hub3d-act");
      if (rafId) cancelAnimationFrame(rafId);
      actCleanup?.();
      timers.forEach((t) => clearTimeout(t));
      timers.clear();
      cleanups.forEach((fn) => fn());
      cleanups.length = 0;
      bruce.destroy();
      oldMoneyTv.dispose();
      terraceVista.dispose();
      meteorCtrl.dispose();
      controls.dispose();
      sunnySkyTex.dispose();
      rainySkyTex.dispose();
      patronCardTex.dispose();
      flameTex.dispose();
      skyCycloramaMat?.dispose?.();
      tvScreenMat?.dispose?.();
      patronCardMat?.dispose?.();
      flameGeo.dispose();
      flameMats.forEach((m) => m.dispose());
      sparkGeo.dispose();
      sparkMat.dispose();
      envRT.dispose();
      moteGeo.dispose();
      moteMat.dispose();
      rainGeo.dispose();
      rainMat.dispose();
      ballGeo.dispose();
      ballMat.dispose();
      rippleGeo.dispose();
      rippleMat.dispose();
      swapRingGeos.forEach((g) => g.dispose());
      swapRingMats.forEach((m) => m.dispose());
      if (roomRoot) {
        roomRoot.traverse((obj) => {
          if (obj.geometry) obj.geometry.dispose();
          const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
          mats.forEach((m) => {
            if (!m) return;
            m.map?.dispose?.();
            m.normalMap?.dispose?.();
            m.roughnessMap?.dispose?.();
            m.emissiveMap?.dispose?.();
            m.dispose?.();
          });
        });
      }
      renderer.dispose();
    },
  };
}
