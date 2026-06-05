from __future__ import annotations

import re
from typing import List, Optional

from .config import GENERIC_EMAIL_LOCALPARTS, PERSONAL_EMAIL_DOMAINS

_NICKNAME_GROUPS = {
    "robert": ("bob", "bobby", "rob", "robbie", "bert"),
    "william": ("will", "bill", "billy", "willie", "liam"),
    "richard": ("rick", "ricky", "rich", "richie", "dick"),
    "james": ("jim", "jimmy", "jamie"),
    "john": ("jack", "johnny", "jon"),
    "michael": ("mike", "mick", "mickey", "micky"),
    "charles": ("charlie", "chuck", "chas"),
    "thomas": ("tom", "tommy"),
    "joseph": ("joe", "joey"),
    "daniel": ("dan", "danny"),
    "matthew": ("matt", "matty"),
    "christopher": ("chris", "topher"),
    "anthony": ("tony",),
    "edward": ("ed", "eddie", "ted", "ned"),
    "andrew": ("andy", "drew"),
    "nicholas": ("nick", "nicky"),
    "benjamin": ("ben", "benny"),
    "samuel": ("sam", "sammy"),
    "david": ("dave", "davey"),
    "stephen": ("steve", "stevie"),
    "kenneth": ("ken", "kenny"),
    "ronald": ("ron", "ronnie"),
    "donald": ("don", "donnie"),
    "margaret": ("maggie", "meg", "peggy", "marge"),
    "elizabeth": ("liz", "beth", "betty", "eliza", "lizzie", "betsy"),
    "katherine": ("kate", "katie", "kathy", "cathy", "kat", "katy"),
    "catherine": ("kate", "katie", "kathy", "cathy", "cat"),
    "jennifer": ("jen", "jenny", "jenn"),
    "patricia": ("pat", "patty", "trish", "tricia"),
    "susan": ("sue", "susie", "suzy"),
    "deborah": ("deb", "debbie", "debby"),
    "barbara": ("barb", "barbie"),
    "victoria": ("vicky", "vic", "tori"),
    "alexandra": ("alex", "lexi", "sandra"),
    "alexander": ("alex", "alec", "xander"),
}
_NICKNAME_TO_CANON = {}
for _canon, _variants in _NICKNAME_GROUPS.items():
    _NICKNAME_TO_CANON[_canon] = _canon
    if isinstance(_variants, str):
        _variants = (_variants,)
    for _v in _variants:
        _NICKNAME_TO_CANON.setdefault(_v, _canon)

_HONORIFICS = {"mr", "mrs", "ms", "miss", "dr", "prof", "sir", "rev", "mx"}

def canon_token(token: str) -> str:
    t = token.lower().strip(".")
    return _NICKNAME_TO_CANON.get(t, t)

def clean_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    v = re.sub(r"\s+", " ", value).strip()
    return v or None

def name_tokens(name: Optional[str]) -> List[str]:
    if not name:
        return []
    cleaned = re.sub(r"\([^)]*\)", " ", name)
    cleaned = re.sub(r"[^A-Za-z.\s'-]", " ", cleaned)
    toks = []
    for raw in cleaned.split():
        t = raw.strip(".").lower()
        if not t or t in _HONORIFICS:
            continue
        toks.append(t)
    return toks

def _first_last(tokens: List[str]):
    if not tokens:
        return None, None
    if len(tokens) == 1:
        return tokens[0], tokens[0]
    return tokens[0], tokens[-1]

def names_match(a: Optional[str], b: Optional[str]) -> bool:
    ta, tb = name_tokens(a), name_tokens(b)
    if not ta or not tb:
        return False
    fa, la = _first_last(ta)
    fb, lb = _first_last(tb)
    if canon_token(la) != canon_token(lb):
        return False
    if _first_name_match(fa, fb):
        return True
    return False

def _first_name_match(fa: str, fb: str) -> bool:
    if canon_token(fa) == canon_token(fb):
        return True
    if len(fa) == 1 and fb.startswith(fa):
        return True
    if len(fb) == 1 and fa.startswith(fb):
        return True
    return False

def phone_digits(phone: Optional[str]) -> Optional[str]:
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    if not digits:
        return None
    return digits[-10:] if len(digits) >= 10 else digits

def phones_match(a: Optional[str], b: Optional[str]) -> bool:
    da, db = phone_digits(a), phone_digits(b)
    return bool(da and db and da == db)

def email_localpart(email: Optional[str]) -> Optional[str]:
    if not email or "@" not in email:
        return None
    return email.split("@", 1)[0].lower()

def email_domain(email: Optional[str]) -> Optional[str]:
    if not email or "@" not in email:
        return None
    return email.split("@", 1)[1].lower().strip()

def is_personal_email(email: Optional[str]) -> bool:
    dom = email_domain(email)
    return bool(dom and dom in PERSONAL_EMAIL_DOMAINS)

def is_generic_localpart(email: Optional[str]) -> bool:
    lp = email_localpart(email)
    if not lp:
        return False
    head = re.split(r"[._\-+]", lp)[0]
    return lp in GENERIC_EMAIL_LOCALPARTS or head in GENERIC_EMAIL_LOCALPARTS

def email_corroborates_name(email: Optional[str], name: Optional[str]) -> bool:
    lp = email_localpart(email)
    toks = [t for t in name_tokens(name) if len(t) >= 2]
    if not lp or not toks:
        return False
    parts = [p for p in re.split(r"[._\-+0-9]", lp) if len(p) >= 2]
    name_canon = {canon_token(t) for t in toks}
    for p in parts:
        if p in toks or canon_token(p) in name_canon:
            return True
    if lp in toks or canon_token(lp) in name_canon:
        return True
    return False

def classify_role(role: Optional[str]):
    from .config import NON_DM_RANK, ROLE_TIERS
    if not role:
        return NON_DM_RANK, False
    r = role.lower().strip()
    best = NON_DM_RANK
    for rank, phrases in ROLE_TIERS:
        for phrase in phrases:
            if phrase in r:
                best = min(best, rank)
                break
    return best, best != NON_DM_RANK
