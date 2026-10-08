// Blind scoring (RFC 0001 R7). A session directory holds:
//   items.json   public: shuffled blind ids (no sources, no labels)
//   img/<id>.png normalised images (same width, metadata stripped, random names)
//   key.json     PRIVATE: blind id -> { source: "agent" | "studio", label, origin } (never served)
//   scores.json  owner's answers: blind id -> { quality: 1-5, guess: "agent" | "studio", note }
//   locked       present once the owner locks; scores are then read-only, unblinding allowed
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

export type Source = "agent" | "studio";
export type Score = { quality: number; guess: Source; note?: string };
export const ROOT = process.env.BLIND_ROOT ?? join(process.env.HOME!, "newblender-data/blind/sessions");

const read = <T>(p: string, fallback: T): T => (existsSync(p) ? JSON.parse(readFileSync(p, "utf8")) : fallback);

export function session(id: string) {
  if (!/^[a-z0-9-]{4,40}$/.test(id)) throw new Error("bad session id");
  const dir = join(ROOT, id);
  if (!existsSync(join(dir, "items.json"))) throw new Error("unknown session");
  return {
    dir,
    items: (): string[] => read(join(dir, "items.json"), []),
    scores: (): Record<string, Score> => read(join(dir, "scores.json"), {}),
    locked: () => existsSync(join(dir, "locked")),
    image: (bid: string) => {
      if (!read<string[]>(join(dir, "items.json"), []).includes(bid)) return null;
      return join(dir, "img", `${bid}.png`);
    },
    save(bid: string, s: Score) {
      if (existsSync(join(dir, "locked"))) throw new Error("session is locked");
      if (!read<string[]>(join(dir, "items.json"), []).includes(bid)) throw new Error("unknown item");
      if (!Number.isInteger(s.quality) || s.quality < 1 || s.quality > 5) throw new Error("quality must be 1-5");
      if (s.guess !== "agent" && s.guess !== "studio") throw new Error("guess must be agent or studio");
      const all = read<Record<string, Score>>(join(dir, "scores.json"), {});
      all[bid] = { quality: s.quality, guess: s.guess, note: String(s.note ?? "").slice(0, 500) };
      writeFileSync(join(dir, "scores.json"), JSON.stringify(all, null, 1));
    },
    lock() {
      const n = Object.keys(read(join(dir, "scores.json"), {})).length;
      if (n < read<string[]>(join(dir, "items.json"), []).length) throw new Error("score every item before locking");
      writeFileSync(join(dir, "locked"), new Date().toISOString());
    },
    key: (): Record<string, { source: Source; label: string; origin: string }> => {
      if (!existsSync(join(dir, "locked"))) throw new Error("refusing to read the key before the session is locked");
      return read(join(dir, "key.json"), {});
    },
  };
}
