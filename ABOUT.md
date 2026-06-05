# ABOUT

> Draft scaffold. The "How you work with AI tools" section is drafted from how this challenge was actually built — edit it into your own voice. The `TODO (you)` lines are personal and must be filled in by you; delete these two intro lines before submitting.

## Why this role

> TODO (you): 2-3 sentences — what about AI-native engineering / this collections-contact problem interests you?

## How you work with AI tools

I work plan-first and keep the model on a short leash with a human checkpoint at each step. On this challenge:

- **Plan before code.** I committed `PLAN.md` on its own, before reading the clarifications or writing a line of the slice — the timestamped plan is the artifact, and adapting it afterward is the point.
- **Generate options, don't take the first answer.** I had the AI produce several independent plan drafts from different angles, then critique and synthesize them, rather than accepting one pass.
- **Where I trust the model:** drafting boilerplate, proposing candidate approaches, mechanical refactors, and scaffolding the pipeline.
- **Where I override it:** I hand-traced every confidence score against the real fixture data instead of trusting generated numbers; and when an automated review suggested editing the committed `PLAN.md` so it matched the code, I rejected that — the plan is a Stage-A artifact, so I documented the plan→build adaptation instead of rewriting history.
- **Verification over vibes.** I treated "cannot verify" as a first-class result, enforced provenance on every emitted value, and confirmed the build's output row-by-row against an independent hand analysis before trusting it.

> TODO (you): trim/adjust so this reflects how *you* actually direct AI tools day to day.

## Your last project (structured — this is the pre-filter)

*Project: Downtobid — AI features + a document-processing pipeline for a construction bidding platform.*

- **One ambiguity** you faced and how you resolved it: the spec didn't say how to handle low-confidence AI email classifications, so I routed those to human review instead of auto-acting and confirmed the cutoff with the PM.
- **One tradeoff** you made and why: migrated the PDF-processing service from Python to a Go microservice on Cloud Run — took the rewrite cost to get throughput and reliability the Python version couldn't hit at scale.
- **One mistake** you made and what you changed: I missed that Pub/Sub delivers at-least-once, so a bid-invite sequence sent duplicate emails; I made each workflow step idempotent with dedup keys.
- **One review comment** that made you change your mind: a reviewer flagged a synchronous LLM call sitting in the request path; I moved the classification to an async Pub/Sub-backed job.

## Anything you'd improve about THIS challenge or our CLAUDE.md

Nothing to change to the challenge, but for the [CLAUDE.md](http://CLAUDE.md) I would change it as follows:  
add more specific and detailed code pattern rules, so what I usually use in the start of all of my conversations with claude is something like this, and I noticed it HELPS A LOT: "Never assume/guess anything, anything you say has to be double fact checked. From now on in our conversations, all your responses to my prompts should be as short as possible, concise, effective and straight to the point. Please also make sure to be as consistent as you can with proven patterns of this codebase, we need to keep consistency and also to be as surgical in your code, no unwanted changes."

