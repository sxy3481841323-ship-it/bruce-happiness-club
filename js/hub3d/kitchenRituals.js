import * as THREE from "three";

/**
 * Modular controller for 1F South Marble-Grey Culinary Hall interactive rituals
 * (built at true 2.65x Penthouse scale), North-South ocean look-back, Pool/BBQ lighting,
 * and Built-In French Double-Door Refrigerator (±95° outward hinge swing).
 */
export function createKitchenRituals({
  scene,
  sfx,
  bruce,
  sayBruce,
  walkBruceTo,
  flyCamera,
  later,
  spawnFxParticles,
  stageEl,
  dockEl,
  fridgeDrawerEl,
  onOpenShop,
  onOpenSmartPanel,
  highlightTrickBtn,
}) {
  let fridgeLeftDoorPivot = null;
  let fridgeRightDoorPivot = null;
  let kitchenWineBottlePivot = null;
  let decanterWineMesh = null;

  const fridgeDoorMeshes = [];
  const espressoMeshes = [];
  const steakHerbMeshes = [];
  const champagneChefMeshes = [];
  const smartPanelMeshes = [];
  const grandEntryMeshes = [];
  const pianoMeshes = [];
  const golfMeshes = [];
  const sportGalleryMeshes = [];
  const poolMeshes = [];

  let fridgeOpenTarget = 0;
  let fridgeOpenAmount = 0;
  let chefStageOn = false;
  let courtyardLightsOn = true;
  let zoomiesQueue = [];

  // Lighting tuned for South Pietra-Grey Island, 7.1 WU Fridge & Outdoor Pool/BBQ Courtyard
  const kitchenPendantLight = new THREE.PointLight(0xffe6c4, 1.95, 34, 1.15);
  kitchenPendantLight.position.set(2.2, 6.4, 24.4);
  scene.add(kitchenPendantLight);

  const diningChandelierLight = new THREE.PointLight(0xffe2b8, 1.9, 26, 1.2);
  diningChandelierLight.position.set(0.0, 7.2, 31.0);
  scene.add(diningChandelierLight);

  const fridgeInteriorLight = new THREE.PointLight(0xebf6ff, 0.55, 18, 1.2);
  fridgeInteriorLight.position.set(13.40, 4.10, 19.90);
  scene.add(fridgeInteriorLight);

  const pianoSalonLight = new THREE.PointLight(0xffe6c2, 1.85, 34, 1.15);
  pianoSalonLight.position.set(22.4, 12.2, 0.8);
  scene.add(pianoSalonLight);

  const southCourtyardPoolLight = new THREE.PointLight(0x74d8ff, 2.3, 34, 1.15);
  southCourtyardPoolLight.position.set(-3.6, 3.8, 46.5);
  scene.add(southCourtyardPoolLight);

  const southCourtyardBbqLight = new THREE.PointLight(0xffbe7a, 1.9, 24, 1.25);
  southCourtyardBbqLight.position.set(11.4, 4.8, 41.2);
  scene.add(southCourtyardBbqLight);

  // Scaled espresso extraction stream at (12.82, 2.86 -> 2.40, 28.50)
  const espressoCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(12.82, 2.86, 28.50),
    new THREE.Vector3(12.82, 2.62, 28.50),
    new THREE.Vector3(12.82, 2.40, 28.50),
  ]);
  const espressoStreamGeo = new THREE.TubeGeometry(espressoCurve, 12, 0.020, 8, false);
  const espressoStreamMat = new THREE.MeshBasicMaterial({
    color: 0x6f3a18,
    transparent: true,
    opacity: 0.92,
  });
  const espressoStreamMesh = new THREE.Mesh(espressoStreamGeo, espressoStreamMat);
  espressoStreamMesh.visible = false;
  scene.add(espressoStreamMesh);

  // Scaled champagne arc pour stream into crystal decanter (-0.75, 2.32, 19.50)
  const champagneCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(-0.62, 3.24, 19.52),
    new THREE.Vector3(-0.71, 3.02, 19.51),
    new THREE.Vector3(-0.75, 2.74, 19.50),
    new THREE.Vector3(-0.75, 2.46, 19.50),
  ]);
  const champagneStreamGeo = new THREE.TubeGeometry(champagneCurve, 16, 0.024, 8, false);
  const champagneStreamMat = new THREE.MeshBasicMaterial({
    color: 0xf7df94,
    transparent: true,
    opacity: 0.90,
    depthWrite: false,
  });
  const champagneStreamMesh = new THREE.Mesh(champagneStreamGeo, champagneStreamMat);
  champagneStreamMesh.visible = false;
  scene.add(champagneStreamMesh);

  // Scaled rosemary sprig gliding from West herb counter (-13.6, 2.85, 20.1) to steak board (2.8, 2.52, 19.6)
  const rosemaryGeo = new THREE.CapsuleGeometry(0.036, 0.34, 4, 8);
  rosemaryGeo.rotateZ(Math.PI * 0.42);
  const rosemaryMat = new THREE.MeshStandardMaterial({ color: 0x3b6335, roughness: 0.65 });
  const rosemarySprigMesh = new THREE.Mesh(rosemaryGeo, rosemaryMat);
  rosemarySprigMesh.visible = false;
  scene.add(rosemarySprigMesh);

  // Rising simmering steam above Wolf 6-burner cookware suite (-13.45, 2.7..4.0, 18.8..22.1)
  const steamCount = 28;
  const steamPos = new Float32Array(steamCount * 3);
  for (let i = 0; i < steamCount; i++) {
    steamPos[i * 3] = -13.45 + ((i * 0.37) % 1.0) - 0.5;
    steamPos[i * 3 + 1] = 2.65 + ((i * 0.31) % 1.4);
    steamPos[i * 3 + 2] = 18.8 + ((i * 0.53) % 3.3);
  }
  const steamGeo = new THREE.BufferGeometry();
  steamGeo.setAttribute("position", new THREE.BufferAttribute(steamPos, 3));
  const steamMat = new THREE.PointsMaterial({
    color: 0xfff8ee,
    size: 0.16,
    transparent: true,
    opacity: 0.0,
    depthWrite: false,
  });
  const steamPoints = new THREE.Points(steamGeo, steamMat);
  scene.add(steamPoints);

  let espressoAnim = null;
  let steakAnim = null;
  let champagneAnim = null;
  let pendingFridgeLeft = [];
  let pendingFridgeRight = [];
  let pendingWineBottle = [];

  function collectMesh(obj) {
    if (/^FridgeDoorLeft|^FridgeDoorInsetLeft|^FridgeHandle.*Left/i.test(obj.name)) {
      pendingFridgeLeft.push(obj);
      fridgeDoorMeshes.push(obj);
    } else if (/^FridgeDoorRight|^FridgeDoorInsetRight|^FridgeHandle.*Right/i.test(obj.name)) {
      pendingFridgeRight.push(obj);
      fridgeDoorMeshes.push(obj);
    } else if (/^Fridge|^BioFresh/i.test(obj.name)) {
      fridgeDoorMeshes.push(obj);
    } else if (/^KitchenEspresso|^Coffee|^KitchenGranola/i.test(obj.name)) {
      espressoMeshes.push(obj);
    } else if (/^Wolf|^LeCreuset|^Mauviel|^StainlessSaucier|^CastIronGrill|^CarbonSteelWok|^BackSplashPotRail|^KitchenSteakBoard|^KitchenRawSteaks/i.test(obj.name)) {
      steakHerbMeshes.push(obj);
    } else if (/^KitchenPourBottle|^KitchenPourFoil/i.test(obj.name)) {
      pendingWineBottle.push(obj);
      champagneChefMeshes.push(obj);
    } else if (/^KitchenDecanterWine/i.test(obj.name)) {
      decanterWineMesh = obj;
      champagneChefMeshes.push(obj);
    } else if (/^Kitchen|^Bottle_|^Label_|^DiningTableMarble/i.test(obj.name)) {
      champagneChefMeshes.push(obj);
    } else if (/^SmartHomePanel/i.test(obj.name)) {
      smartPanelMeshes.push(obj);
    } else if (/^GrandEntryDoors|^GrandEntryDoor|^GrandEntryPulls/i.test(obj.name)) {
      grandEntryMeshes.push(obj);
    } else if (/^GrandPiano|^Piano(OpenLid|Bench|Fig)/i.test(obj.name)) {
      pianoMeshes.push(obj);
    } else if (/^Putting|^Golf/i.test(obj.name)) {
      golfMeshes.push(obj);
    } else if (/^Tennis|^Equestrian|^Saddle|^Dressage/i.test(obj.name)) {
      sportGalleryMeshes.push(obj);
    } else if (/^pool_water|^lounge_|^bbq_/i.test(obj.name)) {
      poolMeshes.push(obj);
    }
  }

  function attachPivots(roomRoot) {
    if (pendingFridgeLeft.length) {
      fridgeLeftDoorPivot = new THREE.Group();
      fridgeLeftDoorPivot.position.set(12.35, 4.05, 16.05);
      roomRoot.add(fridgeLeftDoorPivot);
      pendingFridgeLeft.forEach((m) => {
        fridgeLeftDoorPivot.add(m);
        m.position.set(-12.35, -4.05, -16.05);
      });
    }
    if (pendingFridgeRight.length) {
      fridgeRightDoorPivot = new THREE.Group();
      fridgeRightDoorPivot.position.set(12.35, 4.05, 23.75);
      roomRoot.add(fridgeRightDoorPivot);
      pendingFridgeRight.forEach((m) => {
        fridgeRightDoorPivot.add(m);
        m.position.set(-12.35, -4.05, -23.75);
      });
    }
    if (pendingWineBottle.length) {
      kitchenWineBottlePivot = new THREE.Group();
      kitchenWineBottlePivot.position.set(0.10, 2.70, 19.55);
      roomRoot.add(kitchenWineBottlePivot);
      pendingWineBottle.forEach((m) => {
        kitchenWineBottlePivot.add(m);
        m.position.set(-0.10, -2.70, -19.55);
      });
    }
    pendingFridgeLeft = [];
    pendingFridgeRight = [];
    pendingWineBottle = [];
  }

  const poolDockEl = stageEl?.querySelector("#hub3d-pool-dock");
  const clubDockEl = stageEl?.querySelector("#hub3d-club-dock");

  function setDockVisibility(floorId) {
    const showK = floorId === "kitchen" || fridgeOpenTarget > 0.5;
    dockEl?.classList.toggle("is-visible", showK);
    dockEl?.classList.toggle("is-hidden-for-fridge", fridgeOpenTarget > 0.5);
    poolDockEl?.classList.toggle("is-visible", floorId === "pool");
    clubDockEl?.classList.toggle("is-visible", floorId === "club");
    document.body.classList.toggle("is-kitchen-floor", showK || floorId === "pool" || floorId === "club");
    if (floorId !== "kitchen" && fridgeOpenTarget < 0.5) {
      fridgeDrawerEl?.classList.remove("is-open");
    }
  }

  function toggleFridge(forceOpen = null) {
    const next = forceOpen === null ? fridgeOpenTarget < 0.5 : Boolean(forceOpen);
    fridgeOpenTarget = next ? 1 : 0;
    fridgeDrawerEl?.classList.toggle("is-open", next);
    dockEl?.classList.toggle("is-hidden-for-fridge", next);
    dockEl?.querySelector('[data-kitchen-act="fridge"]')?.classList.toggle("is-active", next);
    sfx.playTap();
    if (next) {
      setDockVisibility("kitchen");
      flyCamera(
        new THREE.Vector3(2.4, 4.35, 19.90),
        new THREE.Vector3(13.5, 4.05, 19.90),
        780,
      );
      walkBruceTo(9.2, 23.8, { silent: true });
      sayBruce(
        "整面 7.8 单位内嵌双门冰箱全景拉开——顶层有机鲜奶与无糖醇厚希腊酸奶，中层蓝莓、牛油果、黄柠檬与时蔬保鲜盒，底层 0°C 抽屉备着肋眼牛排与鲜肉食材。",
        5200,
        "KITCHEN · 内嵌双门鲜食库",
      );
    } else {
      sayBruce("轻推合上哑光炭灰暗门，双开门齐平收进高柜墙里。", 3000, "KITCHEN · 隐形收合");
    }
    return next;
  }

  function serveYogurtBowl() {
    sfx.playGlassPour();
    const r = stageEl.getBoundingClientRect();
    spawnFxParticles(r.width * 0.48, r.height * 0.52, "water", 14);
    toggleFridge(false);
    flyCamera(
      new THREE.Vector3(-1.8, 3.75, 15.2),
      new THREE.Vector3(1.2, 2.45, 18.6),
      740,
    );
    sayBruce(
      "舀一大碗无糖醇厚希腊酸奶配新鲜蓝莓与烤谷物放在炭灰大理石岛台上，透窗遥望池畔与雪峰。",
      4600,
      "KITCHEN · 晨间酸奶碗",
    );
  }

  function startZoomies() {
    zoomiesQueue = [
      [-3.6, 17.0],
      [-3.6, 22.4],
      [9.8, 22.4],
      [9.8, 16.8],
      [-2.4, 17.6],
    ];
    const [nx, nz] = zoomiesQueue.shift();
    bruce.setResting(null);
    bruce.walkTo(nx, nz, { speedScale: 1.85 });
    later(() => bruce.triggerHappyHop?.(), 420);
  }

  function startMorningEspresso() {
    espressoAnim = { t: 0, dur: 2.8, soundPlayed: false, zoomiesStarted: false };
    sfx.playTap();
    const r = stageEl.getBoundingClientRect();
    spawnFxParticles(r.width * 0.56, r.height * 0.48, "warm", 14);
    flyCamera(
      new THREE.Vector3(5.6, 4.15, 24.4),
      new THREE.Vector3(13.0, 2.95, 26.45),
      780,
    );
    sayBruce(
      "不必等闹钟，浓缩油脂流进瓷杯配烤燕麦坚果棒，窗外山脊泛亮，本汪绕着 10.6 单位大岛台先跑两圈早安 Zoomies！",
      5000,
      "RITUAL · 晨间手冲与奔跑",
    );
  }

  function startHerbSteakPrep() {
    steakAnim = { t: 0, dur: 2.9, doneWalk: false };
    chefStageOn = true;
    sfx.playTap();
    rosemarySprigMesh.visible = true;
    rosemarySprigMesh.position.set(-13.6, 2.95, 20.1);
    const r = stageEl.getBoundingClientRect();
    spawnFxParticles(r.width * 0.5, r.height * 0.52, "warm", 14);
    flyCamera(
      new THREE.Vector3(-5.6, 4.1, 20.5),
      new THREE.Vector3(-13.4, 3.1, 20.5),
      780,
    );
    sayBruce(
      "60 寸 Wolf 六头红旋钮灶台上正齐声开火：焰红 Le Creuset 铸铁珐琅锅慢炖高汤、锤纹铜汤锅文火收汁、铸铁烤盘煎肋眼，中式碳钢炒锅与背墙黄铜挂架铜锅一应俱全！",
      5200,
      "CHEF · Wolf 灶台与七件名锅",
    );
  }

  function startChampagneChefStage() {
    chefStageOn = !chefStageOn;
    champagneAnim = { t: 0, dur: 2.6, poured: false };
    dockEl?.querySelector('[data-kitchen-act="champagne"]')?.classList.toggle("is-active", chefStageOn);
    sfx.playConciergeBell();
    const r = stageEl.getBoundingClientRect();
    spawnFxParticles(r.width * 0.5, r.height * 0.5, "gold", 16);
    flyCamera(
      new THREE.Vector3(-3.4, 4.35, 15.6),
      new THREE.Vector3(0.8, 2.55, 19.5),
      820,
    );
    sayBruce(
      chefStageOn
        ? "入夜把灰云石大岛台切成私厨剧场，线型吊灯聚光，香槟缓缓注入水晶醒酒器，铁板台升起细暖微烟。"
        : "收起铁板热烟，留一杯微晃香槟陪着法式推拉门外的山风发呆。",
      5000,
      "RITUAL · 私厨剧场与醒酒",
    );
  }

  function lookNorthToOcean() {
    sfx.playTap();
    flyCamera(
      new THREE.Vector3(3.2, 4.45, 24.8),
      new THREE.Vector3(1.2, 2.75, -18.0),
      860,
    );
    walkBruceTo(3.2, 22.6, { silent: true });
    sayBruce(
      "站在主厨岛台后方朝北望去，视线直穿客厅与壁炉落日海景落地窗——全屋发生的一切与远方海平线尽收眼底。",
      5200,
      "C-AXIS · 岛台回望大海",
    );
  }

  function toggleCourtyardLights(force = null) {
    courtyardLightsOn = force === null ? !courtyardLightsOn : Boolean(force);
    southCourtyardPoolLight.intensity = courtyardLightsOn ? 2.1 : 0.15;
    southCourtyardBbqLight.intensity = courtyardLightsOn ? 1.8 : 0.12;
    return courtyardLightsOn;
  }

  function focusDiningHall() {
    sfx.playTap();
    flyCamera(
      new THREE.Vector3(-8.2, 4.6, 22.8),
      new THREE.Vector3(1.2, 2.3, 33.6),
      800,
    );
    walkBruceTo(0.8, 28.0, { silent: true });
    sayBruce("穿过备餐岛台就是独立长形正餐宴会厅，八张羊羔绒餐椅围着整块炭灰大理石餐桌，正对黑色法式落地门外的无边泳池与阿尔卑斯雪峰。", 5200, "DINING · 独立山景长桌正餐厅");
  }

  // Interactive 3D Golf Putting Ball rolling toward center putting cup (31.0, 0.14, 9.0)
  const golfPutBall = new THREE.Mesh(
    new THREE.SphereGeometry(0.11, 14, 10),
    new THREE.MeshStandardMaterial({ color: 0xf8f8f4, roughness: 0.28 }),
  );
  golfPutBall.visible = false;
  scene.add(golfPutBall);
  let golfPutAnim = null;

  function playGrandPiano() {
    sfx.playPianoNocturne?.();
    const r = stageEl.getBoundingClientRect();
    spawnFxParticles(r.width * 0.5, r.height * 0.48, "note", 16);
    flyCamera(
      new THREE.Vector3(25.6, 4.3, -13.2),
      new THREE.Vector3(44.0, 2.4, -6.8),
      800,
    );
    walkBruceTo(25.6, -9.6, { silent: true });
    later(() => bruce.triggerHappyHop?.(), 650);
    sayBruce("在弧形全景落地窗前奏响九尺黑檀木三角钢琴与夜曲乐谱，窗外跨河斜拉大桥与暮色天际线正一点点亮起灯火。", 5200, "CLUB · 黑檀木三角钢琴");
  }

  function practicePuttingGreen() {
    sfx.playGolfPutt?.();
    golfPutAnim = { t: 0, dur: 1.15 };
    golfPutBall.visible = true;
    golfPutBall.position.set(25.0, 0.18, 5.2);
    const r = stageEl.getBoundingClientRect();
    spawnFxParticles(r.width * 0.54, r.height * 0.54, "gold", 14);
    flyCamera(
      new THREE.Vector3(19.8, 4.6, 2.8),
      new THREE.Vector3(33.5, 1.6, 8.6),
      800,
    );
    walkBruceTo(24.2, 6.2, { silent: true });
    sayBruce("在加宽果岭上一杆清脆推进！右侧背光壁龛陈列着三支钛合金一号木、五支锻铁杆与黄铜推杆，旁边立着墨绿真皮球包。", 5000, "CLUB · 果岭一杆进洞");
  }

  function inspectSportGallery() {
    sfx.playTap();
    flyCamera(
      new THREE.Vector3(28.5, 4.4, 4.2),
      new THREE.Vector3(28.5, 3.2, 14.6),
      780,
    );
    walkBruceTo(26.2, 10.6, { silent: true });
    sayBruce("南侧浅米白背光陈列柜里清晰勾勒出带白色网线的交叉网球拍、干邑色英式马术盛装舞步鞍垫与双马靴头盔。", 5000, "CLUB · 网球与马术背光陈列廊");
  }

  function enjoyPoolside() {
    sfx.playGlassPour();
    const r = stageEl.getBoundingClientRect();
    spawnFxParticles(r.width * 0.45, r.height * 0.55, "water", 14);
    flyCamera(
      new THREE.Vector3(-8.6, 3.6, 40.4),
      new THREE.Vector3(-2.4, 1.2, 56.0),
      820,
    );
    walkBruceTo(-11.8, 43.2, { silent: true });
    sayBruce("跨出法式推拉门就是户外蓝绿无边恒温泳池，柚木躺椅旁支着遮阳伞，水光映着冰湖与积雪险峰。", 5000, "POOL · 无边泳池与柚木躺椅");
  }

  function igniteOutdoorBbq() {
    sfx.playTap();
    const r = stageEl.getBoundingClientRect();
    spawnFxParticles(r.width * 0.6, r.height * 0.5, "warm", 14);
    toggleCourtyardLights(true);
    flyCamera(
      new THREE.Vector3(4.2, 3.9, 37.0),
      new THREE.Vector3(11.4, 2.0, 41.2),
      780,
    );
    walkBruceTo(7.4, 39.2, { silent: true });
    sayBruce("开启户外不锈钢燃气 BBQ 烧烤吧台！傍晚风一吹过花坛迷迭香，就可以把肋眼端到泳池畔现烤了。", 5000, "COURTYARD · 户外 BBQ 炉台");
  }

  function gazeAlpinePeaks() {
    sfx.playConciergeBell();
    flyCamera(
      new THREE.Vector3(0.0, 5.2, 46.8),
      new THREE.Vector3(0.0, 12.0, 118.0),
      900,
    );
    walkBruceTo(0.8, 40.6, { silent: true });
    sayBruce("站在无边泳池畔远望，翡翠冰湖尽头是两座险峻的阿尔卑斯白云石雪峰，夕阳正洒满冰川雪脊。", 5200, "ALPINE · 雪冠险峰与冰湖");
  }

  function handleRaycastHit(hitObj) {
    if (smartPanelMeshes.includes(hitObj)) {
      onOpenSmartPanel?.();
      return true;
    }
    if (grandEntryMeshes.includes(hitObj)) {
      flyCamera(
        new THREE.Vector3(-7.6, 4.2, -3.6),
        new THREE.Vector3(-14.7, 3.8, -3.6),
        740,
      );
      sayBruce("铸铜灰云石双开大门旁就是深邃黑曜石全屋智能中控屏，点一下屏幕就能总控灯光、壁炉、哈曼与泳池。", 4400, "FOYER · 双开入户大门");
      return true;
    }
    if (fridgeDoorMeshes.includes(hitObj)) {
      toggleFridge();
      return true;
    }
    if (espressoMeshes.includes(hitObj)) {
      startMorningEspresso();
      return true;
    }
    if (steakHerbMeshes.includes(hitObj)) {
      startHerbSteakPrep();
      return true;
    }
    if (champagneChefMeshes.includes(hitObj)) {
      startChampagneChefStage();
      return true;
    }
    if (pianoMeshes.includes(hitObj)) {
      playGrandPiano();
      return true;
    }
    if (golfMeshes.includes(hitObj)) {
      practicePuttingGreen();
      return true;
    }
    if (sportGalleryMeshes.includes(hitObj)) {
      inspectSportGallery();
      return true;
    }
    if (poolMeshes.includes(hitObj)) {
      if (/^bbq_/i.test(hitObj.name)) igniteOutdoorBbq();
      else enjoyPoolside();
      return true;
    }
    return false;
  }

  dockEl?.querySelectorAll("[data-kitchen-act]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const act = btn.getAttribute("data-kitchen-act");
      if (act === "fridge") toggleFridge();
      else if (act === "espresso") startMorningEspresso();
      else if (act === "steak") startHerbSteakPrep();
      else if (act === "champagne") startChampagneChefStage();
      else if (act === "dining") focusDiningHall();
      else if (act === "ocean") lookNorthToOcean();
    });
  });

  poolDockEl?.querySelectorAll("[data-pool-act]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const act = btn.getAttribute("data-pool-act");
      if (act === "lounger") enjoyPoolside();
      else if (act === "bbq") igniteOutdoorBbq();
      else if (act === "alps") gazeAlpinePeaks();
    });
  });

  clubDockEl?.querySelectorAll("[data-club-act]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const act = btn.getAttribute("data-club-act");
      if (act === "piano") playGrandPiano();
      else if (act === "golf") practicePuttingGreen();
      else if (act === "sport") inspectSportGallery();
    });
  });

  fridgeDrawerEl?.querySelector("#btn-fridge-yogurt")?.addEventListener("click", (e) => {
    e.stopPropagation();
    serveYogurtBowl();
  });
  fridgeDrawerEl?.querySelector("#btn-fridge-pantry")?.addEventListener("click", (e) => {
    e.stopPropagation();
    sfx.playTap();
    fridgeDrawerEl.classList.remove("is-open");
    onOpenShop?.();
  });
  fridgeDrawerEl?.querySelector("#btn-fridge-close")?.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleFridge(false);
  });

  function update(dt, elapsed, duskMode) {
    fridgeOpenAmount = THREE.MathUtils.lerp(fridgeOpenAmount, fridgeOpenTarget, Math.min(1, dt * 6.5));
    const swingRad = fridgeOpenAmount * 1.65;
    if (fridgeLeftDoorPivot) fridgeLeftDoorPivot.rotation.y = -swingRad;
    if (fridgeRightDoorPivot) fridgeRightDoorPivot.rotation.y = swingRad;
    fridgeInteriorLight.intensity = 0.55 + fridgeOpenAmount * 3.85;
    kitchenPendantLight.intensity = chefStageOn ? 3.25 : duskMode ? 2.45 : 1.85;

    if (zoomiesQueue.length > 0 && !bruce.isWalking?.()) {
      const [nx, nz] = zoomiesQueue.shift();
      bruce.walkTo(nx, nz, { speedScale: 1.82 });
      if (zoomiesQueue.length === 0) {
        later(() => {
          bruce.playAction("play_bow");
          highlightTrickBtn?.("play_bow");
        }, 700);
      }
    }

    if (espressoAnim) {
      espressoAnim.t += dt;
      const t = espressoAnim.t;
      espressoStreamMesh.visible = t >= 0.35 && t <= 1.95;
      if (espressoStreamMesh.visible && !espressoAnim.soundPlayed) {
        espressoAnim.soundPlayed = true;
        sfx.playGlassPour();
      }
      if (t >= 0.9 && !espressoAnim.zoomiesStarted) {
        espressoAnim.zoomiesStarted = true;
        startZoomies();
      }
      if (t >= espressoAnim.dur) {
        espressoAnim = null;
        espressoStreamMesh.visible = false;
      }
    }

    if (steakAnim) {
      steakAnim.t += dt;
      const p = Math.min(1, steakAnim.t / 1.45);
      const ease = p * p * (3 - 2 * p);
      rosemarySprigMesh.position.set(
        THREE.MathUtils.lerp(-13.6, 2.8, ease),
        2.56 + Math.sin(ease * Math.PI) * 1.15,
        THREE.MathUtils.lerp(20.1, 19.6, ease),
      );
      rosemarySprigMesh.rotation.y = ease * Math.PI * 1.5;
      if (steakAnim.t >= 1.2 && !steakAnim.doneWalk) {
        steakAnim.doneWalk = true;
        walkBruceTo(-2.8, 19.4, { silent: true });
        later(() => bruce.playAction("lick_paw"), 750);
      }
      if (steakAnim.t >= steakAnim.dur) {
        steakAnim = null;
      }
    }

    if (champagneAnim) {
      champagneAnim.t += dt;
      const t = champagneAnim.t;
      const cl = (v) => Math.max(0, Math.min(1, v));
      const sm = (u) => u * u * (3 - 2 * u);
      let lift = 0;
      if (t < 0.65) lift = sm(cl(t / 0.65));
      else if (t < 1.85) lift = 1;
      else lift = 1 - sm(cl((t - 1.85) / 0.70));

      if (kitchenWineBottlePivot) {
        kitchenWineBottlePivot.position.set(
          0.10 - lift * 0.28,
          2.76 + lift * 0.62,
          19.55 - lift * 0.02,
        );
        kitchenWineBottlePivot.rotation.z = 1.12 * lift;
      }
      const pouring = t >= 0.55 && t <= 1.75;
      champagneStreamMesh.visible = pouring;
      if (pouring && !champagneAnim.poured) {
        champagneAnim.poured = true;
        sfx.playGlassPour();
      }
      if (decanterWineMesh && pouring) {
        decanterWineMesh.position.y = cl((t - 0.55) / 1.2) * 0.05;
      }
      if (t >= champagneAnim.dur) {
        champagneAnim = null;
        champagneStreamMesh.visible = false;
        if (kitchenWineBottlePivot) {
          kitchenWineBottlePivot.position.set(0.10, 2.76, 19.55);
          kitchenWineBottlePivot.rotation.set(0, 0, 0);
        }
      }
    }

    if (golfPutAnim) {
      golfPutAnim.t += dt;
      const u = Math.min(1, golfPutAnim.t / golfPutAnim.dur);
      const ease = 1 - Math.pow(1 - u, 3);
      golfPutBall.position.set(
        THREE.MathUtils.lerp(25.0, 31.0, ease),
        0.18 - (u > 0.88 ? (u - 0.88) * 0.9 : 0),
        THREE.MathUtils.lerp(5.2, 9.0, ease) - Math.sin(u * Math.PI) * 0.45,
      );
      if (u >= 1) {
        golfPutAnim = null;
        golfPutBall.visible = false;
        bruce.triggerHappyHop?.();
      }
    }

    steamPoints.visible = chefStageOn;
    if (chefStageOn) {
      steamMat.opacity = 0.28 + Math.sin(elapsed * 2.1) * 0.08;
      const arr = steamGeo.attributes.position.array;
      for (let i = 0; i < steamCount; i++) {
        arr[i * 3 + 1] += dt * 0.52;
        if (arr[i * 3 + 1] > 4.2) arr[i * 3 + 1] = 2.6 + (i % 4) * 0.08;
      }
      steamGeo.attributes.position.needsUpdate = true;
    }
  }

  function dispose() {
    document.body.classList.remove("is-kitchen-floor");
    golfPutBall.geometry.dispose();
    golfPutBall.material.dispose();
    espressoStreamGeo.dispose();
    espressoStreamMat.dispose();
    champagneStreamGeo.dispose();
    champagneStreamMat.dispose();
    rosemaryGeo.dispose();
    rosemaryMat.dispose();
    steamGeo.dispose();
    steamMat.dispose();
  }

  return {
    collectMesh,
    attachPivots,
    setDockVisibility,
    toggleFridge,
    startMorningEspresso,
    startHerbSteakPrep,
    startChampagneChefStage,
    focusDiningHall,
    playGrandPiano,
    practicePuttingGreen,
    inspectSportGallery,
    enjoyPoolside,
    igniteOutdoorBbq,
    gazeAlpinePeaks,
    lookNorthToOcean,
    toggleCourtyardLights,
    handleRaycastHit,
    getInteractiveMeshes: () => [
      ...fridgeDoorMeshes,
      ...espressoMeshes,
      ...steakHerbMeshes,
      ...champagneChefMeshes,
      ...smartPanelMeshes,
      ...grandEntryMeshes,
      ...pianoMeshes,
      ...golfMeshes,
      ...sportGalleryMeshes,
      ...poolMeshes,
    ],
    getState: () => ({
      fridgeOpen: fridgeOpenTarget > 0.5,
      fridgeOpenAmount: +fridgeOpenAmount.toFixed(2),
      chefStageOn,
      courtyardLightsOn,
    }),
    update,
    dispose,
  };
}
