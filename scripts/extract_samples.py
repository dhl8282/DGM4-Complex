"""Extract a small, balanced, review-friendly sample set from DGM4-Complex.

Produces:
  samples/images/...         copied images (origin, manipulations, FAM)
  samples/masks/...          matching binary masks
  samples/sample_metadata.json  list of sample entries (subset of full metadata)
  samples/README.md          short description

Two kinds of samples are included:
  1. Curated groups — full id-groups that show multi-level progression.
     Includes the exact sample shown in paper Figure 1 (id=1102361).
  2. Per-type singletons — 2 samples of each (manipulation_type x generator)
     pair, for the 4x4 grid figure.
"""

from __future__ import annotations

import json
import os
import random
import shutil
import sys
from collections import defaultdict
from typing import Any

META_DIR = "/data/dataset/dataset/DGM4_extended/metadata"
DATA_ROOT = "/data/dataset/dataset"
REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir))
SAMPLES_DIR = os.path.join(REPO_ROOT, "samples")

SEED = 2026
random.seed(SEED)

# Groups to include in full
CURATED_GROUPS = {
    1102361: "paper_figure1",        # exact Fig 1 (Martin Butler / Tanna / Venice)
    1150521: "progression_full",     # covers FAM+NT+TAM+FA+FS+orig
    # High-quality progression candidates (selected by face-area + resolution)
    151419:  "progression_cand_1",   # Reese Witherspoon / Sofia Vergara, 3500x3500
    1538785: "progression_cand_2",   # David Ellis, Swansea Crown Court
    1490349: "progression_cand_3",   # Cheshire Police e-fit
    1672250: "progression_cand_4",   # Karl Demetrius
    1642490: "progression_cand_5",   # Najib Razak
}

# Per-type singletons: (manipulation_type, generator) -> how many
GENERATORS = ["HFGI", "infoswap", "simswap", "StyleCLIP"]
PER_TYPE_K = 2


def load_all() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for split in ("train", "val", "test"):
        path = os.path.join(META_DIR, f"advanced_{split}_AM.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for d in data:
            d["_split"] = split
        items.extend(data)
    return items


def resolve(path: str) -> str:
    """Resolve a metadata-relative path to an absolute filesystem path."""
    if not path:
        return ""
    if path.startswith("/"):
        return path
    return os.path.join(DATA_ROOT, path)


def copy_one(src_rel: str) -> str | None:
    """Copy a file identified by its metadata-relative path into samples/.
    Returns the new metadata-relative path (same form, but under samples/)."""
    if not src_rel:
        return None
    src_abs = resolve(src_rel)
    if not os.path.exists(src_abs):
        print(f"  [missing] {src_abs}", file=sys.stderr)
        return None
    rel = src_rel
    if rel.startswith("DGM4_extended/"):
        rel = rel[len("DGM4_extended/"):]
    dst = os.path.join(SAMPLES_DIR, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not os.path.exists(dst):
        shutil.copy2(src_abs, dst)
    return rel


def gen_from_image_path(p: str) -> str | None:
    """Infer generator name from a manipulation path."""
    for g in GENERATORS:
        if f"/{g}/" in p or f"/{g}-" in p:
            return g
    return None


def manip_type(fake_cls: str) -> str | None:
    # primary face manip type for singleton grid
    base = fake_cls.split("&")
    if "FAM" in base:
        # FAM always combines with FA or FS; we want to surface FAM itself here
        return "FAM"
    if "face_swap" in base:
        return "FS"
    if "face_attribute" in base:
        return "FA"
    return None


def main() -> int:
    print(f"loading metadata from {META_DIR}")
    items = load_all()
    print(f"  total: {len(items):,} samples")

    collected: list[dict[str, Any]] = []
    seen_ids: set[int] = set()

    # 1. curated full groups
    print("\n[1] curated id-groups")
    by_id: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for d in items:
        if d.get("id") in CURATED_GROUPS:
            by_id[d["id"]].append(d)

    for gid, tag in CURATED_GROUPS.items():
        members = by_id.get(gid, [])
        print(f"  id={gid}  tag={tag}  n={len(members)}")
        for d in members:
            d = dict(d)
            d["_curated_tag"] = tag
            collected.append(d)
            seen_ids.add(id(d))

    # 2. per-type singletons for 4x4 grid
    print("\n[2] per-type singletons (2 per (type,generator))")
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for d in items:
        fc = d.get("fake_cls", "")
        mt = manip_type(fc)
        if mt is None:
            continue
        img = d.get("image", "")
        gen = gen_from_image_path(img)
        if gen is None:
            continue
        # prefer samples with binary_mask and bbox populated
        if not d.get("fake_image_box"):
            continue
        # keep it clean: skip if text augmented, we use these purely for image grid
        if d.get("text_aug_cls"):
            continue
        buckets[(mt, gen)].append(d)

    for mt in ("FA", "FS", "FAM"):
        for gen in GENERATORS:
            pool = buckets.get((mt, gen), [])
            random.shuffle(pool)
            picks = pool[:PER_TYPE_K]
            print(f"  {mt:>3}/{gen:<9} -> {len(picks)} picks "
                  f"(pool={len(pool)})")
            for d in picks:
                collected.append(dict(d, _curated_tag=f"grid_{mt}_{gen}"))

    print(f"\n[3] copying files — {len(collected)} samples")
    out_records: list[dict[str, Any]] = []
    copied = 0
    for d in collected:
        rec: dict[str, Any] = {}
        for k in (
            "id", "fake_cls", "text", "origin_text", "topic",
            "fake_image_box", "fake_text_pos", "mtcnn_boxes",
            "AM", "AM_mask_bbox", "text_aug_cls",
            "_split", "_curated_tag",
        ):
            if k in d:
                rec[k] = d[k]

        for key in ("image", "origin_image", "binary_mask", "AM_binary_mask"):
            src = d.get(key)
            if not src:
                continue
            new_rel = copy_one(src)
            if new_rel:
                rec[key] = new_rel
                copied += 1
        out_records.append(rec)

    meta_out = os.path.join(SAMPLES_DIR, "sample_metadata.json")
    with open(meta_out, "w", encoding="utf-8") as f:
        json.dump(out_records, f, indent=2, ensure_ascii=False)
    print(f"  wrote {meta_out}  ({len(out_records)} records, "
          f"{copied} files copied)")

    readme = os.path.join(SAMPLES_DIR, "README.md")
    with open(readme, "w", encoding="utf-8") as f:
        f.write(
            "# DGM4-Complex — sample set\n\n"
            "Small curated subset for reviewers and README figures.\n\n"
            f"- {len(out_records)} samples\n"
            f"- Includes the exact sample from paper Figure 1 "
            "(id=1102361, `paper_figure1`)\n"
            "- Full metadata is in `sample_metadata.json`\n\n"
            "For the full dataset (~37 GB, 276,931 samples) see "
            "`docs/full_dataset_access.md`.\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
