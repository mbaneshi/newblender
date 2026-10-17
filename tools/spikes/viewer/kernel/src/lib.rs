//! Probe P04 kernel: just enough geometry to measure a Rust kernel behind a web viewer.
//! The same code runs natively (examples/bench.rs) and as WASM (wasm-bindgen `Kernel`).

use std::collections::HashMap;
use std::hash::{BuildHasherDefault, Hasher};
use wasm_bindgen::prelude::*;

pub mod edit;
pub use edit::{pick_brute, Accel, Dirty};

/// Small multiplicative hasher (FxHash-like); the default SipHash would unfairly slow the Rust side.
#[derive(Default)]
pub struct Fx(u64);
impl Hasher for Fx {
    fn finish(&self) -> u64 {
        self.0
    }
    fn write(&mut self, bytes: &[u8]) {
        for b in bytes {
            self.0 = (self.0.rotate_left(5) ^ *b as u64).wrapping_mul(0x517c_c1b7_2722_0a95);
        }
    }
    fn write_u64(&mut self, v: u64) {
        self.0 = (self.0.rotate_left(5) ^ v).wrapping_mul(0x517c_c1b7_2722_0a95);
    }
}

#[derive(Clone, Default)]
pub struct Mesh {
    pub pos: Vec<f32>,
    pub idx: Vec<u32>,
    pub nrm: Vec<f32>,
}

impl Mesh {
    pub fn tri_count(&self) -> usize {
        self.idx.len() / 3
    }

    /// (n+1)^2 vertices on the unit square, 2 n^2 triangles, a gentle wave in z.
    pub fn grid(n: u32) -> Mesh {
        let side = n + 1;
        let mut pos = Vec::with_capacity((side * side * 3) as usize);
        for j in 0..side {
            for i in 0..side {
                let x = i as f32 / n as f32 * 2.0 - 1.0;
                let y = j as f32 / n as f32 * 2.0 - 1.0;
                pos.extend_from_slice(&[x, y, 0.1 * (x * 6.0).sin() * (y * 6.0).cos()]);
            }
        }
        let mut idx = Vec::with_capacity((n * n * 6) as usize);
        for j in 0..n {
            for i in 0..n {
                let a = j * side + i;
                let (b, c, d) = (a + 1, a + side, a + side + 1);
                idx.extend_from_slice(&[a, b, d, a, d, c]);
            }
        }
        Mesh { pos, idx, nrm: Vec::new() }
    }

    /// Midpoint subdivision: every triangle becomes four; shared edges share their midpoint vertex.
    pub fn subdivide(&self) -> Mesh {
        let mut pos = self.pos.clone();
        let mut mid: HashMap<u64, u32, BuildHasherDefault<Fx>> =
            HashMap::with_capacity_and_hasher(self.idx.len(), Default::default());
        let mut idx = Vec::with_capacity(self.idx.len() * 4);
        let mut midpoint = |a: u32, b: u32, pos: &mut Vec<f32>| -> u32 {
            let key = if a < b { ((a as u64) << 32) | b as u64 } else { ((b as u64) << 32) | a as u64 };
            *mid.entry(key).or_insert_with(|| {
                let (pa, pb) = (a as usize * 3, b as usize * 3);
                let n = (pos.len() / 3) as u32;
                let p = [(pos[pa] + pos[pb]) * 0.5, (pos[pa + 1] + pos[pb + 1]) * 0.5, (pos[pa + 2] + pos[pb + 2]) * 0.5];
                pos.extend_from_slice(&p);
                n
            })
        };
        for t in self.idx.chunks_exact(3) {
            let (a, b, c) = (t[0], t[1], t[2]);
            let ab = midpoint(a, b, &mut pos);
            let bc = midpoint(b, c, &mut pos);
            let ca = midpoint(c, a, &mut pos);
            idx.extend_from_slice(&[a, ab, ca, ab, b, bc, ca, bc, c, ab, bc, ca]);
        }
        Mesh { pos, idx, nrm: Vec::new() }
    }

    /// Area-weighted vertex normals.
    pub fn compute_normals(&mut self) {
        let mut n = vec![0.0f32; self.pos.len()];
        for t in self.idx.chunks_exact(3) {
            let (a, b, c) = (t[0] as usize * 3, t[1] as usize * 3, t[2] as usize * 3);
            let e1 = [self.pos[b] - self.pos[a], self.pos[b + 1] - self.pos[a + 1], self.pos[b + 2] - self.pos[a + 2]];
            let e2 = [self.pos[c] - self.pos[a], self.pos[c + 1] - self.pos[a + 1], self.pos[c + 2] - self.pos[a + 2]];
            let f = [e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]];
            for &v in &[a, b, c] {
                n[v] += f[0];
                n[v + 1] += f[1];
                n[v + 2] += f[2];
            }
        }
        for v in n.chunks_exact_mut(3) {
            let l = (v[0] * v[0] + v[1] * v[1] + v[2] * v[2]).sqrt().max(1e-20);
            v[0] /= l;
            v[1] /= l;
            v[2] /= l;
        }
        self.nrm = n;
    }

    /// Cheap order-sensitive fingerprint for cross-implementation agreement checks.
    pub fn checksum(&self) -> f64 {
        let mut s = 0.0f64;
        for (i, v) in self.pos.iter().enumerate().step_by(7) {
            s += *v as f64 * ((i % 13) as f64 + 1.0);
        }
        for (i, v) in self.idx.iter().enumerate().step_by(11) {
            s += (*v as f64) * ((i % 5) as f64 + 1.0) * 1e-3;
        }
        s
    }
}

#[wasm_bindgen]
pub struct Kernel {
    mesh: Mesh,
    acc: Option<Accel>,
    dirty: (u32, u32, u32),
}

#[wasm_bindgen]
impl Kernel {
    #[wasm_bindgen(constructor)]
    pub fn new(n: u32) -> Kernel {
        Kernel { mesh: Mesh::grid(n), acc: None, dirty: (0, 0, 0) }
    }
    pub fn subdivide(&mut self) {
        self.mesh = self.mesh.subdivide();
    }
    pub fn compute_normals(&mut self) {
        self.mesh.compute_normals();
    }
    pub fn tri_count(&self) -> u32 {
        self.mesh.tri_count() as u32
    }
    pub fn vert_count(&self) -> u32 {
        (self.mesh.pos.len() / 3) as u32
    }
    pub fn checksum(&self) -> f64 {
        self.mesh.checksum()
    }
    /// Build adjacency + BVH (needed before pick/sculpt/refit).
    pub fn build_accel(&mut self) {
        self.acc = Some(Accel::new(&self.mesh));
    }
    /// Closest triangle hit by the ray, or -1. Writes the distance to `hit_t()`.
    pub fn pick(&mut self, ox: f32, oy: f32, oz: f32, dx: f32, dy: f32, dz: f32) -> i32 {
        let r = self.acc.as_ref().unwrap().pick(&self.mesh, [ox, oy, oz], [dx, dy, dz]);
        self.dirty.2 = r.map_or(0, |h| h.1.to_bits());
        r.map_or(-1, |h| h.0 as i32)
    }
    pub fn pick_brute(&mut self, ox: f32, oy: f32, oz: f32, dx: f32, dy: f32, dz: f32) -> i32 {
        pick_brute(&self.mesh, [ox, oy, oz], [dx, dy, dz]).map_or(-1, |h| h.0 as i32)
    }
    pub fn hit_t(&self) -> f32 {
        f32::from_bits(self.dirty.2)
    }
    /// Brush stroke; returns the number of vertices whose normal was repaired. See dirty_lo/dirty_hi.
    pub fn sculpt(&mut self, cx: f32, cy: f32, cz: f32, radius: f32, amount: f32) -> u32 {
        let acc = self.acc.as_mut().unwrap();
        let d = self.mesh.sculpt(acc, [cx, cy, cz], radius, amount);
        self.dirty = (d.lo, d.hi, self.dirty.2);
        d.touched as u32
    }
    pub fn refit(&mut self) {
        self.acc.as_mut().unwrap().refit(&self.mesh);
    }
    pub fn refit_local(&mut self) {
        self.acc.as_mut().unwrap().refit_local(&self.mesh);
    }
    pub fn dirty_lo(&self) -> u32 {
        self.dirty.0
    }
    pub fn dirty_hi(&self) -> u32 {
        self.dirty.1
    }
    /// Pointers into WASM linear memory, for zero-copy typed-array views on the JS side.
    /// A view is invalidated when memory grows (any allocating call), so re-create it after each op.
    pub fn pos_ptr(&self) -> *const f32 {
        self.mesh.pos.as_ptr()
    }
    pub fn pos_len(&self) -> usize {
        self.mesh.pos.len()
    }
    pub fn idx_ptr(&self) -> *const u32 {
        self.mesh.idx.as_ptr()
    }
    pub fn idx_len(&self) -> usize {
        self.mesh.idx.len()
    }
    pub fn nrm_ptr(&self) -> *const f32 {
        self.mesh.nrm.as_ptr()
    }
    pub fn nrm_len(&self) -> usize {
        self.mesh.nrm.len()
    }
}
