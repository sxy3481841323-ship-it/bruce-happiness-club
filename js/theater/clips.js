export const THEATER_SCENES = [
  {
    id: "home_brush",
    zone: "home",
    title: "露台阳光顺毛",
    subtitle: "窗边 · 午后",
    desc: "午后暖阳斜进窗边，顺着奶油色长毛轻轻梳理；看见飞机耳预警及时松手，别碰吹风机也别刷手机。",
    win: 11,
    fail: -13,
    swapProb: 0,
    interaction: "brush",
    fallbackPoster: "./assets/img/scene_home.jpg",
    tintClass: "",
  },
  {
    id: "home_rain_vinyl",
    zone: "home",
    title: "雨窗擦爪听黑胶",
    subtitle: "客厅 · 雨天",
    desc: "雨点敲打落地窗，按顺序为布鲁斯擦干湿爪、披上毛毯，再落下黑胶唱针进入暖光陪听。",
    win: 12,
    fail: -12,
    swapProb: 0,
    interaction: "rainVinyl",
    fallbackPoster: "./assets/img/scene_home.jpg",
    tintClass: "th-tint-rain",
  },
  {
    id: "home_hide_seek",
    zone: "home",
    title: "客厅抛球寻宝",
    subtitle: "客厅 · 阳光",
    desc: "向上甩出网球看布鲁斯兴奋扑找，忍住别点角落滑出的手机推送，也别碰高速吹风筒。",
    win: 12,
    fail: -14,
    swapProb: 0.12,
    interaction: "fetch",
    fallbackPoster: "./assets/img/scene_home.jpg",
    tintClass: "",
  },
  {
    id: "street_cafe",
    zone: "street",
    title: "林荫街角探店",
    subtitle: "街角 · 午后",
    desc: "慢动作走过精品玻璃橱窗，看清 PAWS WELCOME 与 NO DOGS 门贴，选对可以进的店。",
    win: 14,
    fail: -18,
    swapProb: 0.22,
    interaction: "cafeDoors",
    fallbackPoster: "./assets/img/scene_street.jpg",
    tintClass: "",
  },
  {
    id: "street_bridge",
    zone: "street",
    title: "暮色水岸晚风",
    subtitle: "水岸 · 蓝调时刻",
    desc: "傍晚水岸微风轻拂，依次点亮三盏暖黄岸灯，躲开突然出现的喇叭与摩托噪音圈。",
    win: 14,
    fail: -16,
    swapProb: 0.14,
    interaction: "lanterns",
    fallbackPoster: "./assets/img/scene_street.jpg",
    tintClass: "th-tint-dusk",
  },
];

export function getScene(id) {
  return THEATER_SCENES.find((s) => s.id === id) || THEATER_SCENES[0];
}

export function getClipSources(scene) {
  const base = `./assets/clips/${scene.id}`;
  return {
    poster: `${base}/poster.jpg`,
    posterFallback: scene.fallbackPoster,
    intro: `${base}/intro.mp4`,
    introFallback: scene.fallbackPoster,
    win: `${base}/win.mp4`,
    winFallback: "./assets/img/bruce_happy.jpg",
    fail_phone: `${base}/fail_phone.mp4`,
    failPhoneFallback: "./assets/img/bruce_phone.jpg",
    fail_hazard: `${base}/fail_hazard.mp4`,
    failHazardFallback: "./assets/img/bruce_blocked.jpg",
    swap: `${base}/swap.mp4`,
    swapFallback: "./assets/img/bruce_happy.jpg",
  };
}
