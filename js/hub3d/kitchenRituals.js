import * as THREE from "three";

/**
 * Modular controller for 1F West Mountain-View Kitchen interactive rituals:
 * 1. Built-in French Double-Door Refrigerator (±96° hinged swing, 4200K LED, dairy/produce HUD)
 * 2. Morning Espresso Extraction + Granola Bar + Bruce Zoomies lap around the island
 * 3. Herb Window Rosemary Snip + Sea-Salt Ribeye Prep + Bruce tasting dish
 * 4. Evening Champagne Decanting + Chef's Table Teppanyaki Stage
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

  let fridgeOpenTarget = 0;
  let fridgeOpenAmount = 0;
  let chefStageOn = false;
  let zoomiesQueue = [];

  // Lighting tuned for Calacatta Viola waterfall island & bright fridge showcase
  const kitchenPendantLight = new THREE.PointLight(0xffe0b2, 1.35, 16, 1.3);
  kitchenPendantLight.position.set(-10.4, 2.24, -9.8);
  scene.add(kitchenPendantLight);

  const fridgeInteriorLight = new THREE.PointLight(0xebf6ff, 0.35, 7, 1.35);
  fridgeInteriorLight.position.set(-14.28, 1.72, -3.20);
  scene.add(fridgeInteriorLight);

  // Espresso crema pour stream (-14.09, 1.31 -> 1.09, -5.20)
  const espressoCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(-14.09, 1.31, -5.20),
    new THREE.Vector3(-14.085, 1.22, -5.20),
    new THREE.Vector3(-14.08, 1.11, -5.20),
  ]);
  const espressoStreamGeo = new THREE.TubeGeometry(espressoCurve, 12, 0.008, 8, false);
  const espressoStreamMat = new THREE.MeshBasicMaterial({
    color: 0x6f3a18,
    transparent: true,
    opacity: 0.92,
  });
  const espressoStreamMesh = new THREE.Mesh(espressoStreamGeo, espressoStreamMat);
  espressoStreamMesh.visible = false;
  scene.add(espressoStreamMesh);

  // Champagne arc pour stream into crystal decanter (-10.24, 1.30 -> -10.22, 1.00, -12.06)
  const champagneCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(-10.26, 1.30, -12.08),
    new THREE.Vector3(-10.23, 1.22, -12.07),
    new THREE.Vector3(-10.22, 1.08, -12.06),
    new THREE.Vector3(-10.22, 0.98, -12.06),
  ]);
  const champagneStreamGeo = new THREE.TubeGeometry(champagneCurve, 16, 0.010, 8, false);
  const champagneStreamMat = new THREE.MeshBasicMaterial({
    color: 0xf7df94,
    transparent: true,
    opacity: 0.88,
    depthWrite: false,
  });
  const champagneStreamMesh = new THREE.Mesh(champagneStreamGeo, champagneStreamMat);
  champagneStreamMesh.visible = false;
  scene.add(champagneStreamMesh);

  // Gliding rosemary sprig for afternoon steak prep
  const rosemaryGeo = new THREE.CapsuleGeometry(0.016, 0.14, 4, 8);
  rosemaryGeo.rotateZ(Math.PI * 0.42);
  const rosemaryMat = new THREE.MeshStandardMaterial({ color: 0x45693d, roughness: 0.65 });
  const rosemarySprigMesh = new THREE.Mesh(rosemaryGeo, rosemaryMat);
  rosemarySprigMesh.visible = false;
  scene.add(rosemarySprigMesh);

  // Subtle teppanyaki & steam motes above (-10.55, 0.96, -8.0)
  const steamCount = 24;
  const steamPos = new Float32Array(steamCount * 3);
  for (let i = 0; i < steamCount; i++) {
    steamPos[i * 3] = -10.55 + ((i * 0.19) % 0.56) - 0.28;
    steamPos[i * 3 + 1] = 0.96 + ((i * 0.13) % 0.65);
    steamPos[i * 3 + 2] = -8.00 + ((i * 0.27) % 0.88) - 0.44;
  }
  const steamGeo = new THREE.BufferGeometry();
  steamGeo.setAttribute("position", new THREE.BufferAttribute(steamPos, 3));
  const steamMat = new THREE.PointsMaterial({
    color: 0xfff8ee,
    size: 0.085,
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
    if (/^FridgeDoorLeft|^FridgeHandleLeft/i.test(obj.name)) {
      pendingFridgeLeft.push(obj);
      fridgeDoorMeshes.push(obj);
    } else if (/^FridgeDoorRight|^FridgeHandleRight/i.test(obj.name)) {
      pendingFridgeRight.push(obj);
      fridgeDoorMeshes.push(obj);
    } else if (/^Fridge/i.test(obj.name)) {
      fridgeDoorMeshes.push(obj);
    } else if (/^KitchenEspresso|^KitchenGranola/i.test(obj.name)) {
      espressoMeshes.push(obj);
    } else if (/^KitchenHerb|^KitchenSteakBoard|^KitchenRawSteaks|^KitchenSaltBowl/i.test(obj.name)) {
      steakHerbMeshes.push(obj);
    } else if (/^KitchenPourBottle|^KitchenPourFoil/i.test(obj.name)) {
      pendingWineBottle.push(obj);
      champagneChefMeshes.push(obj);
    } else if (/^KitchenDecanterWine/i.test(obj.name)) {
      decanterWineMesh = obj;
      champagneChefMeshes.push(obj);
    } else if (/^KitchenWine|^KitchenCoupes|^KitchenTeppanyaki/i.test(obj.name)) {
      champagneChefMeshes.push(obj);
    }
  }

  function attachPivots(roomRoot) {
    if (pendingFridgeLeft.length) {
      fridgeLeftDoorPivot = new THREE.Group();
      fridgeLeftDoorPivot.position.set(-13.86, 1.34, -4.27);
      roomRoot.add(fridgeLeftDoorPivot);
      pendingFridgeLeft.forEach((m) => {
        fridgeLeftDoorPivot.add(m);
        m.position.set(13.86, -1.34, 4.27);
      });
    }
    if (pendingFridgeRight.length) {
      fridgeRightDoorPivot = new THREE.Group();
      fridgeRightDoorPivot.position.set(-13.86, 1.34, -2.13);
      roomRoot.add(fridgeRightDoorPivot);
      pendingFridgeRight.forEach((m) => {
        fridgeRightDoorPivot.add(m);
        m.position.set(13.86, -1.34, 2.13);
      });
    }
    if (pendingWineBottle.length) {
      kitchenWineBottlePivot = new THREE.Group();
      kitchenWineBottlePivot.position.set(-10.55, 1.08, -12.10);
      roomRoot.add(kitchenWineBottlePivot);
      pendingWineBottle.forEach((m) => {
        kitchenWineBottlePivot.add(m);
        m.position.set(10.55, -1.08, 12.10);
      });
    }
    pendingFridgeLeft = [];
    pendingFridgeRight = [];
    pendingWineBottle = [];
  }

  function setDockVisibility(floorId) {
    const show = floorId === "kitchen" || fridgeOpenTarget > 0.5;
    dockEl?.classList.toggle("is-visible", show);
    document.body.classList.toggle("is-kitchen-floor", show);
    if (floorId !== "kitchen" && fridgeOpenTarget < 0.5) {
      fridgeDrawerEl?.classList.remove("is-open");
    }
  }

  function toggleFridge(forceOpen = null) {
    const next = forceOpen === null ? fridgeOpenTarget < 0.5 : Boolean(forceOpen);
    fridgeOpenTarget = next ? 1 : 0;
    fridgeDrawerEl?.classList.toggle("is-open", next);
    dockEl?.querySelector('[data-kitchen-act="fridge"]')?.classList.toggle("is-active", next);
    sfx.playTap();
    if (next) {
      setDockVisibility("kitchen");
      flyCamera(
        new THREE.Vector3(-9.2, 2.05, -2.65),
        new THREE.Vector3(-14.25, 1.48, -3.20),
        760,
      );
      walkBruceTo(-12.2, -3.3, { silent: true });
      sayBruce(
        "嵌入式双门鲜食冰箱拉开啦——上层有有机鲜奶与 0% 无糖希腊酸奶，中层码满蓝莓、树莓、牛油果和鲜蔬，底层 0°C 抽屉还备着你的鲜切牛排与本汪的冰鲜食。",
        5200,
        "KITCHEN · 内嵌双门鲜食库",
      );
    } else {
      sayBruce("轻推合上胡桃木暗门，双开门齐平隐进厨电墙里。", 3000, "KITCHEN · 隐形收合");
    }
    return next;
  }

  function serveYogurtBowl() {
    sfx.playGlassPour();
    const r = stageEl.getBoundingClientRect();
    spawnFxParticles(r.width * 0.48, r.height * 0.52, "water", 14);
    toggleFridge(false);
    flyCamera(
      new THREE.Vector3(-7.6, 1.95, -7.8),
      new THREE.Vector3(-10.1, 0.96, -8.8),
      720,
    );
    sayBruce(
      "舀两勺 0% 无糖希腊酸奶配新鲜蓝莓树莓放在紫脉石岛台上，窗外是晨雾山脊，什么正事也不干才最舒坦。",
      4600,
      "KITCHEN · 晨间酸奶碗",
    );
  }

  function startZoomies() {
    zoomiesQueue = [
      [-8.6, -13.6],
      [-12.6, -10.6],
      [-12.4, -5.8],
      [-8.5, -6.2],
      [-8.6, -9.4],
    ];
    const [nx, nz] = zoomiesQueue.shift();
    bruce.setResting(null);
    bruce.walkTo(nx, nz, { speedScale: 1.82 });
    later(() => bruce.triggerHappyHop?.(), 420);
  }

  function startMorningEspresso() {
    espressoAnim = { t: 0, dur: 2.8, soundPlayed: false, zoomiesStarted: false };
    sfx.playTap();
    const r = stageEl.getBoundingClientRect();
    spawnFxParticles(r.width * 0.42, r.height * 0.48, "warm", 14);
    flyCamera(
      new THREE.Vector3(-10.4, 2.08, -4.0),
      new THREE.Vector3(-14.2, 1.28, -5.05),
      780,
    );
    sayBruce(
      "不用闹钟，咖啡豆香配手烤燕麦坚果棒在西窗下慢慢散开，本汪绕着整石大岛台先跑两圈早安 Zoomies！",
      5000,
      "RITUAL · 晨间手冲与奔跑",
    );
  }

  function startHerbSteakPrep() {
    steakAnim = { t: 0, dur: 2.9, doneWalk: false };
    sfx.playTap();
    rosemarySprigMesh.visible = true;
    rosemarySprigMesh.position.set(-14.3, 1.38, -9.1);
    const r = stageEl.getBoundingClientRect();
    spawnFxParticles(r.width * 0.46, r.height * 0.52, "gold", 14);
    flyCamera(
      new THREE.Vector3(-8.2, 2.25, -8.4),
      new THREE.Vector3(-11.2, 1.02, -10.2),
      780,
    );
    sayBruce(
      "从西窗香草园现剪一枝迷迭香，三块厚切肋眼排排坐落盐静置，岛台边黄铜小碟里也分好了本汪的一小口无盐鲜肉～",
      5000,
      "RITUAL · 窗边采香与慢切",
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
      new THREE.Vector3(-7.4, 2.25, -13.6),
      new THREE.Vector3(-10.5, 1.10, -10.8),
      820,
    );
    sayBruce(
      chefStageOn
        ? "入夜把紫脉岛台切成私厨社交剧场，琥珀吊灯聚光，香槟沿水晶醒酒器徐徐流下，铁板温热微烟。"
        : "收起铁板热烟，留一杯微晃香槟在岛台边陪山风发呆。",
      5000,
      "RITUAL · 私厨剧场与醒酒",
    );
  }

  function handleRaycastHit(hitObj) {
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
    return false;
  }

  // Bind Kitchen HUD dock & fridge popover buttons
  dockEl?.querySelectorAll("[data-kitchen-act]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const act = btn.getAttribute("data-kitchen-act");
      if (act === "fridge") toggleFridge();
      else if (act === "espresso") startMorningEspresso();
      else if (act === "steak") startHerbSteakPrep();
      else if (act === "champagne") startChampagneChefStage();
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
    // Smooth French double-door hinge swing (±96°) + interior LED ramp
    fridgeOpenAmount = THREE.MathUtils.lerp(fridgeOpenAmount, fridgeOpenTarget, Math.min(1, dt * 6.5));
    const swingRad = fridgeOpenAmount * 1.68;
    if (fridgeLeftDoorPivot) fridgeLeftDoorPivot.rotation.y = swingRad;
    if (fridgeRightDoorPivot) fridgeRightDoorPivot.rotation.y = -swingRad;
    fridgeInteriorLight.intensity = 0.35 + fridgeOpenAmount * 2.35;
    kitchenPendantLight.intensity = chefStageOn ? 2.45 : duskMode ? 1.85 : 1.35;

    // Bruce Morning Zoomies multi-waypoint runner
    if (zoomiesQueue.length > 0 && !bruce.isWalking?.()) {
      const [nx, nz] = zoomiesQueue.shift();
      bruce.walkTo(nx, nz, { speedScale: 1.78 });
      if (zoomiesQueue.length === 0) {
        later(() => {
          bruce.playAction("play_bow");
          highlightTrickBtn?.("play_bow");
        }, 700);
      }
    }

    // Morning Espresso pour stream
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

    // Herb snip & steak marination glide
    if (steakAnim) {
      steakAnim.t += dt;
      const p = Math.min(1, steakAnim.t / 1.45);
      const ease = p * p * (3 - 2 * p);
      rosemarySprigMesh.position.set(
        THREE.MathUtils.lerp(-14.3, -10.52, ease),
        1.01 + Math.sin(ease * Math.PI) * 0.42,
        THREE.MathUtils.lerp(-9.1, -10.30, ease),
      );
      rosemarySprigMesh.rotation.y = ease * Math.PI * 1.5;
      if (steakAnim.t >= 1.2 && !steakAnim.doneWalk) {
        steakAnim.doneWalk = true;
        walkBruceTo(-9.25, -13.1, { silent: true });
        later(() => bruce.playAction("lick_paw"), 750);
      }
      if (steakAnim.t >= steakAnim.dur) {
        steakAnim = null;
      }
    }

    // Champagne bottle lift & arc pour
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
          -10.55 + lift * 0.18,
          1.08 + lift * 0.26,
          -12.10 + lift * 0.02,
        );
        kitchenWineBottlePivot.rotation.z = -1.12 * lift;
      }
      const pouring = t >= 0.55 && t <= 1.75;
      champagneStreamMesh.visible = pouring;
      if (pouring && !champagneAnim.poured) {
        champagneAnim.poured = true;
        sfx.playGlassPour();
      }
      if (decanterWineMesh && pouring) {
        decanterWineMesh.position.y = cl((t - 0.55) / 1.2) * 0.024;
      }
      if (t >= champagneAnim.dur) {
        champagneAnim = null;
        champagneStreamMesh.visible = false;
        if (kitchenWineBottlePivot) {
          kitchenWineBottlePivot.position.set(-10.55, 1.08, -12.10);
          kitchenWineBottlePivot.rotation.set(0, 0, 0);
        }
      }
    }

    // Teppanyaki subtle steam particles when Chef Stage active
    steamPoints.visible = chefStageOn;
    if (chefStageOn) {
      steamMat.opacity = 0.28 + Math.sin(elapsed * 2.1) * 0.08;
      const arr = steamGeo.attributes.position.array;
      for (let i = 0; i < steamCount; i++) {
        arr[i * 3 + 1] += dt * 0.34;
        if (arr[i * 3 + 1] > 1.72) arr[i * 3 + 1] = 0.96 + (i % 4) * 0.03;
      }
      steamGeo.attributes.position.needsUpdate = true;
    }
  }

  function dispose() {
    document.body.classList.remove("is-kitchen-floor");
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
    handleRaycastHit,
    getInteractiveMeshes: () => [
      ...fridgeDoorMeshes,
      ...espressoMeshes,
      ...steakHerbMeshes,
      ...champagneChefMeshes,
    ],
    getState: () => ({
      fridgeOpen: fridgeOpenTarget > 0.5,
      fridgeOpenAmount: +fridgeOpenAmount.toFixed(2),
      chefStageOn,
    }),
    update,
    dispose,
  };
}
