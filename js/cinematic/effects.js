import * as THREE from 'three';
import { clamp, mesh, random } from './math.js';

export function createLighting(scene, renderer, config, mobile) {
  const environment = new THREE.Scene();
  const shell = new THREE.Mesh(
    new THREE.SphereGeometry(30, 24, 12),
    new THREE.MeshBasicMaterial({
      color: config.dusk ? '#54657c' : '#b1b9bb',
      side: THREE.BackSide,
    }),
  );
  environment.add(shell);
  for (const [position, size, color, intensity] of [
    [[-5, 7, -9], [9, 7], '#ffe3ac', 4],
    [[7, 5, 3], [7, 5], '#d9e7f4', 1.6],
    [[0, 13, 0], [8, 8], '#fff7e6', 2],
  ]) {
    const plane = new THREE.Mesh(
      new THREE.PlaneGeometry(...size),
      new THREE.MeshBasicMaterial({
        color: new THREE.Color(color).multiplyScalar(intensity),
        side: THREE.DoubleSide,
      }),
    );
    plane.position.fromArray(position);
    plane.lookAt(0, 0, 0);
    environment.add(plane);
  }
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envTarget = pmrem.fromScene(environment, 0.08, 0.1, 60, { size: mobile ? 128 : 256 });
  scene.environment = envTarget.texture;
  scene.environmentIntensity = 0.43;
  environment.traverse((o) => {
    o.dispose?.();
    o.geometry?.dispose();
    o.material?.dispose();
  });
  pmrem.dispose();
  const sky = config.dusk ? '#5b6c83' : config.rain ? '#8c9d9e' : '#bdc5b1';
  scene.background = new THREE.Color(sky);
  scene.fog = new THREE.FogExp2(sky, config.environment === 'street' ? 0.025 : 0.012);
  const ambient = new THREE.HemisphereLight(config.dusk ? '#94b6de' : '#e8edeb', '#7f6950', 0.65);
  scene.add(ambient);
  const sun = new THREE.DirectionalLight(
    config.dusk ? '#f3b97a' : '#ffe2ae',
    config.rain ? 1.3 : 2.6,
  );
  sun.position.set(-3, 6, -4);
  sun.castShadow = true;
  sun.shadow.mapSize.setScalar(mobile ? 1024 : 2048);
  sun.shadow.camera.left = -8;
  sun.shadow.camera.right = 8;
  sun.shadow.camera.top = 8;
  sun.shadow.camera.bottom = -8;
  sun.shadow.camera.near = 0.5;
  sun.shadow.camera.far = 25;
  sun.shadow.bias = -0.0003;
  sun.shadow.normalBias = 0.025;
  sun.shadow.radius = 4;
  scene.add(sun);
  const fill = new THREE.DirectionalLight('#f5e3c6', 0.95);
  fill.position.set(3, 3, 5);
  scene.add(fill);
  const rim = new THREE.DirectionalLight('#ffe7bd', 1.4);
  rim.position.set(1, 3, -3);
  scene.add(rim);
  // Painted radial occlusion grounds the paws even on lower quality shadow maps.
  const shadowCanvas = document.createElement('canvas');
  shadowCanvas.width = shadowCanvas.height = 128;
  const ctx = shadowCanvas.getContext('2d'),
    gradient = ctx.createRadialGradient(64, 64, 2, 64, 64, 64);
  gradient.addColorStop(0, 'rgba(24,18,11,.30)');
  gradient.addColorStop(0.45, 'rgba(24,18,11,.15)');
  gradient.addColorStop(1, 'rgba(24,18,11,0)');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 128, 128);
  const contact = mesh(
    new THREE.PlaneGeometry(1.5, 3.1),
    new THREE.MeshBasicMaterial({
      map: new THREE.CanvasTexture(shadowCanvas),
      transparent: true,
      depthWrite: false,
    }),
    scene,
    [0, 0.042, 0],
  );
  contact.rotation.x = -Math.PI / 2;
  contact.castShadow = contact.receiveShadow = false;
  return {
    sun,
    fill,
    rim,
    ambient,
    contact,
    envTarget,
    update(cold, warmth, bruce) {
      sun.color.set('#ffe0a9').lerp(new THREE.Color('#8fa9c9'), cold);
      sun.intensity = (config.rain ? 1.3 : 2.6) * (1 - cold * 0.65) + warmth * 0.6;
      fill.color.set('#f5e3c6').lerp(new THREE.Color('#88a4c2'), cold);
      rim.intensity = 1.4 + warmth * 1.7;
      contact.position.x = bruce.root.position.x;
      contact.position.z = bruce.root.position.z;
      contact.rotation.z = -bruce.root.rotation.y;
    },
    destroy() {
      scene.environment = null;
      envTarget.dispose();
    },
  };
}

const rainFragment = `
uniform float uTime; uniform float uAmount; varying vec2 vUv;
float hash(float n){return fract(sin(n*127.1)*43758.5453);}
void main(){
 vec2 uv=vUv; float drops=0.; float edge=0.;
 for(int layer=0;layer<2;layer++){
   float l=float(layer); vec2 st=uv*vec2(45.+l*29.,9.+l*7.);
   float id=floor(st.x); float seed=hash(id+93.*l); float y=fract(st.y+uTime*(.31+seed*.32)+seed*9.);
   float x=fract(st.x)-.5+sin(y*9.+seed*22.)*.06;
   float head=exp(-dot(vec2(x*15.,(y-.18)*25.),vec2(x*15.,(y-.18)*25.)));
   float trail=exp(-abs(x)*60.)*smoothstep(.9,.2,y)*smoothstep(.15,.30,y)*.36;
   drops+=head+trail; edge+=head*(x>0.?1.:-1.);
 }
 vec3 reflected=mix(vec3(.23,.40,.53),vec3(.97,.91,.70),clamp(.5+edge,0.,1.));
 gl_FragColor=vec4(reflected,clamp(drops*.53*uAmount,0.,.58));
}`;

export function createAtmosphere(scene, config, mobile) {
  const rng = random(71),
    count = mobile ? 180 : 360;
  const positions = new Float32Array(count * 3),
    seeds = new Float32Array(count),
    sizes = new Float32Array(count);
  for (let i = 0; i < count; i++) {
    positions.set([(rng() - 0.5) * 18, rng() * 7, (rng() - 0.5) * 17], i * 3);
    seeds[i] = rng();
    sizes[i] = 1 + rng() * 3;
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('aSeed', new THREE.BufferAttribute(seeds, 1));
  geometry.setAttribute('aSize', new THREE.BufferAttribute(sizes, 1));
  const uniforms = { uTime: { value: 0 }, uCold: { value: 0 }, uCelebrate: { value: 0 } };
  const material = new THREE.ShaderMaterial({
    uniforms,
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    vertexShader: `attribute float aSeed; attribute float aSize; uniform float uTime; uniform float uCold; uniform float uCelebrate; varying float vSeed;
    void main(){vSeed=aSeed; vec3 p=position; p.x+=sin(uTime*.17+aSeed*30.)*.5; p.z+=cos(uTime*.15+aSeed*20.)*.25;
    p.y=mod(position.y+uTime*(.035-uCold*2.5+uCelebrate*.12)+14.,7.); vec4 mv=modelViewMatrix*vec4(p,1.);
    gl_Position=projectionMatrix*mv; gl_PointSize=clamp(aSize*(12.+uCelebrate*16.)/(-mv.z),1.,12.);}`,
    fragmentShader: `uniform float uCold; uniform float uCelebrate; varying float vSeed;
    void main(){vec2 p=gl_PointCoord-.5; p.y*=1.+uCold*3.; float a=exp(-dot(p,p)*20.); if(a<.03)discard;
    vec3 c=mix(vec3(1.,.79,.44),vec3(.66,.78,.9),uCold); c=mix(c,vec3(1.,.68+vSeed*.2,.5+vSeed*.2),uCelebrate*.4); gl_FragColor=vec4(c,a*(.13+uCelebrate*.32));}`,
  });
  scene.add(new THREE.Points(geometry, material));
  const rainMat = new THREE.ShaderMaterial({
    uniforms: { uTime: { value: 0 }, uAmount: { value: config.rain ? 1 : 0 } },
    transparent: true,
    depthWrite: false,
    side: THREE.DoubleSide,
    vertexShader:
      'varying vec2 vUv; void main(){vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
    fragmentShader: rainFragment,
  });
  const windowRain = mesh(new THREE.PlaneGeometry(11, 5), rainMat, scene, [0, 2.6, -3.68]);
  windowRain.castShadow = false;
  if (config.environment !== 'home') windowRain.visible = false;
  const rays = new THREE.Group();
  scene.add(rays);
  const rayMat = new THREE.ShaderMaterial({
    transparent: true,
    depthWrite: false,
    side: THREE.DoubleSide,
    blending: THREE.AdditiveBlending,
    uniforms: { uOpacity: { value: config.rain ? 0.018 : 0.045 } },
    vertexShader:
      'varying vec2 vUv; void main(){vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
    fragmentShader:
      'varying vec2 vUv; uniform float uOpacity; void main(){float a=pow(sin(vUv.x*3.14159),2.)*sin(vUv.y*3.14159); gl_FragColor=vec4(1.,.82,.53,a*uOpacity);}',
  });
  for (let i = 0; i < 4; i++) {
    const ray = mesh(new THREE.PlaneGeometry(0.5 + i * 0.2, 8), rayMat, rays, [
      -3 + i * 1.5,
      2,
      -1.6,
    ]);
    ray.rotation.set(0.5, 0.3, -0.55);
    ray.castShadow = ray.receiveShadow = false;
  }
  // A bounded particle pool: interaction strokes never allocate meshes or textures.
  const trailCount = 96,
    trailPositions = new Float32Array(trailCount * 3),
    lives = new Float32Array(trailCount),
    wetFlags = new Float32Array(trailCount),
    velocities = new Float32Array(trailCount * 3);
  trailPositions.fill(-100);
  const trailGeo = new THREE.BufferGeometry();
  trailGeo.setAttribute('position', new THREE.BufferAttribute(trailPositions, 3));
  trailGeo.setAttribute('aLife', new THREE.BufferAttribute(lives, 1));
  trailGeo.setAttribute('aWet', new THREE.BufferAttribute(wetFlags, 1));
  const trailMat = new THREE.ShaderMaterial({
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    vertexShader:
      'attribute float aLife; attribute float aWet; varying float vLife; varying float vWet; void main(){vLife=aLife;vWet=aWet;vec4 p=modelViewMatrix*vec4(position,1.); gl_Position=projectionMatrix*p; gl_PointSize=clamp(aLife*50./(-p.z),0.,22.);}',
    fragmentShader:
      'varying float vLife;varying float vWet;void main(){vec2 p=gl_PointCoord-.5;p.x*=1.+vWet*.4;float d=length(p);vec3 c=mix(vec3(1.,.81,.46),vec3(.69,.84,.95),vWet);gl_FragColor=vec4(c,smoothstep(.5,0.,d)*vLife*.55);}',
  });
  const trails = new THREE.Points(trailGeo, trailMat);
  trails.frustumCulled = false;
  scene.add(trails);
  let cursor = 0;
  // Falling leaves are actual rotating, lit meshes, separate from luminous dust.
  const leafMat = new THREE.MeshStandardMaterial({
    color: '#aa8747',
    roughness: 0.8,
    side: THREE.DoubleSide,
  });
  const leafShape = new THREE.Shape();
  leafShape.moveTo(0, -0.1);
  leafShape.bezierCurveTo(-0.085, -0.035, -0.065, 0.075, 0, 0.13);
  leafShape.bezierCurveTo(0.065, 0.065, 0.07, -0.04, 0, -0.1);
  const leafGeo = new THREE.ShapeGeometry(leafShape, 8),
    leaves = new THREE.InstancedMesh(leafGeo, leafMat, 24),
    dummy = new THREE.Object3D();
  scene.add(leaves);
  const leafSeeds = Array.from({ length: 24 }, () => [
    rng() * 16 - 8,
    rng() * 7,
    rng() * 18 - 9,
    rng() * 8,
  ]);
  return {
    emit(point, amount = 3, wet = 0) {
      for (let i = 0; i < amount; i++) {
        const n = cursor++ % trailCount;
        lives[n] = 0.8 + rng() * 0.2;
        wetFlags[n] = wet;
        trailPositions.set(
          [point.x + (rng() - 0.5) * 0.12, point.y + rng() * 0.06, point.z + (rng() - 0.5) * 0.1],
          n * 3,
        );
        velocities.set(
          [
            (rng() - 0.5) * (0.04 + wet * 1.2),
            0.14 + wet * rng() * 0.8,
            (rng() - 0.5) * (0.04 + wet * 1.2),
          ],
          n * 3,
        );
      }
      trailGeo.attributes.aWet.needsUpdate = true;
    },
    update(time, dt, cold, celebration) {
      uniforms.uTime.value = time;
      uniforms.uCold.value = cold;
      uniforms.uCelebrate.value = celebration;
      rainMat.uniforms.uTime.value = time;
      rainMat.uniforms.uAmount.value = Math.max(config.rain ? 1 : 0, cold);
      rayMat.uniforms.uOpacity.value = (config.rain ? 0.018 : 0.045) * (1 - cold);
      for (let i = 0; i < trailCount; i++) {
        lives[i] = Math.max(0, lives[i] - dt * (0.7 + wetFlags[i] * 0.7));
        if (lives[i] > 0) {
          velocities[i * 3 + 1] -= wetFlags[i] * dt * 2;
          for (let j = 0; j < 3; j++) trailPositions[i * 3 + j] += velocities[i * 3 + j] * dt;
        }
      }
      trailGeo.attributes.position.needsUpdate = true;
      trailGeo.attributes.aLife.needsUpdate = true;
      leaves.visible = config.environment === 'street' || celebration > 0.1;
      leafMat.color.set(celebration > 0.1 ? '#e5bcaa' : '#aa8747');
      for (let i = 0; i < leafSeeds.length; i++) {
        const s = leafSeeds[i];
        dummy.position.set(
          s[0] + Math.sin(time * 0.4 + s[3]) * 0.8,
          (s[1] - time * (0.1 + celebration * 0.1) + 100) % 7,
          s[2],
        );
        dummy.rotation.set(time * 0.5 + s[3], s[3], Math.sin(time + i));
        dummy.scale.setScalar(celebration > 0.1 ? 0.65 : 1);
        dummy.updateMatrix();
        leaves.setMatrixAt(i, dummy.matrix);
      }
      leaves.instanceMatrix.needsUpdate = true;
    },
  };
}

export function createPostProcess(renderer, width, height) {
  const target = new THREE.WebGLRenderTarget(width, height, {
    depthBuffer: true,
    type: THREE.HalfFloatType,
  });
  target.depthTexture = new THREE.DepthTexture(width, height, THREE.UnsignedIntType);
  const scene = new THREE.Scene(),
    camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  const uniforms = {
    tColor: { value: target.texture },
    tDepth: { value: target.depthTexture },
    uResolution: { value: new THREE.Vector2(width, height) },
    uCold: { value: 0 },
    uWarm: { value: 0 },
    uTime: { value: 0 },
    uFocus: { value: 5 },
    uFade: { value: 1 },
    uFlash: { value: 0 },
    uReduced: { value: 0 },
  };
  const material = new THREE.ShaderMaterial({
    uniforms,
    depthTest: false,
    depthWrite: false,
    vertexShader: 'varying vec2 vUv; void main(){vUv=uv; gl_Position=vec4(position.xy,0.,1.);}',
    fragmentShader: `
      uniform sampler2D tColor; uniform sampler2D tDepth; uniform vec2 uResolution; uniform float uCold,uWarm,uTime,uFocus,uFade,uFlash,uReduced; varying vec2 vUv;
      float viewDepth(float z){return .1*100./(100.-z*(100.-.1));}
      float hash(vec2 p){return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453);}
      void main(){
        vec2 uv=vUv;
        vec2 rainCell=uv*vec2(67.,8.); float rainId=floor(rainCell.x); float rainSeed=hash(vec2(rainId,1.));
        float rainY=fract(rainCell.y+uTime*(.4+rainSeed*.4)+rainSeed*5.);
        float rainX=fract(rainCell.x)-.5+sin(rainY*9.+rainSeed*12.)*.04;
        float droplet=exp(-dot(vec2(rainX*20.,(rainY-.2)*25.),vec2(rainX*20.,(rainY-.2)*25.)));
        float streak=exp(-abs(rainX)*70.)*smoothstep(.9,.25,rainY)*smoothstep(.17,.3,rainY)*.3;
        uv.x+=uCold*rainX*droplet*.012;
        float depth=viewDepth(texture2D(tDepth,uv).r);
        float blur=clamp(abs(depth-uFocus)/max(depth,.1)*1.3,0.,1.)*.7+uCold*.5;
        vec2 pixel=1./uResolution; vec3 c=texture2D(tColor,uv).rgb*.36;
        for(int i=0;i<8;i++){float a=float(i)*.785398; vec2 d=vec2(cos(a),sin(a))*pixel*(1.8+uCold*3.)*blur; c+=texture2D(tColor,uv+d).rgb*.08;}
        float lum=dot(c,vec3(.2126,.7152,.0722)); c=mix(c,vec3(lum)*vec3(.79,.90,1.09),uCold*.68);
        c+=vec3(.09,.14,.17)*(droplet+streak)*uCold*.45;
        c*=mix(vec3(1.045,1.01,.945),vec3(1.10,1.035,.92),uWarm*.6);
        float vignette=1.-smoothstep(.22,.85,length((uv-.5)*vec2(1.,.9)))*.28; c*=vignette;
        c+=(hash(gl_FragCoord.xy+floor(uTime*24.))-.5)*.012*(1.-uReduced);
        c=mix(vec3(.015,.022,.025),c,uFade); c+=vec3(1.,.82,.49)*uFlash;
        gl_FragColor=vec4(c,1.);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
  });
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), material);
  scene.add(quad);
  return {
    uniforms,
    resize(w, h) {
      target.setSize(w, h);
      uniforms.uResolution.value.set(w, h);
    },
    render(world, worldCamera) {
      renderer.setRenderTarget(target);
      renderer.render(world, worldCamera);
      renderer.setRenderTarget(null);
      renderer.render(scene, camera);
    },
    destroy() {
      target.dispose();
      target.depthTexture.dispose();
      quad.dispose();
      quad.geometry.dispose();
      material.dispose();
    },
  };
}
