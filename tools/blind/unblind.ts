// Unblind a locked session and summarise.   bun tools/blind/unblind.ts <session-id>
// Writes results.md in the session directory and prints it.
import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { session, type Source } from "./lib";

const id = process.argv[2];
const s = session(id);
const key = s.key();  // throws unless locked
const scores = s.scores();
const rows = s.items().map((b, i) => ({ n: i + 1, b, ...key[b], ...scores[b] }));
const mean = (src: Source) => {
  const q = rows.filter((r) => r.source === src).map((r) => r.quality);
  return q.length ? (q.reduce((a, c) => a + c, 0) / q.length).toFixed(2) : "-";
};
const correct = rows.filter((r) => r.guess === r.source).length;
const fooled = rows.filter((r) => r.source === "agent" && r.guess === "studio").length;
const md = `# Blind scoring results — session \`${id}\`

| | Agent | Studio |
|---|---|---|
| Items | ${rows.filter((r) => r.source === "agent").length} | ${rows.filter((r) => r.source === "studio").length} |
| Mean production quality (1-5) | **${mean("agent")}** | **${mean("studio")}** |

- **Source guesses correct:** ${correct} of ${rows.length} (${Math.round((100 * correct) / rows.length)}%). Near 50% would mean agent work is indistinguishable.
- **Agent items taken for real production:** ${fooled}

| # | Source | Label | Quality | Guess | Note |
|---|---|---|---|---|---|
${rows.map((r) => `| ${r.n} | ${r.source} | ${r.label} | ${r.quality} | ${r.guess}${r.guess === r.source ? "" : " ✗"} | ${r.note ?? ""} |`).join("\n")}
`;
writeFileSync(join(s.dir, "results.md"), md);
console.log(md);
