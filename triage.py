#!/usr/bin/env python3
"""
Signal Triage Digest
--------------------
Reads raw customer/partner signals exported from Slack, keyword-filtered email,
and the Oracle PFR tracker, and turns them into ONE grouped digest you can scan
before a Monday partner sync.

Design decisions come straight from the IMPACT work:
  - Intent:   the expensive error is a MISS (a real blocker you never see).
  - Mental Model: the AI RETRIEVES, GROUPS, and FLAGS. It does NOT prioritize.
                  You keep urgency, escalation, and ownership.
  - Plumbing: manual file-drop trigger; a WIDE / high-recall filter.
  - Accuracy (the safety net): when the tool is UNSURE, it pushes the signal
                  TOWARD you, not away. Low-confidence items go in a REVIEW
                  section at the TOP of the digest, never hidden.
                  It also prints per-source coverage so an empty source
                  (e.g. a forgotten PFR export) is impossible to miss.

Everything here is plain Python standard library. No installs.

Usage:
    python triage.py --input ./sample_data --output digest.md
"""

import argparse
import csv
import glob
import os
import sys
from collections import defaultdict
from datetime import datetime

# ---------------------------------------------------------------------------
# Config: the vocabulary that decides how confident we are about a signal.
# WIDE / high-recall on purpose. Better to over-pull and let you skim than to
# silently drop a blocker. Edit these lists to tune what the tool catches.
# ---------------------------------------------------------------------------

# Strong intent words: someone is clearly asking for / blocked on something.
STRONG_KEYWORDS = [
    "feature request", "customer ask", "customer request", "blocker",
    "blocked", "escalation", "escalate", "sev1", "sev 1", "p1",
    "showstopper", "deal breaker", "cannot go live", "can't go live",
]

# Product areas we care about (also used to group the digest).
PRODUCT_AREAS = {
    "Observability": ["observability", "monitoring", "metrics", "logging", "logs", "telemetry", "dashboards"],
    "DR / Resiliency": ["disaster recovery", " dr ", "failover", "resiliency", "backup", "rpo", "rto"],
    "Networking": ["networking", "network", "vpc", "vcn", "connectivity", "peering", "latency", "dns"],
    "Database": ["database", "db ", "exadata", "rac", "adb", "autonomous", "patching", "upgrade"],
    "Partner / Ops": ["provisioning", "onboarding", "billing", "quota", "capacity", "region"],
}

# Softer hint words: something might be wrong, but intent is not explicit.
WEAK_KEYWORDS = [
    "gap", "missing", "not supported", "unsupported", "broken", "regression",
    "issue", "bug", "slow", "outage", "down", "fails", "failed", "cannot",
    "can't", "workaround", "concern", "risk", "unhappy", "frustrated",
]


def classify(text):
    """Return (confidence, area, matched_terms) for one signal.

    confidence is one of: "high", "review".
      - high   -> clear intent AND a known product area -> grouped in the digest.
      - review -> anything ambiguous (only a hint, OR no clear product area)
                  -> surfaced in the REVIEW section so a human looks.
    The bias is intentional: when in doubt, send it to REVIEW, never drop it.
    """
    t = " " + text.lower() + " "
    matched = []

    strong = [k for k in STRONG_KEYWORDS if k in t]
    weak = [k for k in WEAK_KEYWORDS if k in t]

    area = None
    for name, terms in PRODUCT_AREAS.items():
        if any(term in t for term in terms):
            area = name
            matched.extend([term.strip() for term in terms if term in t])
            break

    matched = strong + weak + matched

    # High confidence only when intent is explicit AND we can place it.
    if strong and area:
        return "high", area, matched
    # Everything else the tool is less sure about -> human looks.
    if strong or weak or area:
        return "review", area or "Unclassified", matched
    return None, None, []  # no signal at all -> not customer-relevant


def read_signals(input_dir):
    """Read every .csv in input_dir into a common shape.

    Tolerant of column names. Expected-ish columns: source, date, author, text.
    Falls back to joining all cells if there's no obvious text column.
    Returns (rows, coverage) where coverage counts rows per source file.
    """
    rows = []
    coverage = {}
    files = sorted(glob.glob(os.path.join(input_dir, "*.csv")))
    if not files:
        print(f"  ! No .csv files found in {input_dir}", file=sys.stderr)
    for path in files:
        source = os.path.splitext(os.path.basename(path))[0]
        count = 0
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for raw in reader:
                low = {(k or "").lower(): (v or "") for k, v in raw.items()}
                text = (low.get("text") or low.get("message") or low.get("body")
                        or low.get("summary") or low.get("description") or "")
                if not text:  # no obvious text column: join everything
                    text = " ".join(str(v) for v in raw.values())
                rows.append({
                    "source": low.get("source") or source,
                    "date": low.get("date") or low.get("created") or "",
                    "author": low.get("author") or low.get("from") or low.get("owner") or "",
                    "text": text.strip(),
                })
                count += 1
        coverage[source] = count
    return rows, coverage


def build_digest(rows, coverage, expected_sources=None):
    """Return the digest as a markdown string."""
    review = []                      # low-confidence -> surfaced at TOP
    grouped = defaultdict(list)      # high-confidence -> grouped by area
    dropped = 0                      # no signal detected

    for r in rows:
        conf, area, matched = classify(r["text"])
        if conf == "high":
            grouped[area].append((r, matched))
        elif conf == "review":
            review.append((r, area, matched))
        else:
            dropped += 1

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    out = []
    out.append(f"# Signal Triage Digest — {now}")
    out.append("")
    out.append("_Grouped, **not** prioritized. You decide urgency, escalation, and ownership._")
    out.append("")

    # --- Coverage report: catches the "a source came back empty" miss --------
    out.append("## Coverage check")
    out.append("")
    exp = expected_sources or list(coverage.keys())
    for s in exp:
        n = coverage.get(s, 0)
        flag = "  ⚠️ EMPTY — did this export run?" if n == 0 else ""
        out.append(f"- **{s}**: {n} rows{flag}")
    out.append(f"- _{len(rows)} signals read · {dropped} looked like noise and were set aside_")
    out.append("")

    # --- SAFETY NET: low-confidence at the TOP, never hidden -----------------
    out.append(f"## ⚠️ REVIEW FIRST — not sure, you look ({len(review)})")
    out.append("")
    out.append("_The tool wasn't confident about these. They're up top on purpose — "
               "your expensive error is a **miss**, so uncertain items get MORE of your "
               "attention, not less._")
    out.append("")
    if review:
        for r, area, matched in review:
            hint = f" · _hint: {', '.join(sorted(set(matched))[:4])}_" if matched else ""
            out.append(f"- **[{r['source']}]** {r['text']}  \n  "
                       f"_{r['author']} · {r['date']} · guessed area: {area}_{hint}")
    else:
        out.append("- _(nothing flagged for review this run)_")
    out.append("")

    # --- Confident, grouped signals ------------------------------------------
    out.append("## Grouped signals")
    out.append("")
    if grouped:
        for area in sorted(grouped.keys()):
            items = grouped[area]
            out.append(f"### {area} ({len(items)})")
            for r, matched in items:
                out.append(f"- **[{r['source']}]** {r['text']}  \n  "
                            f"_{r['author']} · {r['date']}_")
            out.append("")
    else:
        out.append("- _(no high-confidence signals this run)_")
        out.append("")

    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Turn raw signals into one triage digest.")
    ap.add_argument("--input", default="sample_data", help="folder of .csv exports")
    ap.add_argument("--output", default="digest.md", help="digest file to write")
    ap.add_argument("--expect", default="", help="comma-separated source names you EXPECT (for the empty-source check)")
    args = ap.parse_args()

    print(f"Reading signals from: {args.input}")
    rows, coverage = read_signals(args.input)
    expected = [s.strip() for s in args.expect.split(",") if s.strip()] or None
    digest = build_digest(rows, coverage, expected)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(digest)

    print(f"Wrote digest -> {args.output}")
    print("-" * 60)
    print(digest)


if __name__ == "__main__":
    main()
