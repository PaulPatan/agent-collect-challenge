from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

@dataclass
class CompanyInput:
    company_name: str
    mailing_address: str

@dataclass
class Candidate:
    provider: str
    source_url: str
    name: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    provider_confidence: Optional[int] = None

@dataclass
class Resolution:
    company: CompanyInput
    candidates: List[Candidate] = field(default_factory=list)

    chosen_name: Optional[str] = None
    chosen_role: Optional[str] = None
    role_rank: int = 99
    is_decision_maker_role: bool = False

    chosen_channel: Optional[str] = None
    channel_kind: Optional[str] = None
    channel_provider: Optional[str] = None

    providers: List[str] = field(default_factory=list)
    source_urls: List[str] = field(default_factory=list)

    has_named_identity: bool = False
    only_enrichment: bool = False
    name_agreement: bool = False
    channel_agreement: bool = False
    email_name_corroboration: bool = False
    name_conflict: bool = False
    channel_conflict: bool = False

@dataclass
class ScoredResolution:
    resolution: Resolution
    score: int
    reasons: List[Tuple[str, int]] = field(default_factory=list)

@dataclass
class OutputRow:
    company_name: str
    mailing_address: str
    contact_name: str
    contact_role: str
    contact_email_or_phone: str
    confidence_score: int
    source: str
    needs_human_review: bool
    review_reason: str
    source_urls: str
    score_reasons: str
