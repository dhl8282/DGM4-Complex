#!/usr/bin/env bash
# Build the five release archives listed in docs/full_dataset_access.md.
# Usage:
#   DGM4C_SRC=/data/dataset/dataset/DGM4_extended \
#   DGM4C_OUT=/data/cs_aica_backup/cs/dgm4-complex-bundles \
#   bash scripts/build_release_bundles.sh
#
# Each archive is created in $DGM4C_OUT with a manifest .sha256 next to it.
# Run this on the machine that hosts the full dataset.

set -euo pipefail

SRC="${DGM4C_SRC:-/data/dataset/dataset/DGM4_extended}"
OUT="${DGM4C_OUT:-/data/cs_aica_backup/cs/dgm4-complex-bundles}"

mkdir -p "$OUT"

if [[ ! -d "$SRC" ]]; then
    echo "error: DGM4C_SRC does not exist: $SRC" >&2
    exit 1
fi

echo "src: $SRC"
echo "out: $OUT"
echo

cd "$SRC"

# ------------------------------------------------------------------
# 1. metadata — small (~200 MB), gzipped
# ------------------------------------------------------------------
echo "[1/5] metadata -> dgm4-complex-metadata.tar.gz"
tar czf "$OUT/dgm4-complex-metadata.tar.gz" \
    metadata/advanced_train_AM.json \
    metadata/advanced_val_AM.json \
    metadata/advanced_test_AM.json \
    metadata/advanced_train_v3.json \
    metadata/advanced_val_v3.json \
    metadata/advanced_test_v3.json \
    metadata/advanced_train_FAM_pure.json \
    metadata/advanced_val_FAM_pure.json \
    metadata/advanced_test_FAM_pure.json \
    metadata/advanced_train_FAM_any.json \
    metadata/advanced_val_FAM_any.json \
    metadata/advanced_test_FAM_any.json \
    metadata/advanced_train_TAM_pure.json \
    metadata/advanced_val_TAM_pure.json \
    metadata/advanced_test_TAM_pure.json \
    metadata/advanced_train_TAM_any.json \
    metadata/advanced_val_TAM_any.json \
    metadata/advanced_test_TAM_any.json \
    metadata/advanced_train_NT_pure.json \
    metadata/advanced_val_NT_pure.json \
    metadata/advanced_test_NT_pure.json \
    metadata/advanced_train_NT_any.json \
    metadata/advanced_val_NT_any.json \
    metadata/advanced_test_NT_any.json \
    metadata/advanced_train_CTRL.json \
    metadata/advanced_val_CTRL.json \
    metadata/advanced_test_CTRL.json

# ------------------------------------------------------------------
# 2. FAM images (~5–7 GB) — store-only tar (already compressed jpgs)
# ------------------------------------------------------------------
echo "[2/5] FAM images -> dgm4-complex-fam-images.tar"
tar cf "$OUT/dgm4-complex-fam-images.tar" \
    manipulation/FaceAdapter/HFGI \
    manipulation/FaceAdapter/StyleCLIP \
    manipulation/FaceAdapter/infoswap \
    manipulation/FaceAdapter/simswap

# ------------------------------------------------------------------
# 3. FAM masks (~1 GB)
# ------------------------------------------------------------------
echo "[3/5] FAM masks -> dgm4-complex-fam-masks.tar"
tar cf "$OUT/dgm4-complex-fam-masks.tar" \
    manipulation/FaceAdapter/HFGI-mask \
    manipulation/FaceAdapter/StyleCLIP-mask \
    manipulation/FaceAdapter/infoswap-mask \
    manipulation/FaceAdapter/simswap-mask

# ------------------------------------------------------------------
# 4. Base manipulation masks (new SAM2 masks over base DGM4) (~1 GB)
# ------------------------------------------------------------------
echo "[4/5] base masks -> dgm4-complex-base-masks.tar"
tar cf "$OUT/dgm4-complex-base-masks.tar" \
    manipulation/HFGI-mask \
    manipulation/StyleCLIP-mask \
    manipulation/infoswap-mask \
    manipulation/simswap-mask

# ------------------------------------------------------------------
# 5. Origin images + articles (~20 GB)
# ------------------------------------------------------------------
echo "[5/5] origin (images + articles) -> dgm4-complex-origin.tar"
tar cf "$OUT/dgm4-complex-origin.tar" origin

# ------------------------------------------------------------------
# manifest
# ------------------------------------------------------------------
echo
echo "computing sha256 manifest"
cd "$OUT"
sha256sum dgm4-complex-*.tar* > dgm4-complex-SHA256SUMS.txt
ls -lh dgm4-complex-*.tar* dgm4-complex-SHA256SUMS.txt

echo
echo "done. upload these files to Dropbox / Google Drive:"
echo "  - dgm4-complex-metadata.tar.gz"
echo "  - dgm4-complex-fam-images.tar"
echo "  - dgm4-complex-fam-masks.tar"
echo "  - dgm4-complex-base-masks.tar"
echo "  - dgm4-complex-origin.tar"
echo "  - dgm4-complex-SHA256SUMS.txt"
echo
echo "then paste the share links into docs/full_dataset_access.md"
