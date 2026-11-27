import * as THREE from "three";

/**
 * Animated Sunset Ocean Shader + Wheeling 3D Coastal Seagulls for the Penthouse Terrace.
 */
export function createTerraceVista(scene) {
  const disposables = [];
  const gulls = [];
  const sailboats = [];
  let oceanMat = null;

  const gullBodyGeo = new THREE.ConeGeometry(0.11, 0.56, 8);
  gullBodyGeo.rotateX(Math.PI * 0.5);
  const gullWingInnerGeo = new THREE.BoxGeometry(0.56, 0.025, 0.22);
  gullWingInnerGeo.translate(0.28, 0, 0);
  const gullWingOuterGeo = new THREE.BoxGeometry(0.46, 0.02, 0.16);
  gullWingOuterGeo.translate(0.23, 0, 0);

  const gullWhiteMat = new THREE.MeshStandardMaterial({
    color: 0xf7f2ea,
    roughness: 0.65,
    metalness: 0.05,
  });
  const gullTipMat = new THREE.MeshStandardMaterial({
    color: 0x5d6775,
    roughness: 0.72,
    metalness: 0.04,
  });
  disposables.push(gullBodyGeo, gullWingInnerGeo, gullWingOuterGeo, gullWhiteMat, gullTipMat);

  const gullConfigs = [
    { cx: -4.0, cz: -42.0, rx: 14.0, rz: 7.5, y: 4.8, speed: 0.34, phase: 0.0, scale: 1.0 },
    { cx: 5.5, cz: -52.0, rx: 18.0, rz: 9.0, y: 6.4, speed: 0.28, phase: 1.9, scale: 0.92 },
    { cx: -12.0, cz: -62.0, rx: 16.0, rz: 8.0, y: 7.8, speed: 0.25, phase: 3.4, scale: 1.1 },
    { cx: 9.0, cz: -38.0, rx: 10.5, rz: 5.5, y: 3.3, speed: 0.40, phase: 4.7, scale: 0.85 },
    { cx: 0.5, cz: -46.0, rx: 13.0, rz: 6.5, y: 5.5, speed: 0.31, phase: 2.6, scale: 0.95 },
  ];

  const gullRoot = new THREE.Group();
  gullRoot.name = "CoastalSeagullsGroup";

  gullConfigs.forEach((cfg) => {
    const root = new THREE.Group();
    root.scale.setScalar(cfg.scale);

    const body = new THREE.Mesh(gullBodyGeo, gullWhiteMat);
    root.add(body);

    const buildWing = (dir) => {
      const innerPivot = new THREE.Group();
      const innerMesh = new THREE.Mesh(gullWingInnerGeo, gullWhiteMat);
      if (dir < 0) innerMesh.scale.x = -1;
      innerPivot.add(innerMesh);

      const outerPivot = new THREE.Group();
      outerPivot.position.set(dir * 0.54, 0, 0.02);
      const outerMesh = new THREE.Mesh(gullWingOuterGeo, gullTipMat);
      if (dir < 0) outerMesh.scale.x = -1;
      outerPivot.add(outerMesh);
      innerPivot.add(outerPivot);
      root.add(innerPivot);
      return { innerPivot, outerPivot, dir };
    };

    const leftWing = buildWing(-1);
    const rightWing = buildWing(1);
    gullRoot.add(root);
    gulls.push({ cfg, root, leftWing, rightWing });
  });
  scene.add(gullRoot);

  oceanMat = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
      uSunDir: { value: new THREE.Vector3(-0.08, 0.16, -0.98).normalize() },
      uDeepColor: { value: new THREE.Color(0x183454) },
      uShallowColor: { value: new THREE.Color(0x28567c) },
      uSunGlow: { value: new THREE.Color(0xffbe76) },
      uSkyHorizon: { value: new THREE.Color(0xe6a979) },
      uMoodDim: { value: 1.0 },
    },
    vertexShader: `
      uniform float uTime;
      varying vec3 vWorldPos;
      void main() {
        vec4 wp = modelMatrix * vec4(position, 1.0);
        float w1 = sin(wp.x * 0.19 + uTime * 1.15) * cos(wp.z * 0.24 - uTime * 0.9);
        float w2 = sin(wp.x * 0.43 - wp.z * 0.31 + uTime * 1.7) * 0.45;
        wp.y += (w1 + w2) * 0.22;
        vWorldPos = wp.xyz;
        gl_Position = projectionMatrix * viewMatrix * wp;
      }
    `,
    fragmentShader: `
      uniform float uTime;
      uniform vec3 uSunDir;
      uniform vec3 uDeepColor;
      uniform vec3 uShallowColor;
      uniform vec3 uSunGlow;
      uniform vec3 uSkyHorizon;
      uniform float uMoodDim;
      varying vec3 vWorldPos;

      void main() {
        vec3 dx = vec3(0.0);
        float nx = cos(vWorldPos.x * 0.55 + uTime * 1.45) * 0.12 +
                   cos(vWorldPos.x * 1.25 - vWorldPos.z * 0.7 + uTime * 2.1) * 0.08;
        float nz = sin(vWorldPos.z * 0.62 - uTime * 1.25) * 0.14 +
                   sin(vWorldPos.z * 1.4 + uTime * 1.9) * 0.09;
        vec3 N = normalize(vec3(nx, 1.0, nz));
        vec3 V = normalize(cameraPosition - vWorldPos);
        float fresnel = pow(1.0 - max(dot(N, V), 0.0), 4.0);

        vec3 baseWater = mix(uDeepColor, uShallowColor, clamp(0.45 + 0.55 * sin(vWorldPos.z * 0.05), 0.0, 1.0));
        vec3 col = mix(baseWater, uSkyHorizon * 0.78, fresnel * 0.72);

        // Shimmering sunset glitter reflection track
        vec3 H = normalize(uSunDir + V);
        float specBroad = pow(max(dot(N, H), 0.0), 26.0);
        float specSharp = pow(max(dot(N, H), 0.0), 190.0);
        col += uSunGlow * (specBroad * 0.55 + specSharp * 1.65) * uMoodDim;

        // Aerial distance haze blending softly into horizon
        float dist = clamp((abs(vWorldPos.z) - 42.0) / 115.0, 0.0, 1.0);
        col = mix(col, uSkyHorizon * (0.72 * uMoodDim + 0.18), pow(dist, 1.45));
        gl_FragColor = vec4(col, 1.0);
      }
    `,
  });
  disposables.push(oceanMat);

  return {
    attachRoomRoot(roomRoot) {
      if (!roomRoot) return;
      sailboats.length = 0;
      roomRoot.traverse((obj) => {
        if (!obj.isMesh) return;
        if (obj.name === "OceanVistaWater") {
          obj.material?.dispose?.();
          obj.material = oceanMat;
          obj.castShadow = false;
          obj.receiveShadow = false;
        }
        if (/^Sailboat/i.test(obj.name)) {
          sailboats.push({ mesh: obj, baseY: obj.position.y, phase: obj.position.x * 0.25 });
        }
      });
    },
    setMood({ sulking = false, dusk = false } = {}) {
      if (!oceanMat) return;
      if (sulking) {
        oceanMat.uniforms.uDeepColor.value.setHex(0x1f2d3c);
        oceanMat.uniforms.uShallowColor.value.setHex(0x2e4154);
        oceanMat.uniforms.uSkyHorizon.value.setHex(0x4a5c70);
        oceanMat.uniforms.uSunGlow.value.setHex(0x7c90a6);
        oceanMat.uniforms.uMoodDim.value = 0.28;
      } else if (dusk) {
        oceanMat.uniforms.uDeepColor.value.setHex(0x0f1f38);
        oceanMat.uniforms.uShallowColor.value.setHex(0x1e3958);
        oceanMat.uniforms.uSkyHorizon.value.setHex(0xb86d58);
        oceanMat.uniforms.uSunGlow.value.setHex(0xff9f59);
        oceanMat.uniforms.uMoodDim.value = 0.72;
      } else {
        oceanMat.uniforms.uDeepColor.value.setHex(0x183454);
        oceanMat.uniforms.uShallowColor.value.setHex(0x28567c);
        oceanMat.uniforms.uSkyHorizon.value.setHex(0xe6a979);
        oceanMat.uniforms.uSunGlow.value.setHex(0xffbe76);
        oceanMat.uniforms.uMoodDim.value = 1.0;
      }
      gullRoot.visible = !sulking;
    },
    update(dt, elapsed) {
      if (oceanMat) {
        oceanMat.uniforms.uTime.value = elapsed;
      }
      for (let i = 0; i < sailboats.length; i++) {
        const s = sailboats[i];
        s.mesh.position.y = s.baseY + Math.sin(elapsed * 1.1 + s.phase) * 0.14;
        s.mesh.rotation.z = Math.sin(elapsed * 0.9 + s.phase) * 0.035;
      }
      if (gullRoot.visible) {
        for (let i = 0; i < gulls.length; i++) {
          const { cfg, root, leftWing, rightWing } = gulls[i];
          const t = elapsed * cfg.speed + cfg.phase;
          const x = cfg.cx + Math.cos(t) * cfg.rx;
          const z = cfg.cz + Math.sin(t) * cfg.rz;
          const vx = -Math.sin(t) * cfg.rx * cfg.speed;
          const vz = Math.cos(t) * cfg.rz * cfg.speed;
          root.position.set(x, cfg.y + Math.sin(t * 2.0) * 0.45, z);
          root.rotation.y = Math.atan2(vx, vz);
          root.rotation.z = Math.sin(t) * 0.18;

          // Alternate thermal glide & gentle slow coastal wingbeats
          const flapCycle = Math.sin(elapsed * 2.2 + cfg.phase * 1.7);
          const glideWindow = Math.sin(elapsed * 0.55 + cfg.phase) > 0.25 ? 0.22 : 1.0;
          const innerAngle = 0.14 + flapCycle * 0.42 * glideWindow;
          const outerAngle = -0.18 - flapCycle * 0.28 * glideWindow;
          leftWing.innerPivot.rotation.z = -innerAngle;
          leftWing.outerPivot.rotation.z = -outerAngle;
          rightWing.innerPivot.rotation.z = innerAngle;
          rightWing.outerPivot.rotation.z = outerAngle;
        }
      }
    },
    dispose() {
      scene.remove(gullRoot);
      disposables.forEach((d) => d.dispose?.());
    },
  };
}
