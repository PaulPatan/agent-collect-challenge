from __future__ import annotations

from typing import Dict, List

from .models import Candidate
from .normalize import clean_text

_KNOWN_PROVIDERS = ("registry", "listing", "enrichment")

def _coerce_confidence(value):
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

def candidate_from_raw(provider: str, raw: dict) -> Candidate | None:
    if not isinstance(raw, dict):
        return None
    source_url = clean_text(raw.get("source_url")) or ""
    name = clean_text(raw.get("name"))
    role = clean_text(raw.get("role"))
    email = clean_text(raw.get("email"))
    if email:
        email = email.lower()
    phone = clean_text(raw.get("phone"))
    confidence = _coerce_confidence(raw.get("provider_confidence"))

    if not any((name, role, email, phone)):
        return None
    if not source_url:
        return None

    return Candidate(
        provider=provider,
        source_url=source_url,
        name=name,
        role=role,
        email=email,
        phone=phone,
        provider_confidence=confidence,
    )

def normalize_all(raw_by_provider: Dict[str, dict]) -> List[Candidate]:
    candidates: List[Candidate] = []
    for provider in _KNOWN_PROVIDERS:
        if provider in raw_by_provider:
            cand = candidate_from_raw(provider, raw_by_provider[provider])
            if cand is not None:
                candidates.append(cand)
    return candidates
