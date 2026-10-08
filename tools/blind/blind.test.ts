import { expect, test, beforeAll } from "bun:test";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";

const root = mkdtempSync(join(tmpdir(), "blind-"));
process.env.BLIND_ROOT = root;
const { handle } = await import("./server");
const { session } = await import("./lib");

beforeAll(() => {
  const d = join(root, "test1");
  mkdirSync(join(d, "img"), { recursive: true });
  writeFileSync(join(d, "items.json"), JSON.stringify(["aa11", "bb22"]));
  writeFileSync(join(d, "key.json"), JSON.stringify({ aa11: { source: "agent", label: "SECRET-LABEL", origin: "x" }, bb22: { source: "studio", label: "y", origin: "z" } }));
  writeFileSync(join(d, "img", "aa11.png"), "png");
  writeFileSync(join(d, "img", "bb22.png"), "png");
});

const post = (path: string, body: unknown) => handle(new Request(`http://x${path}`, { method: "POST", body: JSON.stringify(body) }));

test("the page never contains the key", async () => {
  const html = await (await handle(new Request("http://x/?s=test1"))).text();
  expect(html).not.toContain("SECRET-LABEL");
  expect(html).not.toContain("\"source\"");  // no key fields; "studio" itself appears as a guess option
});

test("only listed images are served; key.json is not reachable", async () => {
  expect((await handle(new Request("http://x/img/test1/aa11.png"))).status).toBe(200);
  expect((await handle(new Request("http://x/img/test1/key.json"))).status).toBe(404);
  expect((await handle(new Request("http://x/img/test1/..%2Fkey.json"))).status).toBe(404);
});

test("the key cannot be read before locking; lock needs every item scored", async () => {
  expect(() => session("test1").key()).toThrow();
  expect((await post("/api/score", { s: "test1", b: "aa11", quality: 3, guess: "agent" })).status).toBe(200);
  expect((await post("/api/lock", { s: "test1" })).status).toBe(400);
  expect((await post("/api/score", { s: "test1", b: "bb22", quality: 9, guess: "agent" })).status).toBe(400);
  expect((await post("/api/score", { s: "test1", b: "bb22", quality: 5, guess: "studio" })).status).toBe(200);
  expect((await post("/api/lock", { s: "test1" })).status).toBe(200);
});

test("after locking, scores are read-only and the key opens", async () => {
  expect((await post("/api/score", { s: "test1", b: "aa11", quality: 5, guess: "studio" })).status).toBe(400);
  expect(session("test1").key().aa11.source).toBe("agent");
  expect(session("test1").scores().aa11.quality).toBe(3);
});
