from __future__ import annotations

from typing import List, Tuple

from .config import WEIGHTS, ScoreWeights
from .models import Resolution, ScoredResolution
from .resolve import _by_provider

def apply_caps(total, only_enrichment, has_named_identity, weights, reasons=None):
    if only_enrichment and total > weights.cap_only_enrichment:
        if reasons is not None:
            reasons.append(("cap: lone enrichment source", weights.cap_only_enrichment - total))
        total = weights.cap_only_enrichment
    if not has_named_identity and total > weights.cap_no_named_identity:
        if reasons is not None:
            reasons.append(("cap: no named identity", weights.cap_no_named_identity - total))
        total = weights.cap_no_named_identity
    return total

def score(resolution: Resolution, weights: ScoreWeights = WEIGHTS) -> ScoredResolution:
    res = resolution
    reasons: List[Tuple[str, int]] = []
    total = 0

    reg = _by_provider(res.candidates, "registry")
    lst = _by_provider(res.candidates, "listing")
    enr = _by_provider(res.candidates, "enrichment")

    def add(label: str, delta: int):
        nonlocal total
        total += delta
        reasons.append((label, delta))

    if reg and reg.name:
        add("registry name", weights.registry_name)
        if res.is_decision_maker_role:
            add(f"registry decision-maker role ({res.chosen_role})", weights.registry_dm_role)

    if lst and (lst.name or lst.phone):
        add("listing contact", weights.listing_contact)

    if enr and (enr.email or enr.phone):
        conf = enr.provider_confidence or 0
        delta = int(round(weights.enrichment_channel_max * conf / 100))
        add(f"enrichment channel (provider_confidence {conf})", delta)

    if res.name_agreement:
        add("name agreement (registry<->listing)", weights.name_agreement)
    if res.email_name_corroboration:
        add("email corroborates named person", weights.email_name_corroboration)
    if res.channel_agreement:
        add("phone agreement (listing<->enrichment)", weights.channel_agreement)

    if res.name_conflict:
        add("name conflict (registry vs listing)", weights.name_conflict)
    if res.channel_conflict:
        add("phone conflict (listing vs enrichment)", weights.channel_conflict)

    clamped = max(0, min(100, total))
    if clamped != total:
        reasons.append(("clamp to 0..100", clamped - total))
    total = clamped

    total = apply_caps(total, res.only_enrichment, res.has_named_identity, weights, reasons)

    return ScoredResolution(resolution=res, score=total, reasons=reasons)
