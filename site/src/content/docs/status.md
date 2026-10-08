---
title: Where things stand
description: What newblender has measured and built so far, and what is still open.
---

newblender is in **discovery**. Nothing in the engine has been redesigned yet. Everything published here is measurement, evidence and method.

## The documents

- **[RFC 0001](/newblender/rfc/0001-newblender/)** is the framing. It has seven resolutions so far: the dead facts, discovery first, two tracks, a virtual production, the four-pass method, six-layer verification and capability scoring.
- **[RFC 0002](/newblender/rfc/0002-research-publication/)** proposes publishing the discovery work as a research series. It is open.
- **[The S01 Modeling brief](/newblender/discovery/s01-modeling/05-brief/)** covers the first pipeline stage, studied end to end in four passes: read, dissect, trace, why.

## What the agent has built

Each demo is a first slice of a [showcase](/newblender/showcase/00-index/) plan. It was built live in Blender 5.2 and judged by checks written before the build.

| Demo | Checks | Blind quality (agent vs. studio, 1–5) |
|---|---|---|
| [001 Chair](/newblender/demos/001-chair/) | 12/12 | not scored |
| [002 Flow: flooded forest, 4K](/newblender/demos/002-flow/) | 11/11, plus reproducibility and render budget | 1.00 vs. 3.75 |
| [003 Charge: battery-factory bay](/newblender/demos/003-charge/) | 11/11 live; 2 open fails awaiting rulings | 2.33 vs. 4.50 |

## The first honest number

In the first blind session, the owner rated 12 images: 6 agent renders and 6 real production frames. They didn't know which was which.

- **Mean quality:** agent work scored 1.67, studio work 4.00.
- **Guessing the source:** 83% correct.
- **Self-scoring:** the agent had rated its own Flow shot 2.5, but blind it scored 1.0.

Passing every technical check is not the same as looking good. That's why the quality number comes only from blind rating.

## Open

- Two check rules in Charge are waiting on the owner's ruling: should UV stretch be weighted by area, and should known emitters be masked from the firefly count?
- RFC 0002's publication questions.
