"""Verify DGM4-Complex dataset statistics against the paper.

Loads advanced_{train,val,test}_AM.json and cross-checks sample counts
against the values reported in the GraDual paper (IEEE Access 2026),
Tables 3 and 4.

Usage:
    python scripts/verify_statistics.py [--meta-dir PATH]

Exits 0 if every check passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from typing import Any

SPLITS = ("train", "val", "test")

# Paper Table 3 (full benchmark, after dedup)
PAPER_TOTAL = 276_931
PAPER_SPLIT_TOTAL_ONLY = True  # paper does not break down per split

# Paper Table 4 auxiliary occurrences
PAPER_AUX = {
    "FAM": 46_931,
    "TAM": 32_553,
    "NT": 22_155,
    "NT_CTRL": 13_847,
}

# Paper Table 3 category totals (Original + Added)
PAPER_TABLE3 = {
    "image_single": ("Image Single-level", 69_081, 0),
    "image_multi":  ("Image Multi-level",  0,     26_202),
    "text_single":  ("Text Single-level",  23_349, 9_886),
    "text_multi":   ("Text Multi-level",   0,     6_092),
    "mm_single":    ("Multimodal Single-level", 25_949, 0),
    "mm_multi":     ("Multimodal Multi-level",  0,     48_832),
    "control":      ("Control",            53_693, 13_847),
}


def load_splits(meta_dir: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for split in SPLITS:
        path = os.path.join(meta_dir, f"advanced_{split}_AM.json")
        if not os.path.exists(path):
            print(f"  [!] missing: {path}", file=sys.stderr)
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"  loaded {split:>5}: {len(data):>7,} samples  ({os.path.basename(path)})")
        items.extend(data)
    return items


def mark(ok: bool) -> str:
    return "\033[32m✓\033[0m" if ok else "\033[31m✗\033[0m"


def row(label: str, measured: int, expected: int, pct_of: int | None = None) -> bool:
    ok = measured == expected
    pct = f"  ({measured / pct_of * 100:5.2f}%)" if pct_of else ""
    print(f"  {mark(ok)} {label:<22} {measured:>8,}  "
          f"(paper: {expected:>8,}){pct}")
    return ok


def classify_auxiliary(item: dict[str, Any]) -> set[str]:
    """Return the set of auxiliary labels present in this sample.

    A single sample may carry multiple auxiliaries (FAM + TAM, etc.),
    matching paper Table 4's 'occurrences can co-occur' note.
    """
    labels: set[str] = set()
    fake_cls = item.get("fake_cls", "") or ""
    text_aug_cls = item.get("text_aug_cls")

    if item.get("AM") or "FAM" in fake_cls.split("&"):
        labels.add("FAM")
    if text_aug_cls == "TAM":
        labels.add("TAM")
    elif text_aug_cls == "NT":
        labels.add("NT")
    elif text_aug_cls == "NT_CTRL":
        labels.add("NT_CTRL")
    return labels


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--meta-dir",
        default=os.environ.get(
            "DGM4_COMPLEX_META",
            "/data/dataset/dataset/DGM4_extended/metadata",
        ),
        help="directory containing advanced_{train,val,test}_AM.json",
    )
    args = ap.parse_args()

    print(f"meta_dir: {args.meta_dir}")
    print()
    print("[1/3] Loading splits")
    items = load_splits(args.meta_dir)
    total = len(items)
    print()

    print("[2/3] Paper Table 3 — total samples")
    all_ok = True
    all_ok &= row("Total samples", total, PAPER_TOTAL)
    print()

    print("[3/3] Paper Table 4 — auxiliary occurrences")
    counts: Counter[str] = Counter()
    for it in items:
        for lab in classify_auxiliary(it):
            counts[lab] += 1

    for key in ("FAM", "TAM", "NT", "NT_CTRL"):
        all_ok &= row(key, counts[key], PAPER_AUX[key], pct_of=total)

    print()
    print("fake_cls distribution (top 15):")
    fc = Counter(it.get("fake_cls", "") for it in items)
    for k, v in fc.most_common(15):
        print(f"  {v:>7,}  {k}")

    print()
    if all_ok:
        print("\033[32mAll checks passed.\033[0m")
        return 0
    print("\033[31mSome checks failed — see rows marked ✗.\033[0m")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
