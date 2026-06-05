from __future__ import annotations

from typing import Set

from .config import CONFIDENCE_THRESHOLD
from .models import OutputRow, ScoredResolution
from .normalize import email_domain, phone_digits

def _format_reasons(reasons) -> str:
    return "; ".join(f"{label} {delta:+d}" for label, delta in reasons)

def is_suppressed(company_name: str, resolution, suppression: Set[str]) -> bool:
    if not suppression:
        return False
    keys = {company_name.strip().lower()}
    channel = resolution.chosen_channel
    if channel:
        keys.add(channel.strip().lower())
        dig = phone_digits(channel)
        if dig:
            keys.add(dig)
        dom = email_domain(channel)
        if dom:
            keys.add(dom)
    return bool(keys & suppression)

def _review_reason(res, suppressed: bool) -> str:
    if suppressed:
        return "suppressed"
    if not res.candidates:
        return "no_sources"
    if res.name_conflict or res.channel_conflict:
        return "conflicting_sources"
    if res.chosen_channel is not None and not res.has_named_identity:
        return "role_unverified"
    return "single_weak_source"

def gate(
    scored: ScoredResolution,
    suppression: Set[str] = frozenset(),
    threshold: int = CONFIDENCE_THRESHOLD,
) -> OutputRow:
    res = scored.resolution
    company = res.company
    source = "+".join(res.providers)
    source_urls = " | ".join(res.source_urls)
    score_reasons = _format_reasons(scored.reasons)

    suppressed = is_suppressed(company.company_name, res, suppression)
    emittable = (
        scored.score >= threshold
        and res.chosen_channel is not None
        and not suppressed
    )

    if emittable:
        return OutputRow(
            company_name=company.company_name,
            mailing_address=company.mailing_address,
            contact_name=res.chosen_name or "",
            contact_role=res.chosen_role or "",
            contact_email_or_phone=res.chosen_channel,
            confidence_score=scored.score,
            source=source,
            needs_human_review=False,
            review_reason="",
            source_urls=source_urls,
            score_reasons=score_reasons,
        )

    return OutputRow(
        company_name=company.company_name,
        mailing_address=company.mailing_address,
        contact_name="",
        contact_role="",
        contact_email_or_phone="",
        confidence_score=scored.score,
        source=source,
        needs_human_review=True,
        review_reason=_review_reason(res, suppressed),
        source_urls=source_urls,
        score_reasons=score_reasons,
    )
