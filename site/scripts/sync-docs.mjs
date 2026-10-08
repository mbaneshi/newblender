// Publish the repo's docs/ as site pages. The repo notes are the single source of truth;
// the generated pages are gitignored. Relative links are rewritten: links to published
// notes become site links, anything else (tools, YAML cards, folders) points at GitHub.
import { readdir, readFile, writeFile, mkdir, rm } from "node:fs/promises";
import { join, dirname, relative, posix } from "node:path";

const REPO_ROOT = new URL("../../", import.meta.url).pathname;
const DOCS = join(REPO_ROOT, "docs");
const OUT = new URL("../src/content/docs/", import.meta.url).pathname;
const REPO = "https://github.com/mbaneshi/newblender";
const BASE = "/newblender";
const SECTIONS = ["rfc", "discovery", "showcase", "demos"];

async function walk(dir) {
  const out = [];
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) out.push(...(await walk(p)));
    else if (e.name.endsWith(".md") && !e.name.startsWith("_")) out.push(p);
  }
  return out;
}

// docs/demos/002-flow/report.md -> demos/002-flow ; docs/rfc/0001-x.md -> rfc/0001-x
const slugOf = (repoPath) =>
  relative("docs", repoPath).replace(/\/report\.md$/, "").replace(/\.md$/, "").toLowerCase();

const sidebarLabel = (title) =>
  title
    .replace(/: how an agent could make it$/, "")
    .replace(/ — (check )?report$/, "")
    .replace(/ \([^)]*\)$/, "")
    .replace(/^(RFC \d+) — ([^:]+):.*$/, "$1 — $2");

const files = (await Promise.all(SECTIONS.map((s) => walk(join(DOCS, s)).catch(() => [])))).flat();
const published = new Set(files.map((f) => relative(REPO_ROOT, f)));

function rewrite(body, repoPath) {
  return body.replace(/\]\((?!https?:|#|mailto:)([^)\s]+)\)/g, (m, target) => {
    const [path, hash = ""] = target.split("#");
    const resolved = posix.normalize(posix.join(posix.dirname(repoPath), path)).replace(/\/$/, "");
    const anchor = hash ? `#${hash}` : "";
    if (published.has(resolved)) return `](${BASE}/${slugOf(resolved)}/${anchor})`;
    const kind = /\.[a-z0-9]+$/i.test(resolved) ? "blob" : "tree";
    return `](${REPO}/${kind}/dev/${resolved}${anchor})`;
  });
}

for (const s of SECTIONS) await rm(join(OUT, s), { recursive: true, force: true });

for (const file of files) {
  const repoPath = relative(REPO_ROOT, file);
  const raw = await readFile(file, "utf8");
  const title = raw.match(/^#\s+(.+)$/m)?.[1].trim() ?? slugOf(repoPath);
  const body = rewrite(raw.replace(/^#\s+.+\n+/m, ""), repoPath);
  const page = [
    "---",
    `title: ${JSON.stringify(title)}`,
    `sidebar:`,
    `  label: ${JSON.stringify(sidebarLabel(title))}`,
    `editUrl: ${JSON.stringify(`${REPO}/edit/dev/${repoPath}`)}`,
    "---",
    "",
    `:::note`,
    `Generated from [\`${repoPath}\`](${REPO}/blob/dev/${repoPath}).`,
    `:::`,
    "",
    body,
  ].join("\n");
  const out = join(OUT, `${slugOf(repoPath)}.md`);
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, page);
}
console.log(`[sync-docs] ${files.length} pages → src/content/docs/{${SECTIONS.join(",")}}/`);
