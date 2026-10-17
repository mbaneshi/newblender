//! Native baseline for P05: `cargo run --release --example edit_bench` prints JSON lines.
use p04_kernel::{pick_brute, Accel, Mesh};
use std::time::Instant;

fn ms(t: Instant) -> f64 {
    t.elapsed().as_secs_f64() * 1000.0
}
fn med(mut v: Vec<f64>) -> f64 {
    v.sort_by(|a, b| a.partial_cmp(b).unwrap());
    v[v.len() / 2]
}

fn main() {
    for n in [447u32, 707, 1000] {
        let mut m = Mesh::grid(n);
        m.compute_normals();
        let t = Instant::now();
        let mut acc = Accel::new(&m);
        let build = ms(t);
        // deterministic rays from above, scattered over the sheet
        let rays: Vec<[f32; 3]> = (0..200).map(|i| { let a = i as f32 * 2.399; [(a.sin() * 0.9), (a.cos() * 0.9) * ((i % 7) as f32 / 7.0 + 0.2), 3.0] }).collect();
        let d = [0.0f32, 0.0, -1.0];
        let bvh: Vec<f64> = rays.iter().map(|r| { let t = Instant::now(); let h = acc.pick(&m, *r, d); std::hint::black_box(h); ms(t) }).collect();
        let brute: Vec<f64> = rays.iter().take(20).map(|r| { let t = Instant::now(); let h = pick_brute(&m, *r, d); std::hint::black_box(h); ms(t) }).collect();
        // agreement on every ray we brute-forced
        let agree = rays.iter().take(20).all(|r| match (acc.pick(&m, *r, d), pick_brute(&m, *r, d)) { (Some(a), Some(b)) => (a.1 - b.1).abs() < 1e-5, (None, None) => true, _ => false });
        let mut sc = Vec::new();
        let mut rf = Vec::new();
        let mut rf_full = Vec::new();
        let mut touched = 0;
        let mut span = 0;
        let mut moved_min = usize::MAX;
        for i in 0..20 {
            let (cx, cy) = (-0.5 + 0.05 * i as f32, 0.1f32);
            let c = [cx, cy, 0.1 * (cx * 6.0).sin() * (cy * 6.0).cos()]; // on the surface, so every stroke moves vertices
            let t = Instant::now();
            let dd = m.sculpt(&mut acc, c, 0.05, 0.02);
            sc.push(ms(t));
            touched = dd.touched;
            moved_min = moved_min.min(dd.moved);
            span = dd.hi - dd.lo + 1;
            let t = Instant::now();
            acc.refit_local(&m);
            rf.push(ms(t));
        }
        // Correctness after edits: rays through the stroked area must still agree with brute force.
        let edit_rays: Vec<[f32; 3]> = (0..20).map(|i| [-0.5 + 0.05 * i as f32 + 0.003, 0.1 + 0.002 * i as f32, 3.0]).collect();
        let agree_after = edit_rays.iter().all(|r| match (acc.pick(&m, *r, d), pick_brute(&m, *r, d)) { (Some(a), Some(b)) => (a.1 - b.1).abs() < 1e-5, (None, None) => true, _ => false });
        for _ in 0..5 {
            let t = Instant::now();
            acc.refit(&m);
            rf_full.push(ms(t));
        }
        let t = Instant::now();
        m.compute_normals();
        let full_nrm = ms(t);
        println!("{{\"impl\":\"native\",\"grid_n\":{n},\"tris\":{},\"build_accel_ms\":{build:.1},\"pick_bvh_ms\":{:.4},\"pick_brute_ms\":{:.2},\"pick_agree\":{agree},\"sculpt_ms\":{:.3},\"refit_local_ms\":{:.4},\"refit_full_ms\":{:.2},\"pick_agree_after_edit\":{agree_after},\"full_normals_ms\":{full_nrm:.2},\"touched_verts\":{touched},\"dirty_span_verts\":{span},\"min_moved_per_stroke\":{moved_min},\"total_verts\":{}}}",
            m.tri_count(), med(bvh), med(brute), med(sc), med(rf), med(rf_full), m.pos.len() / 3);
    }
}
