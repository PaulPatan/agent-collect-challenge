# PLAN — Contact Finder

## Architecture

Turn `data/companies.csv` into one **attributable** decision-maker contact per row with a self-computed confidence score, provenance, and an honest `needs_human_review` flag. Never a fabricated contact.

Deterministic, idempotent batch pipeline; one row = one isolated unit (30 in -> 30 out):

1. **Ingest:** canonicalize name (casefold, strip LLC/Inc/Co), assign company_id.
2. **Filter:** query registry, listing, enrichment behind one Provider interface; absent key / all-null / timeout -> found=false (data, not a crash).
3. **Normalize:** map each provider -> ONE Candidate `{name?,role?,email?,phone?,provider,source_url}`.
4. **Resolve:** merge a company's candidates -> best name+role + best channel (pure fn).
5. **Score:** additive formula -> `{score 0..100, reasons[]}` (pure fn).
6. **Gate:** score < threshold OR no source_url OR conflict -> review + empty contact.
7. **Emit:** output row + provenance trail.

`normalize` absorbs all provider weirdness into one shape, so `score`/`gate` are pure functions, unit-testable against the named scenarios (agreeing sources, lone weak guess, no sources). The `Provider` interface is the seam where real APIs (Secretary-of-State, maps, a licensed enricher) swap in later. Slice runs synchronously; the design allows a real queue (per-`(company,provider)` jobs, retries/backoff) without touching adapters — not built, overkill for 30 rows.

## Sources & strategy

Three signals, the design assumes any one is wrong or empty, and that some rows correctly resolve to nothing.

- **registry** `{name, role}` — the only *identity* signal, but **sparsest**; the registered agent is often a lawyer/formation service, not who pays invoices. Trust the name, treat the role skeptically. No channel.
- **listing** `{name|null, phone}` — *reachability*: a real business line. Name is role-less (receptionist? stale owner?).
- **enrichment** `{email, phone, provider_confidence}` — widest coverage, lowest floor (precise email, weak guess, or `info@` catch-all). **Carries no name** — it can attach a *channel*, never corroborate a *person*. `provider_confidence` is one input, never my output.

Only registry+listing carry names, so name-agreement = registry-vs-listing; channel-agreement = listing-phone-vs-enrichment-phone. Closed false-positive path: a registry *name* must not validate an unrelated enrichment *email* — the email is a capped channel, not proof of the person. Failure handling: absent -> contributes nothing (a single-source row can't earn agreement, so it lands in review by design); disagreement -> penalty + review; lone weak guess -> review; unattributable -> never emitted (≥1 `source_url` is hard). No real scraping — fixtures only.

## Quality

**Dedupe** is *within* a company (isolated by `company_id`): name = first non-null by registry > listing (never invented); role = registry role or null (never manufactured from a role-less name); channel = prefer email, prefer one two sources agree on. Normalize before comparing (digits-only phones, lowercased emails, token-set name match with a last-name+initial floor so `J. Smith`↔`John Smith` agrees but `John`↔`Jane` doesn't). A shared *generic* line is reachability agreement, not person agreement.

**confidence_score** — additive, auditable, every term in `reasons[]`; start 0, clamp 0..100:


| Signal                                                          | Δ                               |
| --------------------------------------------------------------- | ------------------------------- |
| registry named contact                                          | +35                             |
| registry explicit decision-maker role (owner/CFO/AP/office mgr) | +10                             |
| listing contact (name and/or phone)                             | +20                             |
| enrichment channel                                              | +15 × `provider_confidence`/100 |
| name agreement (registry ↔ listing)                             | +20                             |
| channel agreement (listing ↔ enrichment phone)                  | +15                             |
| conflict (different people / channels)                          | −25                             |


Hard caps override the sum: lone enrichment guess -> cap 40 (can't clear the gate); no role anywhere -> cap below threshold (generic line alone -> review); name-less phone -> role `business_line`, never dressed up. **Default threshold = 70.** Examples: registry name+role + agreeing listing = 85 -> emit; lone enrichment @90 ≈ 14 -> review; phone-only -> review; no sources -> 0 -> review.

**Provenance:** output carries `source` (provider labels) + the `mock://` `source_url`s verbatim. Invariant in `gate`: **no `source_url` -> no contact**. Rejected candidates kept in an audit record with their reason.

**Cannot-verify** is a first-class outcome: `needs_human_review=true`, contact fields EMPTY, computed low score, and a `review_reason` ∈ `{no_sources, single_weak_source, conflicting_sources, role_unverified}`. A blank, flagged row is a correct answer.

**False-positive risk** (the expensive error — dunning the wrong party): role gating (agent ≠ AP), unrelated-email guard, catch-all mailboxes capped as channel-only, conflict penalty. I'd rather emit 8 confident + 22 honest "review" than 30 confident-looking rows where 10 are wrong.

## Privacy / compliance

Output drives **payment outreach**, so mis-targeting carries legal/reputational cost. Target the **business/role** (owner, CFO, AP/office manager) via public records + contracted providers, not personal consumer profiles.

- **Will:** use only the sanctioned providers; attach a `source_url` to every value (auditable/correctable); keep `fetched_at`; consult a suppression / Do-Not-Contact list **before emitting** (see Q3); keep cannot-verify non-penalized so there's no incentive to fabricate; centralize the threshold so caution is dial-able.
- **Will NOT:** fabricate/pattern-generate emails or phones (the fake-precision hard-reject); emit personal/home details; scrape or bypass ToS; treat `provider_confidence` as verification; merge similar-looking names; auto-send sub-threshold guesses.

Live-system flags (outside the mock): **FDCPA** (consumer debt — these are commercial, but honor its spirit: right party, business channels, stop requests), **TCPA** (mobile vs landline), **CCPA/CPRA**. Provenance + suppression + cannot-verify are the controls that make a compliance review tractable.

## Clarifying questions

1. **Cost asymmetry: how much worse is a false positive (dun the WRONG party) than a false negative (route a findable contact to review)? Where should the threshold sit, one global value or per-segment?**
  - *Why:* sets the threshold and the whole precision/recall posture; a wrong dunning message is a legal/brand event, a review row costs minutes.
  - *Default:* false positives far costlier -> threshold 70, global, bias to review on conflict.
  - *Changes:* lower -> wider auto-emit / softer conflict penalty; higher -> add a "verified" tier (≥85); per-segment -> threshold becomes config, not a constant. Architecture unchanged.
2. **Is a registered-agent/registry name an acceptable proxy for the decision-maker, or only an explicit owner/CFO/AP/office-manager role? Can a generic verified channel (business line, `billing@`) count on its own?**
  - *Why:* defines "right decision-maker" and sets the weights; the registered agent is often *not* who pays invoices, and a generic line is actionable but not an *identity* — conflating them is the central false-positive risk.
  - *Default:* only explicit roles earn the role bonus; bare agent = name only; name-less line = weak `business_line` that can't clear threshold alone.
  - *Changes:* if agent counts -> registry weight rises, more rows auto-clear; if generic channels count -> `role_unverified` rows clear, coverage up but wrong-party risk up (loops back to Q1).
3. **Could any accounts be sole proprietors where the debt is effectively an individual's (FDCPA + stricter personal-data rules)? Is there a suppression / Do-Not-Contact list I must honor before emitting?**
  - *Why:* if consumer, an owner's personal cell becomes high-risk PII, not a fair business contact — it changes what's *permissible*, not just scoring; emitting a suppressed contact violates regardless of confidence.
  - *Default:* treat all as B2B commercial, role/business channels only, avoid personal cell/home; assume a suppression list exists (empty in fixture) and filter pre-emit.
  - *Changes:* if consumer debts exist -> add entity-type routing from the **registry entity-type field** (not the brittle name suffix), suppress personal-contact emission, raise their threshold; a populated list makes the pre-emit filter mandatory (test: suppressed company always yields an empty, flagged row).

