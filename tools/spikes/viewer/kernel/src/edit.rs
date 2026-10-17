//! P05: the editing half of the viewer question. Vertex->triangle adjacency, a BVH for picking,
//! a brush sculpt that touches only nearby vertices, and local normal repair.
//! Everything here is deliberately plain: no SIMD, no threads, so the numbers are a floor, not a ceiling.

use crate::Mesh;

#[derive(Clone, Copy)]
struct Node {
    min: [f32; 3],
    max: [f32; 3],
    /// Leaf: first index into `order`. Internal: left child (right child is left + 1).
    a: u32,
    /// Leaf: triangle count (> 0). Internal: 0.
    n: u32,
}

const LEAF: usize = 4;

pub struct Accel {
    nodes: Vec<Node>,
    order: Vec<u32>,
    vt_start: Vec<u32>,
    vt_list: Vec<u32>,
    stamp: Vec<u32>,
    tstamp: Vec<u32>,
    epoch: u32,
    parent: Vec<u32>,
    leaf_of: Vec<u32>,
    last_tris: Vec<u32>,
}

fn tri_pts(m: &Mesh, t: usize) -> [[f32; 3]; 3] {
    let g = |v: u32| {
        let i = v as usize * 3;
        [m.pos[i], m.pos[i + 1], m.pos[i + 2]]
    };
    [g(m.idx[t * 3]), g(m.idx[t * 3 + 1]), g(m.idx[t * 3 + 2])]
}

fn tri_bounds(m: &Mesh, t: usize) -> ([f32; 3], [f32; 3]) {
    let p = tri_pts(m, t);
    let mut lo = p[0];
    let mut hi = p[0];
    for q in &p[1..] {
        for k in 0..3 {
            lo[k] = lo[k].min(q[k]);
            hi[k] = hi[k].max(q[k]);
        }
    }
    (lo, hi)
}

/// Moeller-Trumbore. Returns the hit distance along the ray, or None.
fn ray_tri(o: [f32; 3], d: [f32; 3], p: &[[f32; 3]; 3]) -> Option<f32> {
    let sub = |a: [f32; 3], b: [f32; 3]| [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
    let cross = |a: [f32; 3], b: [f32; 3]| [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
    let dot = |a: [f32; 3], b: [f32; 3]| a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    let e1 = sub(p[1], p[0]);
    let e2 = sub(p[2], p[0]);
    let h = cross(d, e2);
    let det = dot(e1, h);
    if det.abs() < 1e-12 {
        return None;
    }
    let inv = 1.0 / det;
    let s = sub(o, p[0]);
    let u = dot(s, h) * inv;
    if !(0.0..=1.0).contains(&u) {
        return None;
    }
    let q = cross(s, e1);
    let v = dot(d, q) * inv;
    if v < 0.0 || u + v > 1.0 {
        return None;
    }
    let t = dot(e2, q) * inv;
    if t > 1e-6 {
        Some(t)
    } else {
        None
    }
}

/// Slab test; returns whether the ray enters the box before `tmax`.
fn ray_box(o: [f32; 3], inv: [f32; 3], lo: [f32; 3], hi: [f32; 3], tmax: f32) -> bool {
    let mut t0 = 0.0f32;
    let mut t1 = tmax;
    for k in 0..3 {
        // A ray parallel to this slab (inv is infinite) never crosses it; 0 * inf would be NaN when the origin sits exactly on a bound.
        if inv[k].is_infinite() {
            if o[k] < lo[k] || o[k] > hi[k] {
                return false;
            }
            continue;
        }
        let a = (lo[k] - o[k]) * inv[k];
        let b = (hi[k] - o[k]) * inv[k];
        let (near, far) = if a < b { (a, b) } else { (b, a) };
        t0 = t0.max(near);
        t1 = t1.min(far);
        if t0 > t1 {
            return false;
        }
    }
    true
}

impl Accel {
    /// Builds adjacency and BVH. Returns the structure; callers time the two halves separately via `build_adjacency`/`build_bvh`.
    pub fn new(m: &Mesh) -> Accel {
        let mut a = Accel { nodes: Vec::new(), order: Vec::new(), vt_start: Vec::new(), vt_list: Vec::new(), stamp: vec![0; m.pos.len() / 3], tstamp: vec![0; m.tri_count()], epoch: 0, parent: Vec::new(), leaf_of: Vec::new(), last_tris: Vec::new() };
        a.build_adjacency(m);
        a.build_bvh(m);
        a
    }

    pub fn build_adjacency(&mut self, m: &Mesh) {
        let nv = m.pos.len() / 3;
        let mut count = vec![0u32; nv + 1];
        for &v in &m.idx {
            count[v as usize + 1] += 1;
        }
        for i in 0..nv {
            count[i + 1] += count[i];
        }
        let mut fill = count.clone();
        let mut list = vec![0u32; m.idx.len()];
        for t in 0..m.tri_count() {
            for k in 0..3 {
                let v = m.idx[t * 3 + k] as usize;
                list[fill[v] as usize] = t as u32;
                fill[v] += 1;
            }
        }
        self.vt_start = count;
        self.vt_list = list;
    }

    pub fn build_bvh(&mut self, m: &Mesh) {
        let nt = m.tri_count();
        let cent: Vec<[f32; 3]> = (0..nt)
            .map(|t| {
                let (lo, hi) = tri_bounds(m, t);
                [(lo[0] + hi[0]) * 0.5, (lo[1] + hi[1]) * 0.5, (lo[2] + hi[2]) * 0.5]
            })
            .collect();
        self.order = (0..nt as u32).collect();
        self.nodes.clear();
        self.nodes.push(Node { min: [0.0; 3], max: [0.0; 3], a: 0, n: 0 });
        // Explicit stack of (node, lo, hi) so deep meshes cannot overflow the call stack.
        let mut stack = vec![(0usize, 0usize, nt)];
        while let Some((ni, lo, hi)) = stack.pop() {
            let mut bmin = [f32::MAX; 3];
            let mut bmax = [f32::MIN; 3];
            let mut cmin = [f32::MAX; 3];
            let mut cmax = [f32::MIN; 3];
            for &t in &self.order[lo..hi] {
                let (a, b) = tri_bounds(m, t as usize);
                let c = cent[t as usize];
                for k in 0..3 {
                    bmin[k] = bmin[k].min(a[k]);
                    bmax[k] = bmax[k].max(b[k]);
                    cmin[k] = cmin[k].min(c[k]);
                    cmax[k] = cmax[k].max(c[k]);
                }
            }
            self.nodes[ni].min = bmin;
            self.nodes[ni].max = bmax;
            if hi - lo <= LEAF {
                self.nodes[ni].a = lo as u32;
                self.nodes[ni].n = (hi - lo) as u32;
                continue;
            }
            let ext = [cmax[0] - cmin[0], cmax[1] - cmin[1], cmax[2] - cmin[2]];
            let axis = if ext[0] >= ext[1] && ext[0] >= ext[2] { 0 } else if ext[1] >= ext[2] { 1 } else { 2 };
            let mid = (lo + hi) / 2;
            self.order[lo..hi].select_nth_unstable_by(mid - lo, |&x, &y| cent[x as usize][axis].partial_cmp(&cent[y as usize][axis]).unwrap());
            let left = self.nodes.len();
            self.nodes.push(Node { min: [0.0; 3], max: [0.0; 3], a: 0, n: 0 });
            self.nodes.push(Node { min: [0.0; 3], max: [0.0; 3], a: 0, n: 0 });
            self.nodes[ni].a = left as u32;
            self.nodes[ni].n = 0;
            stack.push((left, lo, mid));
            stack.push((left + 1, mid, hi));
        }
        self.parent = vec![0; self.nodes.len()];
        self.leaf_of = vec![0; nt];
        for i in 0..self.nodes.len() {
            let n = self.nodes[i];
            if n.n > 0 {
                for &t in &self.order[n.a as usize..(n.a + n.n) as usize] {
                    self.leaf_of[t as usize] = i as u32;
                }
            } else {
                self.parent[n.a as usize] = i as u32;
                self.parent[n.a as usize + 1] = i as u32;
            }
        }
    }

    fn recompute(&mut self, m: &Mesh, i: usize) {
        let n = self.nodes[i];
        let (mut lo, mut hi);
        if n.n > 0 {
            lo = [f32::MAX; 3];
            hi = [f32::MIN; 3];
            for &t in &self.order[n.a as usize..(n.a + n.n) as usize] {
                let (a, b) = tri_bounds(m, t as usize);
                for k in 0..3 {
                    lo[k] = lo[k].min(a[k]);
                    hi[k] = hi[k].max(b[k]);
                }
            }
        } else {
            let (l, r) = (self.nodes[n.a as usize], self.nodes[n.a as usize + 1]);
            lo = [l.min[0].min(r.min[0]), l.min[1].min(r.min[1]), l.min[2].min(r.min[2])];
            hi = [l.max[0].max(r.max[0]), l.max[1].max(r.max[1]), l.max[2].max(r.max[2])];
        }
        self.nodes[i].min = lo;
        self.nodes[i].max = hi;
    }

    /// Refit only the leaves of triangles changed by the last sculpt, and their ancestors.
    /// Stops climbing as soon as a node's bounds come out unchanged.
    pub fn refit_local(&mut self, m: &Mesh) {
        let tris = std::mem::take(&mut self.last_tris);
        let mut seen = std::collections::HashSet::new();
        for &t in &tris {
            let mut i = self.leaf_of[t as usize] as usize;
            if !seen.insert(i) {
                continue;
            }
            loop {
                let before = (self.nodes[i].min, self.nodes[i].max);
                self.recompute(m, i);
                if i == 0 || before == (self.nodes[i].min, self.nodes[i].max) {
                    break;
                }
                i = self.parent[i] as usize;
            }
        }
        self.last_tris = tris;
    }

    /// Bottom-up bounds update after vertices moved. Children always have larger indices than parents.
    pub fn refit(&mut self, m: &Mesh) {
        for i in (0..self.nodes.len()).rev() {
            let n = self.nodes[i];
            let (mut lo, mut hi);
            if n.n > 0 {
                lo = [f32::MAX; 3];
                hi = [f32::MIN; 3];
                for &t in &self.order[n.a as usize..(n.a + n.n) as usize] {
                    let (a, b) = tri_bounds(m, t as usize);
                    for k in 0..3 {
                        lo[k] = lo[k].min(a[k]);
                        hi[k] = hi[k].max(b[k]);
                    }
                }
            } else {
                let (l, r) = (self.nodes[n.a as usize], self.nodes[n.a as usize + 1]);
                lo = [l.min[0].min(r.min[0]), l.min[1].min(r.min[1]), l.min[2].min(r.min[2])];
                hi = [l.max[0].max(r.max[0]), l.max[1].max(r.max[1]), l.max[2].max(r.max[2])];
            }
            self.nodes[i].min = lo;
            self.nodes[i].max = hi;
        }
    }

    /// Closest hit as (triangle, distance).
    pub fn pick(&self, m: &Mesh, o: [f32; 3], d: [f32; 3]) -> Option<(u32, f32)> {
        let inv = [1.0 / d[0], 1.0 / d[1], 1.0 / d[2]];
        let mut best: Option<(u32, f32)> = None;
        let mut tmax = f32::MAX;
        let mut stack = [0u32; 64];
        let mut sp = 1;
        while sp > 0 {
            sp -= 1;
            let n = self.nodes[stack[sp] as usize];
            if !ray_box(o, inv, n.min, n.max, tmax) {
                continue;
            }
            if n.n > 0 {
                for &t in &self.order[n.a as usize..(n.a + n.n) as usize] {
                    if let Some(h) = ray_tri(o, d, &tri_pts(m, t as usize)) {
                        if h < tmax {
                            tmax = h;
                            best = Some((t, h));
                        }
                    }
                }
            } else {
                stack[sp] = n.a;
                stack[sp + 1] = n.a + 1;
                sp += 2;
            }
        }
        best
    }
}

/// Reference answer with no acceleration structure; also the stand-in for "three.js Raycaster on a plain mesh".
pub fn pick_brute(m: &Mesh, o: [f32; 3], d: [f32; 3]) -> Option<(u32, f32)> {
    let mut best: Option<(u32, f32)> = None;
    for t in 0..m.tri_count() {
        if let Some(h) = ray_tri(o, d, &tri_pts(m, t)) {
            if best.map_or(true, |b| h < b.1) {
                best = Some((t as u32, h));
            }
        }
    }
    best
}

/// Result of one brush stroke, so the caller knows what to re-upload.
pub struct Dirty {
    pub moved: usize,
    pub touched: usize,
    pub lo: u32,
    pub hi: u32,
}

impl Mesh {
    /// Raise vertices within `radius` of `c` along +z by `amount` with a smooth falloff, then repair
    /// normals only where a triangle changed. Needs the BVH to find vertices without scanning all of them.
    pub fn sculpt(&mut self, acc: &mut Accel, c: [f32; 3], radius: f32, amount: f32) -> Dirty {
        acc.epoch += 1;
        let ep = acc.epoch;
        let mut moved: Vec<u32> = Vec::new();
        let mut stack = vec![0u32];
        while let Some(ni) = stack.pop() {
            let n = acc.nodes[ni as usize];
            let mut d2 = 0.0f32;
            for k in 0..3 {
                let e = (n.min[k] - c[k]).max(0.0).max(c[k] - n.max[k]);
                d2 += e * e;
            }
            if d2 > radius * radius {
                continue;
            }
            if n.n > 0 {
                for &t in &acc.order[n.a as usize..(n.a + n.n) as usize] {
                    for k in 0..3 {
                        let v = self.idx[t as usize * 3 + k];
                        if acc.stamp[v as usize] == ep {
                            continue;
                        }
                        acc.stamp[v as usize] = ep;
                        let i = v as usize * 3;
                        let (dx, dy, dz) = (self.pos[i] - c[0], self.pos[i + 1] - c[1], self.pos[i + 2] - c[2]);
                        let r2 = dx * dx + dy * dy + dz * dz;
                        if r2 < radius * radius {
                            let f = 1.0 - r2 / (radius * radius);
                            self.pos[i + 2] += amount * f * f;
                            moved.push(v);
                        }
                    }
                }
            } else {
                stack.push(n.a);
                stack.push(n.a + 1);
            }
        }
        // Triangles whose shape changed, then every vertex of those triangles needs a fresh normal.
        let mut tris: Vec<u32> = Vec::new();
        for &v in &moved {
            for &t in &acc.vt_list[acc.vt_start[v as usize] as usize..acc.vt_start[v as usize + 1] as usize] {
                if acc.tstamp[t as usize] != ep {
                    acc.tstamp[t as usize] = ep;
                    tris.push(t);
                }
            }
        }
        acc.last_tris = tris.clone();
        let mut verts: Vec<u32> = Vec::new();
        for &t in &tris {
            for k in 0..3 {
                let v = self.idx[t as usize * 3 + k];
                if acc.stamp[v as usize] != ep + 0x4000_0000 {
                    acc.stamp[v as usize] = ep + 0x4000_0000;
                    verts.push(v);
                }
            }
        }
        for &v in &verts {
            let mut s = [0.0f32; 3];
            for &t in &acc.vt_list[acc.vt_start[v as usize] as usize..acc.vt_start[v as usize + 1] as usize] {
                let p = tri_pts(self, t as usize);
                let e1 = [p[1][0] - p[0][0], p[1][1] - p[0][1], p[1][2] - p[0][2]];
                let e2 = [p[2][0] - p[0][0], p[2][1] - p[0][1], p[2][2] - p[0][2]];
                s[0] += e1[1] * e2[2] - e1[2] * e2[1];
                s[1] += e1[2] * e2[0] - e1[0] * e2[2];
                s[2] += e1[0] * e2[1] - e1[1] * e2[0];
            }
            let l = (s[0] * s[0] + s[1] * s[1] + s[2] * s[2]).sqrt().max(1e-20);
            let i = v as usize * 3;
            self.nrm[i] = s[0] / l;
            self.nrm[i + 1] = s[1] / l;
            self.nrm[i + 2] = s[2] / l;
        }
        let lo = verts.iter().copied().min().unwrap_or(0);
        let hi = verts.iter().copied().max().unwrap_or(0);
        Dirty { moved: moved.len(), touched: verts.len(), lo, hi }
    }
}
