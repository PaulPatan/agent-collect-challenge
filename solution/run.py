from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from contact_finder.config import (
    CONFIDENCE_THRESHOLD,
    DEFAULT_INPUT_CSV,
    DEFAULT_MOCKS_JSON,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SUPPRESSION,
)
from contact_finder.pipeline import run_from_files
from contact_finder.writer import write_csv, write_json

def _summary(rows) -> str:
    total = len(rows)
    emitted = [r for r in rows if not r.needs_human_review]
    review = [r for r in rows if r.needs_human_review]
    reason_counts = Counter(r.review_reason for r in review)
    lines = [
        f"Processed {total} companies (threshold = {CONFIDENCE_THRESHOLD}, precision-first).",
        f"  emitted (confident contact): {len(emitted)}",
        f"  needs_human_review:          {len(review)}",
        "  review reasons:",
    ]
    for reason, n in sorted(reason_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"    {reason:<20} {n}")
    if emitted:
        lines.append("  confident contacts:")
        for r in sorted(emitted, key=lambda r: -r.confidence_score):
            lines.append(
                f"    [{r.confidence_score:3d}] {r.company_name} -> "
                f"{r.contact_name} ({r.contact_role}) {r.contact_email_or_phone}"
            )
    return "\n".join(lines)

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Contact Finder slice (mocked providers).")
    parser.add_argument("--input", default=str(DEFAULT_INPUT_CSV), help="companies.csv path")
    parser.add_argument("--mocks", default=str(DEFAULT_MOCKS_JSON), help="enrichment_responses.json path")
    parser.add_argument("--suppression", default=str(DEFAULT_SUPPRESSION), help="Do-Not-Contact list path")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUTPUT_DIR), help="output directory")
    args = parser.parse_args(argv)

    rows = run_from_files(args.input, args.mocks, args.suppression)

    out_dir = Path(args.out_dir)
    write_csv(rows, out_dir / "contacts.csv")
    write_json(rows, out_dir / "contacts.json")

    print(_summary(rows))
    print(f"\nWrote {out_dir / 'contacts.csv'} and {out_dir / 'contacts.json'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
