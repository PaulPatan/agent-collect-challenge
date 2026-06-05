from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from .models import CompanyInput
from .normalize import clean_text

def load_companies(csv_path) -> List[CompanyInput]:
    path = Path(csv_path)
    companies: List[CompanyInput] = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            name = clean_text(row.get("company_name"))
            if not name:
                continue
            companies.append(
                CompanyInput(
                    company_name=name,
                    mailing_address=clean_text(row.get("mailing_address")) or "",
                )
            )
    return companies
