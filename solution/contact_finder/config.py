from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SOLUTION_DIR = Path(__file__).resolve().parents[1]

DEFAULT_INPUT_CSV = _REPO_ROOT / "challenge" / "data" / "companies.csv"
DEFAULT_MOCKS_JSON = _REPO_ROOT / "challenge" / "mocks" / "enrichment_responses.json"
DEFAULT_SUPPRESSION = _SOLUTION_DIR / "suppression.txt"
DEFAULT_OUTPUT_DIR = _SOLUTION_DIR / "output"

CONFIDENCE_THRESHOLD = 70

@dataclass(frozen=True)
class ScoreWeights:
    registry_name: int = 35
    registry_dm_role: int = 10
    listing_contact: int = 20
    enrichment_channel_max: int = 15
    name_agreement: int = 20
    email_name_corroboration: int = 15
    channel_agreement: int = 10
    name_conflict: int = -30
    channel_conflict: int = -15
    cap_only_enrichment: int = 40
    cap_no_named_identity: int = 45

WEIGHTS = ScoreWeights()

ROLE_TIERS = (
    (1, ("accounts payable", "ap manager", "accounts-payable", "a/p", "ap/ar")),
    (2, ("owner", "co-owner", "founder", "proprietor", "principal",
         "president", "managing member", "managing partner", "partner", "ceo")),
    (3, ("cfo", "chief financial officer", "controller", "comptroller", "finance")),
    (4, ("office manager", "business manager", "operations manager")),
)
NON_DM_RANK = 99

GENERIC_EMAIL_LOCALPARTS = frozenset({
    "info", "office", "contact", "sales", "admin", "support", "hello", "team",
    "billing", "accounts", "ar", "ap", "mail", "enquiries", "inquiries",
    "service", "help", "noreply", "no-reply",
})
PERSONAL_EMAIL_DOMAINS = frozenset({
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
    "icloud.com", "me.com", "live.com", "msn.com", "proton.me", "protonmail.com",
})

PROVIDER_ORDER = ("registry", "listing", "enrichment")
