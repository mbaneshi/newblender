# newblender

Blender's source, redesigned for AI agents as the primary user. **Site:** <https://mbaneshi.github.io/newblender/> (English and Persian). **newblender is not a content tool or an MCP wrapper.** It is a study of which parts of Blender's architecture assume a human with a mouse and keyboard, and what an engine built for agents would look like instead.

**Process:** RFC → discovery → spec → plan. No newblender implementation starts before a spec is approved. Everything here so far is discovery: measurement, demos and tools.

## Start here

- **[Research](docs/research/approach.md)** covers how we work, with a dated [log](docs/research/log.md), [findings and current thinking](docs/research/findings.md), and the [roadmap](docs/research/roadmap.md).
- **[RFC 0001: newblender](docs/rfc/0001-newblender.md)** sets out the framing, the open questions and resolutions R1–R7. It covers the dead facts, the four-pass method, six-layer verification and capability scoring.
- **[RFC 0002: research publication](docs/rfc/0002-research-publication.md)** is a proposal to publish the discovery work as a paper series. It is open, and nothing is decided yet.
- **[S01 Modeling brief](docs/discovery/s01-modeling/05-brief.md)** is the first stage studied end to end.

## Layout

| Path | What it holds |
|---|---|
| `docs/research/` | Approach, dated log, findings and positions, roadmap |
| `docs/rfc/` | RFCs: the decisions and the reasoning behind them |
| `docs/discovery/` | Notes 00–03, the S01 pilot, 320 capability cards and the transformation ledger (L-001…) |
| `docs/showcase/` | 20 verified Blender works, each with a plan for how an agent would build it ([index](docs/showcase/00-index.md)) |
| `docs/demos/` | Check reports for the slices actually built live: [001 chair](docs/demos/001-chair/report.md), [002 Flow](docs/demos/002-flow/report.md), [003 Charge](docs/demos/003-charge/report.md) |
| `tools/registry/` | Dumps Blender's operator registry, scans the C/C++ source for operator definitions, and joins the two |
| `tools/census/` | Takes a census of what real production `.blend` files contain |
| `tools/cards/` | Generates the capability cards from the S01 trace |
| `tools/live/` | A bridge to a running Blender, plus the demo build scripts and their check scripts |
| `tools/blind/` | Blind quality scoring: agent renders mixed with real frames, rated without knowing the source |
| `site/` | The public site: Astro + Starlight, built from `docs/` by `site/scripts/sync-docs.mjs` and deployed to GitHub Pages from `dev` |
| `scripts/` | Branch rails: `new-issue`, `promote`, `setup-hooks`, and the pre-push guard |

## Data lives outside the repo

Large and licensed material lives in `~/newblender-data/` and is never committed:

- downloaded production files
- census output
- the operator registry
- Poly Haven CC0 assets
- demo `.blend` files, renders and videos
- blind sessions, including reference frames that are for local evaluation only

The reports in `docs/demos/` are copies of the text reports kept there.

## Running the tools

**Live bridge.** This needs Blender 5.2 with the Blender Lab MCP add-on (id `mcp`) enabled. Online mode is required.

```bash
/Applications/Blender.app/Contents/MacOS/Blender --online-mode --python tools/live/start_bridge.py
python3 tools/live/bl.py -e "result['n'] = len(bpy.data.objects)"   # run code in the live session
python3 tools/live/snap.py                                           # screenshot the window
python3 tools/live/bl.py tools/live/demos/chair_build.py             # build a demo...
python3 tools/live/bl.py tools/live/checks/chair_checks.py           # ...then run its pre-written checks
```

**Blind scoring.** This uses Bun. `bun test tools/blind` is the gate.

```bash
bun tools/blind/make_session.ts <session-id> <manifest.json> [width]  # normalise and shuffle the images; key stays private
bun tools/blind/server.ts                                             # http://127.0.0.1:7795/?s=<session-id>
bun tools/blind/unblind.ts <session-id>                               # only after the owner locks; writes results.md
```

## Branches

This repo follows gitflow-lite:
- `dev` is the integration branch.
- `main` is the released line, and moves only by tag (`scripts/promote vX.Y.Z`).
- Each issue gets its own worktree branch off `dev` (`scripts/new-issue`).

The repo has no GitHub remote yet.
