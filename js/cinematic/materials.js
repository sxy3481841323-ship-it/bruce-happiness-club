import * as THREE from 'three';
import { random } from './math.js';

function canvasTexture(size, draw, repeat = 1, color = false) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  draw(canvas.getContext('2d'), size);
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(repeat, repeat);
  if (color) texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;
  return texture;
}

export function createMaterials() {
  const rng = random(28);
  const furBump = canvasTexture(
    256,
    (c, n) => {
      c.fillStyle = '#888';
      c.fillRect(0, 0, n, n);
      c.lineWidth = 0.65;
      for (let i = 0; i < 1700; i++) {
        const x = rng() * n,
          y = rng() * n,
          l = 5 + rng() * 25;
        c.strokeStyle = `rgba(${rng() > 0.5 ? '245,240,224' : '20,15,10'},${0.14 + rng() * 0.28})`;
        c.beginPath();
        c.moveTo(x, y);
        c.bezierCurveTo(x - 2, y + l * 0.25, x + 4, y + l * 0.7, x + 1, y + l);
        c.stroke();
      }
    },
    3,
  );
  const furColor = canvasTexture(
    256,
    (c, n) => {
      c.fillStyle = '#e9d6b2';
      c.fillRect(0, 0, n, n);
      for (let i = 0; i < 4000; i++) {
        const x = rng() * n,
          y = rng() * n,
          l = 8 + rng() * 23;
        c.strokeStyle = rng() > 0.55 ? 'rgba(255,249,221,.19)' : 'rgba(106,72,36,.10)';
        c.lineWidth = 0.5 + rng() * 0.5;
        c.beginPath();
        c.moveTo(x, y);
        c.bezierCurveTo(x + 3, y + l * 0.25, x - 3, y + l * 0.7, x, y + l);
        c.stroke();
      }
    },
    3,
    true,
  );
  const twill = canvasTexture(
    256,
    (c, n) => {
      c.fillStyle = '#621b2b';
      c.fillRect(0, 0, n, n);
      for (let i = -n; i < n * 2; i += 6) {
        c.strokeStyle = i % 12 === 0 ? '#9a4b52' : '#471524';
        c.lineWidth = 1.5;
        c.beginPath();
        c.moveTo(i, 0);
        c.lineTo(i + n, n);
        c.stroke();
      }
      for (let i = 0; i < 3500; i++) {
        c.fillStyle = `rgba(243,212,195,${rng() * 0.12})`;
        c.fillRect(rng() * n, rng() * n, 1, 2);
      }
    },
    2,
    true,
  );
  const wood = canvasTexture(
    512,
    (c, n) => {
      c.fillStyle = '#b58c60';
      c.fillRect(0, 0, n, n);
      for (let j = 0; j < 8; j++) {
        c.fillStyle = `rgba(${j % 2 ? '255,229,184' : '70,37,13'},${0.05 + rng() * 0.09})`;
        c.fillRect(j * 64, 0, 64, n);
        for (let i = 0; i < 105; i++) {
          const x = j * 64 + rng() * 64;
          c.strokeStyle = `rgba(67,40,16,${rng() * 0.12})`;
          c.lineWidth = 0.3 + rng() * 0.8;
          c.beginPath();
          c.moveTo(x, 0);
          c.bezierCurveTo(x + 5, 140, x - 6, 320, x + 2, n);
          c.stroke();
        }
        c.fillStyle = '#836645';
        c.fillRect(j * 64, 0, 0.8, n);
        c.fillRect(j * 64, j % 2 ? n * 0.72 : n * 0.25, 64, 0.65);
      }
    },
    3,
    true,
  );
  const fabric = canvasTexture(
    128,
    (c, n) => {
      c.fillStyle = '#999';
      c.fillRect(0, 0, n, n);
      for (let i = 0; i < n; i += 3) {
        c.fillStyle = '#777';
        c.fillRect(i, 0, 1, n);
        c.fillStyle = '#bbb';
        c.fillRect(0, i, n, 1);
      }
    },
    6,
  );
  const standard = (color, extra = {}) =>
    new THREE.MeshStandardMaterial({ color, roughness: 0.78, ...extra });
  const fur = new THREE.MeshPhysicalMaterial({
    color: '#ddbc87',
    map: furColor,
    roughness: 0.84,
    bumpMap: furBump,
    bumpScale: 0.027,
    sheen: 0.8,
    sheenColor: new THREE.Color('#ffebc4'),
    sheenRoughness: 0.65,
  });
  const paleFur = fur.clone();
  paleFur.color.set('#f4dcad');
  const earFur = fur.clone();
  earFur.color.set('#cfa365');
  return {
    fur,
    paleFur,
    earFur,
    scarf: new THREE.MeshPhysicalMaterial({
      map: twill,
      bumpMap: twill,
      bumpScale: 0.007,
      color: '#e3b5b1',
      roughness: 0.48,
      sheen: 0.75,
      sheenColor: new THREE.Color('#ad5260'),
      side: THREE.DoubleSide,
    }),
    nose: new THREE.MeshPhysicalMaterial({
      color: '#171412',
      roughness: 0.21,
      clearcoat: 0.85,
      clearcoatRoughness: 0.13,
      bumpMap: furBump,
      bumpScale: 0.002,
    }),
    eye: new THREE.MeshPhysicalMaterial({
      color: '#231811',
      roughness: 0.12,
      clearcoat: 1,
      clearcoatRoughness: 0.04,
    }),
    iris: new THREE.MeshPhysicalMaterial({ color: '#6e4629', roughness: 0.18, clearcoat: 1 }),
    black: standard('#171817', { roughness: 0.37 }),
    white: standard('#f7eee0'),
    glint: new THREE.MeshBasicMaterial({ color: '#fff8eb' }),
    brass: standard('#b28a4c', { metalness: 0.82, roughness: 0.3 }),
    wood: standard('#eddbbd', { map: wood, bumpMap: wood, bumpScale: 0.009, roughness: 0.57 }),
    walnut: standard('#4d3127', { map: wood, roughness: 0.46 }),
    plaster: standard('#ded4c2'),
    stone: standard('#b7b2a4'),
    linen: standard('#dfd1ac', { bumpMap: fabric, bumpScale: 0.017 }),
    moss: standard('#42564b', { bumpMap: fabric, bumpScale: 0.012 }),
    blanket: standard('#98604f', { bumpMap: fabric, bumpScale: 0.014 }),
    leaf: standard('#4c6543', { side: THREE.DoubleSide }),
    glass: new THREE.MeshPhysicalMaterial({
      color: '#bed7d5',
      roughness: 0.09,
      transparent: true,
      opacity: 0.16,
      metalness: 0.12,
      side: THREE.DoubleSide,
      depthWrite: false,
    }),
    ceramic: new THREE.MeshPhysicalMaterial({ color: '#efead9', roughness: 0.2, clearcoat: 0.5 }),
    water: new THREE.MeshPhysicalMaterial({ color: '#688c88', roughness: 0.25, metalness: 0.48 }),
    green: standard('#9ba447'),
    red: standard('#9e4336'),
    glow: new THREE.MeshBasicMaterial({ color: '#ffd19a', transparent: true, opacity: 0.85 }),
  };
}

export function textTexture(
  text,
  { color = '#f3ead7', background = '#203b31', width = 512, height = 128, fontSize = 66 } = {},
) {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const c = canvas.getContext('2d');
  c.fillStyle = background;
  c.fillRect(0, 0, width, height);
  c.fillStyle = color;
  c.font = `500 ${fontSize}px system-ui, sans-serif`;
  c.textAlign = 'center';
  c.textBaseline = 'middle';
  c.fillText(text, width / 2, height / 2, width * 0.92);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;
  return texture;
}
