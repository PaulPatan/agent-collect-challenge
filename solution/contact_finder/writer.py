from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from .models import OutputRow

CSV_COLUMNS = [
    "company_name",
    "mailing_address",
    "contact_name",
    "contact_role",
    "contact_email_or_phone",
    "confidence_score",
    "source",
    "needs_human_review",
    "review_reason",
    "source_urls",
    "score_reasons",
]

def write_csv(rows: List[OutputRow], path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            d = asdict(row)
            d["needs_human_review"] = "true" if row.needs_human_review else "false"
            writer.writerow({k: d[k] for k in CSV_COLUMNS})

def write_json(rows: List[OutputRow], path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps([asdict(r) for r in rows], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
