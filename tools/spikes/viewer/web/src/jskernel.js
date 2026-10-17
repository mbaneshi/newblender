// Plain-JS twin of kernel/src/lib.rs, for an apples-to-apples comparison. Same algorithm, typed arrays, Map keyed by a numeric edge id.
export function grid(n) {
  const side = n + 1;
  const pos = new Float32Array(side * side * 3);
  let k = 0;
  for (let j = 0; j < side; j++) for (let i = 0; i < side; i++) {
    const x = (i / n) * 2 - 1, y = (j / n) * 2 - 1;
    pos[k++] = x; pos[k++] = y; pos[k++] = 0.1 * Math.sin(x * 6) * Math.cos(y * 6);
  }
  const idx = new Uint32Array(n * n * 6);
  k = 0;
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    const a = j * side + i, b = a + 1, c = a + side, d = a + side + 1;
    idx[k++] = a; idx[k++] = b; idx[k++] = d; idx[k++] = a; idx[k++] = d; idx[k++] = c;
  }
  return { pos, idx, nrm: null };
}

export function subdivide(m) {
  const nv = m.pos.length / 3;
  const maxNew = m.idx.length; // upper bound: 3 midpoints per tri
  let pos = new Float32Array((nv + maxNew) * 3);
  pos.set(m.pos);
  let count = nv;
  const mid = new Map();
  const idx = new Uint32Array(m.idx.length * 4);
  const midpoint = (a, b) => {
    const lo = a < b ? a : b, hi = a < b ? b : a;
    const key = lo * 4294967296 + hi;
    let v = mid.get(key);
    if (v === undefined) {
      v = count++;
      const pa = a * 3, pb = b * 3, pv = v * 3;
      pos[pv] = (pos[pa] + pos[pb]) * 0.5; pos[pv + 1] = (pos[pa + 1] + pos[pb + 1]) * 0.5; pos[pv + 2] = (pos[pa + 2] + pos[pb + 2]) * 0.5;
      mid.set(key, v);
    }
    return v;
  };
  let k = 0;
  for (let t = 0; t < m.idx.length; t += 3) {
    const a = m.idx[t], b = m.idx[t + 1], c = m.idx[t + 2];
    const ab = midpoint(a, b), bc = midpoint(b, c), ca = midpoint(c, a);
    idx[k++] = a; idx[k++] = ab; idx[k++] = ca; idx[k++] = ab; idx[k++] = b; idx[k++] = bc;
    idx[k++] = ca; idx[k++] = bc; idx[k++] = c; idx[k++] = ab; idx[k++] = bc; idx[k++] = ca;
  }
  return { pos: pos.slice(0, count * 3), idx, nrm: null };
}

export function computeNormals(m) {
  const n = new Float32Array(m.pos.length), p = m.pos;
  for (let t = 0; t < m.idx.length; t += 3) {
    const a = m.idx[t] * 3, b = m.idx[t + 1] * 3, c = m.idx[t + 2] * 3;
    const e1x = p[b] - p[a], e1y = p[b + 1] - p[a + 1], e1z = p[b + 2] - p[a + 2];
    const e2x = p[c] - p[a], e2y = p[c + 1] - p[a + 1], e2z = p[c + 2] - p[a + 2];
    const fx = e1y * e2z - e1z * e2y, fy = e1z * e2x - e1x * e2z, fz = e1x * e2y - e1y * e2x;
    for (const v of [a, b, c]) { n[v] += fx; n[v + 1] += fy; n[v + 2] += fz; }
  }
  for (let i = 0; i < n.length; i += 3) {
    const l = Math.max(Math.hypot(n[i], n[i + 1], n[i + 2]), 1e-20);
    n[i] /= l; n[i + 1] /= l; n[i + 2] /= l;
  }
  m.nrm = n;
}

export function checksum(pos, idx) {
  let s = 0;
  for (let i = 0; i < pos.length; i += 7) s += pos[i] * ((i % 13) + 1);
  for (let i = 0; i < idx.length; i += 11) s += idx[i] * ((i % 5) + 1) * 1e-3;
  return s;
}
