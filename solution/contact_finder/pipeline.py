from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Set

from .gate import gate
from .loader import load_companies
from .models import OutputRow
from .normalize_adapter import normalize_all
from .providers import MockProvider, Provider
from .resolve import resolve
from .score import score

def load_suppression(path) -> Set[str]:
    p = Path(path)
    if not p.exists():
        return set()
    out: Set[str] = set()
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        out.add(s.lower())
    return out

def run_pipeline(
    input_csv,
    provider: Provider,
    suppression: Optional[Set[str]] = None,
) -> List[OutputRow]:
    suppression = suppression or set()
    rows: List[OutputRow] = []
    for company in load_companies(input_csv):
        raw = provider.lookup(company.company_name)
        candidates = normalize_all(raw)
        resolution = resolve(company, candidates)
        scored = score(resolution)
        rows.append(gate(scored, suppression))
    return rows

def run_from_files(input_csv, mocks_json, suppression_path=None) -> List[OutputRow]:
    provider = MockProvider.from_file(mocks_json)
    suppression = load_suppression(suppression_path) if suppression_path else set()
    return run_pipeline(input_csv, provider, suppression)
