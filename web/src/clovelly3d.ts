// Clovelly's seabed in 3D: the same 1 m LiDAR grid as the underwater map, as a surface you can turn and zoom, with
// a see-through sea at the tide on the chart. Heights are stretched (EXAGGERATE) so the reef reads at this scale.
// Loaded only when someone opens 3D: three.js is about 150 KB gzipped.

import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

const NONE = -32768;
const EXAGGERATE = 2.5; // under water: the reef's ledges and holes
const LAND_TOP = 3; // m: land is flattened to this, so the cliffs and car park don't wall in the inlet
const FILL_PASSES = 60; // gaps (white water, the buildings the survey left out) filled in from their neighbours, so the photo covers it all
const y = (m: number) => (m < 0 ? m * EXAGGERATE : Math.min(m, LAND_TOP));

export interface Seabed {
  w: number;
  h: number;
  cell: number;
  z: Int16Array; // cm above AHD, NONE = no reading
}

// Colour by height above or below mean sea level: deep blue through to sand at the waterline, then rock
const STOPS: [number, [number, number, number]][] = [
  [-8, [18, 45, 95]],
  [-5, [30, 80, 140]],
  [-3, [50, 125, 165]],
  [-1.5, [95, 165, 170]],
  [-0.3, [185, 190, 150]],
  [0.3, [170, 160, 130]], // the waterline: sand and wet rock
  [1.2, [92, 90, 82]],
  [3, [62, 64, 62]], // land, dark, so the water's the thing you look at
];
function colourAt(m: number): [number, number, number] {
  if (m <= STOPS[0][0]) return STOPS[0][1];
  for (let i = 1; i < STOPS.length; i++) {
    const [h1, c1] = STOPS[i];
    if (m <= h1) {
      const [h0, c0] = STOPS[i - 1];
      const f = (m - h0) / (h1 - h0);
      return [0, 1, 2].map((k) => c0[k] + (c1[k] - c0[k]) * f) as [number, number, number];
    }
  }
  return STOPS[STOPS.length - 1][1];
}

export function seabed3d(container: HTMLElement, g: Seabed, photoUrl: string) {
  const W = g.w * g.cell;
  const H = g.h * g.cell;
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  container.append(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(getComputedStyle(container).getPropertyValue("--surface").trim() || "#1a2226");
  const camera = new THREE.PerspectiveCamera(40, 1, 1, 5000);
  camera.position.set(-55, 125, 205); // from the south-west, three-quarters up: the whole inlet, beach to mouth
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(25, -4, 25);
  controls.enableDamping = true;
  controls.maxPolarAngle = Math.PI * 0.47; // never under the seabed
  controls.minDistance = 40;
  controls.maxDistance = 900;
  controls.update();

  // Gaps, filled inwards from the readings around them
  const z = Float32Array.from(g.z, (v) => (v === NONE ? NaN : v / 100));
  for (let pass = 0; pass < FILL_PASSES; pass++) {
    const next = z.slice();
    for (let r = 0; r < g.h; r++)
      for (let c = 0; c < g.w; c++) {
        const i = r * g.w + c;
        if (!Number.isNaN(z[i])) continue;
        let sum = 0;
        let n = 0;
        for (const [dr, dc] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
          const rr = r + dr;
          const cc = c + dc;
          if (rr < 0 || cc < 0 || rr >= g.h || cc >= g.w) continue;
          const v = z[rr * g.w + cc];
          if (!Number.isNaN(v)) (sum += v), n++;
        }
        if (n >= 2) next[i] = sum / n;
      }
    z.set(next);
  }

  // The seabed: one vertex per cell, triangles only where all three corners have a height
  const pos = new Float32Array(g.w * g.h * 3);
  const col = new Float32Array(g.w * g.h * 3);
  const uv = new Float32Array(g.w * g.h * 2); // where each cell sits on the aerial photo: same box, same projection
  for (let r = 0; r < g.h; r++)
    for (let c = 0; c < g.w; c++) {
      const i = r * g.w + c;
      const m = Number.isNaN(z[i]) ? 0 : z[i];
      pos.set([c * g.cell - W / 2, y(m), r * g.cell - H / 2], i * 3); // row 0 is north: -z
      const rgb = colourAt(m);
      col.set([rgb[0] / 255, rgb[1] / 255, rgb[2] / 255], i * 3);
      uv.set([(c + 0.5) / g.w, 1 - (r + 0.5) / g.h], i * 2);
    }
  const index: number[] = [];
  const has = (i: number) => !Number.isNaN(z[i]);
  for (let r = 0; r < g.h - 1; r++)
    for (let c = 0; c < g.w - 1; c++) {
      const a = r * g.w + c;
      const b = a + 1;
      const d = a + g.w;
      const e = d + 1;
      if (has(a) && has(d) && has(b)) index.push(a, d, b);
      if (has(b) && has(d) && has(e)) index.push(b, d, e);
    }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  geo.setAttribute("color", new THREE.BufferAttribute(col, 3));
  geo.setAttribute("uv", new THREE.BufferAttribute(uv, 2));
  geo.setIndex(index);
  geo.computeVertexNormals();
  const groundMat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.95, metalness: 0, side: THREE.DoubleSide });
  scene.add(new THREE.Mesh(geo, groundMat));
  // The aerial photo draped over it, once it's loaded (the depth colours until then, or if it fails)
  const loader = new THREE.TextureLoader();
  loader.setCrossOrigin("anonymous");
  let photo: THREE.Texture | null = null;
  loader.load(photoUrl, (tex) => {
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = renderer.capabilities.getMaxAnisotropy();
    photo = tex;
    groundMat.map = tex;
    groundMat.vertexColors = false;
    groundMat.needsUpdate = true;
  });

  // The sea at the tide: see-through, so the reef shows under it
  const sea = new THREE.Mesh(
    new THREE.PlaneGeometry(W, H),
    new THREE.MeshStandardMaterial({ color: 0x2a8fc0, transparent: true, opacity: 0.35, roughness: 0.2, depthWrite: false }),
  );
  sea.rotation.x = -Math.PI / 2;
  scene.add(sea);

  scene.add(new THREE.HemisphereLight(0xdfefff, 0x404030, 1.3));
  const sun = new THREE.DirectionalLight(0xffffff, 1.6);
  sun.position.set(-200, 300, -150); // from the north-west, as on the map's relief shading
  scene.add(sun);

  const size = () => {
    const w = container.clientWidth;
    const h = Math.round(w * (w < 500 ? 0.85 : 0.68)); // a phone gets a taller box
    renderer.setSize(w, h);
    camera.aspect = w / h;
    // The same width of view at any size (56° across), so a narrow screen doesn't crop the inlet's ends
    camera.fov = (2 * Math.atan(Math.tan((56 * Math.PI) / 360) / camera.aspect) * 180) / Math.PI;
    camera.updateProjectionMatrix();
  };
  size();
  const ro = new ResizeObserver(size);
  ro.observe(container);
  renderer.setAnimationLoop(() => {
    controls.update();
    renderer.render(scene, camera);
  });

  return {
    setTide(m: number) {
      sea.position.y = y(m);
    },
    dispose() {
      renderer.setAnimationLoop(null);
      ro.disconnect();
      controls.dispose();
      geo.dispose();
      photo?.dispose();
      renderer.dispose();
      renderer.domElement.remove();
    },
  };
}
