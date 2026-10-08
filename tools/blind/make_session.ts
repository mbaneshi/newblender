// Create a blind session from a manifest.
//   bun tools/blind/make_session.ts <session-id> <manifest.json> [width]
// manifest: [{ "path": "...png|jpg|webp", "source": "agent"|"studio", "label": "...", "origin": "..." }]
// Every image is re-encoded to PNG at the same width with metadata stripped, and named by a random id.
import { mkdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { randomBytes } from "node:crypto";
import { ROOT } from "./lib";

const [id, manifestPath, widthArg] = process.argv.slice(2);
if (!id || !manifestPath) throw new Error("usage: make_session.ts <session-id> <manifest.json> [width]");
const width = Number(widthArg ?? 540);
const items: { path: string; source: "agent" | "studio"; label: string; origin: string }[] = JSON.parse(readFileSync(manifestPath, "utf8"));
const dir = join(ROOT, id);
if (existsSync(dir)) throw new Error(`session ${id} already exists`);
mkdirSync(join(dir, "img"), { recursive: true });

const key: Record<string, unknown> = {};
const ids: string[] = [];
for (const it of items) {
  const bid = randomBytes(4).toString("hex");
  const p = Bun.spawnSync(["ffmpeg", "-y", "-loglevel", "error", "-i", it.path, "-vf", `scale=${width}:-2`,
    "-map_metadata", "-1", join(dir, "img", `${bid}.png`)]);
  if (p.exitCode !== 0) throw new Error(`ffmpeg failed on ${it.path}: ${p.stderr}`);
  key[bid] = { source: it.source, label: it.label, origin: it.origin };
  ids.push(bid);
}
for (let i = ids.length - 1; i > 0; i--) {  // Fisher-Yates with crypto randomness
  const j = randomBytes(4).readUInt32BE() % (i + 1);
  [ids[i], ids[j]] = [ids[j], ids[i]];
}
writeFileSync(join(dir, "key.json"), JSON.stringify(key, null, 1));
writeFileSync(join(dir, "items.json"), JSON.stringify(ids));
console.log(`session ${id}: ${ids.length} items in ${dir}`);
