// Local blind scoring page.  bun tools/blind/server.ts   ->  http://127.0.0.1:7795/?s=<session-id>
// Serves only shuffled blind ids and their normalised images. The key is never read here.
import { session } from "./lib";

const esc = (s: string) => s.replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);

export function handle(req: Request): Response | Promise<Response> {
  const url = new URL(req.url);
  try {
    if (url.pathname === "/" && req.method === "GET") {
      const s = session(url.searchParams.get("s") ?? "");
      return new Response(page(url.searchParams.get("s")!, s.items(), s.scores(), s.locked()),
        { headers: { "content-type": "text/html; charset=utf-8" } });
    }
    if (url.pathname.startsWith("/img/") && req.method === "GET") {
      const [, , sid, file] = url.pathname.split("/");
      const path = session(sid).image(file.replace(/\.png$/, ""));
      return path ? new Response(Bun.file(path), { headers: { "cache-control": "no-store" } }) : new Response("Not Found", { status: 404 });
    }
    if (url.pathname === "/api/score" && req.method === "POST") {
      return req.json().then((b: any) => {
        session(String(b.s)).save(String(b.b), { quality: Number(b.quality), guess: b.guess, note: b.note });
        return Response.json({ ok: true });
      }).catch((e) => Response.json({ error: e.message }, { status: 400 }));
    }
    if (url.pathname === "/api/lock" && req.method === "POST") {
      return req.json().then((b: any) => {
        session(String(b.s)).lock();
        return Response.json({ ok: true });
      }).catch((e) => Response.json({ error: e.message }, { status: 400 }));
    }
  } catch (e) {
    return Response.json({ error: (e as Error).message }, { status: 404 });
  }
  return new Response("Not Found", { status: 404 });
}

function page(sid: string, items: string[], scores: Record<string, any>, locked: boolean): string {
  const cards = items.map((b, i) => {
    const s = scores[b] ?? {};
    const radios = [1, 2, 3, 4, 5].map((q) => `<label><input type="radio" name="q-${b}" value="${q}" ${s.quality === q ? "checked" : ""} ${locked ? "disabled" : ""}> ${q}</label>`).join(" ");
    const guess = ["agent", "studio"].map((g) => `<label><input type="radio" name="g-${b}" value="${g}" ${s.guess === g ? "checked" : ""} ${locked ? "disabled" : ""}> ${g === "agent" ? "made by the agent" : "from the real production"}</label>`).join(" ");
    return `<section class="card" data-b="${b}"><img src="/img/${sid}/${b}.png" alt="item ${i + 1}">
<div class="f"><b>#${i + 1}</b><div>Production quality: ${radios}</div><div>Guess: ${guess}</div>
<input class="note" placeholder="note (optional)" value="${esc(s.note ?? "")}" ${locked ? "disabled" : ""}><span class="st">${s.quality ? "saved" : ""}</span></div></section>`;
  }).join("");
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Blind Scoring</title>
<style>:root{--bg:#121417;--card:#1c1f24;--fg:#e8ebf0;--mut:#9aa3af;--acc:#f0a34a}@media (prefers-color-scheme: light){:root{--bg:#f3f2ee;--card:#fff;--fg:#1b1d21;--mut:#5b6370;--acc:#b5651d}}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,system-ui,sans-serif}main{max-width:1180px;margin:auto;padding:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(520px,1fr));gap:16px}.card{background:var(--card);border-radius:10px;overflow:hidden}
img{width:100%;display:block}.f{padding:10px 12px;display:grid;gap:6px}.note{width:100%;padding:4px;background:transparent;color:var(--fg);border:1px solid var(--mut);border-radius:6px}
.st{color:var(--acc);font-size:12px}p{color:var(--mut)}button{background:var(--acc);border:0;padding:8px 14px;border-radius:6px;font-weight:600;cursor:pointer}
@media (max-width:560px){.grid{grid-template-columns:1fr}}</style></head><body><main>
<h1>Blind scoring</h1><p>Each image is either a frame from a real production or a render made by the agent. Sources are hidden and the order is random. For each one, rate production quality (1 = clearly amateur, 5 = indistinguishable from a finished professional film) and guess where it came from. Answers save as you click. ${locked ? "<b>This session is locked.</b>" : "When every item is scored, lock the session; only then can it be unblinded."}</p>
<div class="grid">${cards}</div><p>${locked ? "" : `<button id="lock">Lock my scores</button> <span id="lst"></span>`}</p></main>
<script>
const S=${JSON.stringify(sid)};
function send(card){const b=card.dataset.b;const q=card.querySelector('input[name="q-'+b+'"]:checked');const g=card.querySelector('input[name="g-'+b+'"]:checked');
if(!q||!g)return;fetch('/api/score',{method:'POST',body:JSON.stringify({s:S,b,quality:+q.value,guess:g.value,note:card.querySelector('.note').value})})
.then(r=>r.json()).then(j=>card.querySelector('.st').textContent=j.ok?'saved':j.error);}
document.querySelectorAll('.card').forEach(c=>{c.addEventListener('change',()=>send(c));});
const L=document.getElementById('lock');if(L)L.onclick=()=>fetch('/api/lock',{method:'POST',body:JSON.stringify({s:S})}).then(r=>r.json()).then(j=>{document.getElementById('lst').textContent=j.ok?'Locked. Tell Claude to unblind.':j.error;if(j.ok)location.reload();});
</script></body></html>`;
}

if (import.meta.main) {
  const port = Number(process.env.BLIND_PORT ?? 7795);
  Bun.serve({ hostname: "127.0.0.1", port, fetch: handle });
  console.log(`blind scoring on http://127.0.0.1:${port}/?s=<session>`);
}
