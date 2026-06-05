from __future__ import annotations

from typing import List, Optional

from .config import PROVIDER_ORDER
from .models import Candidate, CompanyInput, Resolution
from .normalize import (
    classify_role,
    email_corroborates_name,
    is_personal_email,
    names_match,
    phones_match,
)

def _by_provider(candidates: List[Candidate], provider: str) -> Optional[Candidate]:
    for c in candidates:
        if c.provider == provider:
            return c
    return None

def _select_channel(reg, lst, enr, chosen_name, email_corroborates):
    email = enr.email if enr else None
    business_email = email if (email and not is_personal_email(email)) else None

    listing_phone = lst.phone if lst else None
    enrich_phone = enr.phone if enr else None

    if business_email and chosen_name and email_corroborates:
        return business_email, "email", "enrichment"

    if listing_phone and enrich_phone and phones_match(listing_phone, enrich_phone):
        return listing_phone, "phone", "listing+enrichment"
    if listing_phone:
        return listing_phone, "phone", "listing"
    if enrich_phone:
        return enrich_phone, "phone", "enrichment"

    if business_email:
        return business_email, "email", "enrichment"
    return None, None, None

def resolve(company: CompanyInput, candidates: List[Candidate]) -> Resolution:
    reg = _by_provider(candidates, "registry")
    lst = _by_provider(candidates, "listing")
    enr = _by_provider(candidates, "enrichment")

    res = Resolution(company=company, candidates=list(candidates))
    res.providers = [p for p in PROVIDER_ORDER if _by_provider(candidates, p)]
    res.source_urls = [
        c.source_url for p in PROVIDER_ORDER for c in candidates if c.provider == p
    ]

    if reg and reg.name:
        res.chosen_name = reg.name
    elif lst and lst.name:
        res.chosen_name = lst.name
    res.has_named_identity = res.chosen_name is not None

    res.chosen_role = reg.role if (reg and reg.role) else None
    res.role_rank, res.is_decision_maker_role = classify_role(res.chosen_role)

    if reg and reg.name and lst and lst.name:
        if names_match(reg.name, lst.name):
            res.name_agreement = True
        else:
            res.name_conflict = True

    lp = lst.phone if lst else None
    ep = enr.phone if enr else None
    if lp and ep:
        if phones_match(lp, ep):
            res.channel_agreement = True
        else:
            res.channel_conflict = True

    if enr and enr.email and res.chosen_name and not is_personal_email(enr.email):
        res.email_name_corroboration = email_corroborates_name(enr.email, res.chosen_name)

    res.chosen_channel, res.channel_kind, res.channel_provider = _select_channel(
        reg, lst, enr, res.chosen_name, res.email_name_corroboration
    )

    res.only_enrichment = bool(enr) and not reg and not lst
    return res
