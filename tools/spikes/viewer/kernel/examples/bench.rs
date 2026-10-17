//! Native baseline: `cargo run --release --example bench` prints JSON lines.
use p04_kernel::Mesh;
use std::time::Instant;

fn main() {
    for n in [224u32, 447, 894] {
        let g = Mesh::grid(n);
        let t = Instant::now();
        let mut s = g.subdivide();
        let sub_ms = t.elapsed().as_secs_f64() * 1000.0;
        let t = Instant::now();
        s.compute_normals();
        let nrm_ms = t.elapsed().as_secs_f64() * 1000.0;
        println!(
            "{{\"impl\":\"native\",\"grid_n\":{n},\"in_tris\":{},\"out_tris\":{},\"subdivide_ms\":{sub_ms:.2},\"normals_ms\":{nrm_ms:.2},\"checksum\":{:.6}}}",
            g.tri_count(), s.tri_count(), s.checksum()
        );
    }
}
