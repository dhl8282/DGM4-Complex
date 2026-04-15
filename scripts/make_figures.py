"""Generate README figures from samples/sample_metadata.json.

Outputs:
  assets/hero_paper_fig1.png           paper Figure 1 reconstruction
  assets/grid_per_type.png             FA / FS / FAM  x  4 generators
  assets/multilevel_progression.png    single id, base -> full multi-level
  assets/text_manipulation_examples.png table of TAM / NT / NT_CTRL examples
  assets/stats_distribution.png        auxiliary type distribution bar chart
"""

from __future__ import annotations

import json
import os
import textwrap
from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import ConnectionPatch, FancyBboxPatch
from PIL import Image

REPO = "/data/cs_aica_backup/cs/anti-fakes/dgm4-complex"
SAMPLES = os.path.join(REPO, "samples")
ASSETS = os.path.join(REPO, "figures")
os.makedirs(ASSETS, exist_ok=True)

with open(os.path.join(SAMPLES, "sample_metadata.json"), "r", encoding="utf-8") as f:
    SAMPLE_META = json.load(f)


def load(rel: str) -> Image.Image:
    return Image.open(os.path.join(SAMPLES, rel)).convert("RGB")


def short_label(fake_cls: str) -> str:
    out = []
    for k in fake_cls.split("&"):
        out.append({
            "orig": "orig",
            "face_attribute": "FA",
            "face_swap": "FS",
            "FAM": "FAM",
            "text_attribute": "TA",
            "text_swap": "TS",
            "TAM": "TAM",
            "NT": "NT",
            "NT_CTRL": "NT_CTRL",
        }.get(k, k))
    return "+".join(out)


def draw_bbox(ax, bbox, color, label=None):
    if not bbox or len(bbox) != 4:
        return
    x1, y1, x2, y2 = bbox
    rect = patches.Rectangle(
        (x1, y1), x2 - x1, y2 - y1,
        linewidth=2.0, edgecolor=color, facecolor="none",
    )
    ax.add_patch(rect)
    if label:
        ax.text(x1, max(y1 - 4, 0), label,
                color="white", fontsize=7,
                bbox=dict(facecolor=color, edgecolor="none", pad=1.5))


# ----------------------------------------------------------------------
# 1. hero: paper Figure 1 style — one multi-level sample with callouts
# ----------------------------------------------------------------------
def _crop_bbox(img: Image.Image, bbox, pad: int = 8) -> Image.Image:
    x1, y1, x2, y2 = bbox
    W, H = img.size
    return img.crop((max(0, x1 - pad), max(0, y1 - pad),
                     min(W, x2 + pad), min(H, y2 + pad)))


def _draw_inline_colored(fig, ax, x0, y0, base, added,
                         base_color="#333", added_color="#c0392b",
                         fontsize=10.5, family="serif",
                         width_chars=95, line_h_axes=0.14):
    """Draw `base + added` as wrapped text on ax, coloring only `added` red.

    Uses Text.get_window_extent after a dummy draw to measure the end of the
    last black line, so the red suffix continues on the same line when there
    is room.
    """
    full = base + added
    wrapped = textwrap.wrap(full, width=width_chars,
                            break_long_words=False, drop_whitespace=False)
    # find the line containing the base/added boundary
    split_line = len(wrapped) - 1
    split_char = 0
    running = 0
    for i, line in enumerate(wrapped):
        if running + len(line) >= len(base):
            split_line = i
            split_char = len(base) - running
            break
        running += len(line)
        # account for whitespace textwrap collapses between lines
        while running < len(full) and full[running] == " ":
            running += 1

    y = y0
    for i, line in enumerate(wrapped):
        if i < split_line:
            ax.text(x0, y, line, color=base_color, fontsize=fontsize,
                    family=family, va="top")
        elif i == split_line:
            black_part = line[:split_char]
            red_part = line[split_char:]
            t_b = ax.text(x0, y, black_part, color=base_color,
                          fontsize=fontsize, family=family, va="top")
            if red_part:
                fig.canvas.draw()
                bb = t_b.get_window_extent().transformed(
                    ax.transData.inverted())
                ax.text(bb.x1, y, red_part, color=added_color,
                        fontsize=fontsize, family=family, va="top",
                        fontweight="bold")
        else:
            ax.text(x0, y, line, color=added_color, fontsize=fontsize,
                    family=family, va="top", fontweight="bold")
        y -= line_h_axes


def _style_crop_axes(ax, color: str, title: str):
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color(color)
        s.set_linewidth(3.0)
    ax.set_title(title, fontsize=10, color=color, fontweight="bold", pad=4)


def fig_hero():
    # pick the FAM+FS+TAM variant — it carries base FS, FAM, and TAM all at once
    cand = [d for d in SAMPLE_META
            if d.get("_curated_tag") == "paper_figure1"
            and d.get("AM")
            and "face_swap" in d["fake_cls"]]
    if not cand:
        print("  no FAM+FS paper_figure1 sample"); return
    d = cand[0]

    manip = load(d["image"])
    origin = load(d["origin_image"])
    fs_bbox = d["fake_image_box"]   # GAN / base face swap region
    fam_bbox = d["AM_mask_bbox"]    # Diffusion / FAM region

    orig_fs   = _crop_bbox(origin, fs_bbox)
    manip_fs  = _crop_bbox(manip,  fs_bbox)
    orig_fam  = _crop_bbox(origin, fam_bbox)
    manip_fam = _crop_bbox(manip,  fam_bbox)

    FS_COLOR  = "#e74c3c"   # GAN / base — red
    FAM_COLOR = "#1abc9c"   # Diffusion / FAM — teal

    fig = plt.figure(figsize=(16, 12.5))
    gs = fig.add_gridspec(
        3, 5,
        height_ratios=[2.4, 2.4, 1.9],
        width_ratios=[0.9, 0.9, 0.25, 2.6, 0.08],
        hspace=0.38, wspace=0.22,
        left=0.04, right=0.99, top=0.93, bottom=0.03,
    )

    # --- main manipulated image spans top 2 rows, right column ---
    ax_main = fig.add_subplot(gs[:2, 3])
    ax_main.imshow(manip)
    ax_main.set_xticks([]); ax_main.set_yticks([])
    draw_bbox(ax_main, fam_bbox, FAM_COLOR, "Diffusion (FAM)")
    draw_bbox(ax_main, fs_bbox,  FS_COLOR,  "GAN (FS)")
    ax_main.set_title(
        f"Multi-level image manipulation  —  {d['fake_cls']}",
        fontsize=12, fontweight="bold", pad=8,
    )

    # --- crops on the left: row 0 = FAM (before/after), row 1 = FS ---
    ax_ofam = fig.add_subplot(gs[0, 0])
    ax_ofam.imshow(orig_fam)
    _style_crop_axes(ax_ofam, FAM_COLOR, "origin")

    ax_mfam = fig.add_subplot(gs[0, 1])
    ax_mfam.imshow(manip_fam)
    _style_crop_axes(ax_mfam, FAM_COLOR, "diffusion result")

    ax_ofs = fig.add_subplot(gs[1, 0])
    ax_ofs.imshow(orig_fs)
    _style_crop_axes(ax_ofs, FS_COLOR, "origin")

    ax_mfs = fig.add_subplot(gs[1, 1])
    ax_mfs.imshow(manip_fs)
    _style_crop_axes(ax_mfs, FS_COLOR, "GAN result")

    # --- arrow from each "result" crop into the corresponding bbox in main ---
    def _arrow(ax_src, bbox_main, color):
        fx1, fy1, fx2, fy2 = bbox_main
        ix = (fx1 + fx2) / 2
        iy = (fy1 + fy2) / 2
        con = ConnectionPatch(
            xyA=(manip_fam.size[0] if ax_src in (ax_mfam,) else manip_fs.size[0],
                 (manip_fam.size[1] if ax_src in (ax_mfam,) else manip_fs.size[1]) / 2),
            coordsA=ax_src.transData,
            xyB=(ix, iy),
            coordsB=ax_main.transData,
            arrowstyle="->", color=color, lw=2.2,
            shrinkA=2, shrinkB=6, mutation_scale=18,
        )
        fig.add_artist(con)

    _arrow(ax_mfam, fam_bbox, FAM_COLOR)
    _arrow(ax_mfs,  fs_bbox,  FS_COLOR)

    # --- small legend-ish label between crop and result (→ "Base / FAM" badges) ---
    fig.text(0.013, 0.72, "FAM\npipeline",
             fontsize=10, color=FAM_COLOR, fontweight="bold",
             ha="left", va="center",
             bbox=dict(facecolor="white", edgecolor=FAM_COLOR, boxstyle="round,pad=0.35"))
    fig.text(0.013, 0.45, "GAN\npipeline",
             fontsize=10, color=FS_COLOR, fontweight="bold",
             ha="left", va="center",
             bbox=dict(facecolor="white", edgecolor=FS_COLOR, boxstyle="round,pad=0.35"))

    # --- text panel spanning full width at the bottom ---
    ax_text = fig.add_subplot(gs[2, :])
    ax_text.axis("off")
    ax_text.set_xlim(0, 1); ax_text.set_ylim(0, 1)

    ot = d.get("origin_text") or ""
    mt = d.get("text") or ""
    TAM_COLOR = "#c0392b"

    ax_text.text(0.01, 0.93, "Cross-modal text manipulation  (TAM)",
                 fontsize=12, fontweight="bold", color=TAM_COLOR, va="top")
    ax_text.text(0.01, 0.70, "Base text:", fontsize=11,
                 fontweight="bold", color="#2c3e50", va="top")
    ax_text.text(0.12, 0.70, textwrap.fill(ot, width=95),
                 fontsize=10.5, color="#333", va="top", family="serif")
    ax_text.text(0.01, 0.32, "TAM text:", fontsize=11,
                 fontweight="bold", color=TAM_COLOR, va="top")

    _draw_inline_colored(
        fig, ax_text, 0.12, 0.32,
        base=ot, added=mt[len(ot):],
        base_color="#333", added_color=TAM_COLOR,
        fontsize=10.5, family="serif", width_chars=95,
        line_h_axes=0.14,
    )

    fig.suptitle(
        f"DGM4-Complex — multi-level manipulation example   "
        f"(id={d['id']}, {d.get('_split')} split)",
        fontsize=14, fontweight="bold", y=0.985,
    )

    # statistics footer inside the figure so it works as a stand-alone
    # dataset-overview image for the README
    fig.text(
        0.5, 0.005,
        "DGM4-Complex   ·   276,931 samples   ·   "
        "FAM 46,931 (16.95%)   ·   TAM 32,553 (11.75%)   ·   "
        "NT 22,155 (8.00%)   ·   NT_CTRL 13,847 (5.00%)",
        ha="center", fontsize=9.5, color="#2c3e50", fontweight="bold",
        bbox=dict(facecolor="#ecf0f1", edgecolor="#bdc3c7",
                  boxstyle="round,pad=0.45"),
    )

    # dataset_overview.png is the paper's own Figure 1 (copied in manually).
    # This script only writes a supplementary hero under a different name.
    out = os.path.join(ASSETS, "multilevel_example.png")
    plt.savefig(out, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  wrote {out}")


# ----------------------------------------------------------------------
# 2. 2x4 grid:
#    Row 1 — base (DGM4): four GAN-based face manipulations
#            FA: HFGI, StyleCLIP | FS: infoswap, simswap
#    Row 2 — DGM4-Complex: FaceAdapter diffusion stacked on each base
# ----------------------------------------------------------------------
def fig_grid():
    picks: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for d in SAMPLE_META:
        tag = d.get("_curated_tag", "")
        if not tag.startswith("grid_"):
            continue
        _, mt, gen = tag.split("_", 2)
        picks[(mt, gen)].append(d)

    row1 = [("FA", "HFGI"), ("FA", "StyleCLIP"),
            ("FS", "infoswap"), ("FS", "simswap")]
    row2 = [("FAM", "HFGI"), ("FAM", "StyleCLIP"),
            ("FAM", "infoswap"), ("FAM", "simswap")]

    base_titles = {
        ("FA", "HFGI"):      ("GAN · face attribute", "HFGI"),
        ("FA", "StyleCLIP"): ("GAN · face attribute", "StyleCLIP"),
        ("FS", "infoswap"):  ("GAN · face swap",      "infoswap"),
        ("FS", "simswap"):   ("GAN · face swap",      "simswap"),
    }

    fig, axes = plt.subplots(2, 4, figsize=(15, 8.4))
    for c, key in enumerate(row1):
        ax = axes[0, c]
        ax.set_xticks([]); ax.set_yticks([])
        pool = picks.get(key, [])
        if pool:
            d = pool[0]
            ax.imshow(load(d["image"]))
            bb = d.get("fake_image_box") or []
            if bb:
                draw_bbox(ax, bb, "#e74c3c")
        method, base = base_titles[key]
        ax.set_title(f"{method}\n{base}", fontsize=10,
                     fontweight="bold", color="#2c3e50")

    for c, key in enumerate(row2):
        ax = axes[1, c]
        ax.set_xticks([]); ax.set_yticks([])
        pool = picks.get(key, [])
        if pool:
            d = pool[0]
            ax.imshow(load(d["image"]))
            bb = d.get("fake_image_box") or []
            if bb:
                draw_bbox(ax, bb, "#e74c3c")
            ab = d.get("AM_mask_bbox") or []
            if ab:
                draw_bbox(ax, ab, "#1abc9c")
        base = key[1]
        ax.set_title(f"Diffusion · FaceAdapter\nover {base} base",
                     fontsize=10, fontweight="bold", color="#1abc9c")

    axes[0, 0].set_ylabel("Base\n(DGM4)",
                          fontsize=12, fontweight="bold",
                          rotation=0, labelpad=38, va="center",
                          color="#2c3e50")
    axes[1, 0].set_ylabel("DGM4-Complex\n(FAM)",
                          fontsize=12, fontweight="bold",
                          rotation=0, labelpad=38, va="center",
                          color="#1abc9c")

    fig.suptitle(
        "Face manipulation coverage  —  "
        "Base (DGM4, GAN) vs FAM (DGM4-Complex, Diffusion)",
        fontsize=13, fontweight="bold", y=0.995,
    )
    fig.text(
        0.5, 0.01,
        "Row 2 samples are all produced by the same diffusion-based "
        "FaceAdapter pipeline; the base name (HFGI / StyleCLIP / "
        "infoswap / simswap) only indicates which DGM4 image the FAM "
        "was stacked on.",
        ha="center", fontsize=8.5, style="italic", color="#555",
    )
    plt.tight_layout(rect=[0, 0.03, 1, 0.98])
    out = os.path.join(ASSETS, "grid_per_type.png")
    plt.savefig(out, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  wrote {out}")


# ----------------------------------------------------------------------
# 3. multi-level progression — one figure per candidate group
# ----------------------------------------------------------------------
def _progression_complexity(d):
    fc = d["fake_cls"]
    score = 0
    if "face_attribute" in fc: score += 1
    if "face_swap" in fc: score += 1
    if "FAM" in fc: score += 2
    if "text_swap" in fc: score += 1
    if "text_attribute" in fc: score += 1
    if d.get("text_aug_cls") in ("TAM", "NT"): score += 1
    return score


def _render_progression(group, tag, out_name):
    group = sorted(group, key=_progression_complexity)[:6]
    n = len(group)
    if n == 0:
        return
    cols = 3
    img_rows = (n + cols - 1) // cols

    FS_COLOR  = "#e74c3c"
    FAM_COLOR = "#1abc9c"
    TAM_COLOR = "#8e44ad"     # purple for text augmentation

    # gridspec: alternating image-row / caption-row
    height_ratios = []
    for _ in range(img_rows):
        height_ratios += [4.0, 1.4]
    fig_w = 5.2 * cols
    fig_h = 1.3 + sum(height_ratios) * 1.05
    fig = plt.figure(figsize=(fig_w, fig_h))
    gs = fig.add_gridspec(
        img_rows * 2, cols,
        height_ratios=height_ratios,
        hspace=0.22, wspace=0.12,
        left=0.03, right=0.98, top=0.94, bottom=0.03,
    )

    for i in range(n):
        r = i // cols
        c = i % cols
        ax_img = fig.add_subplot(gs[r * 2,     c])
        ax_cap = fig.add_subplot(gs[r * 2 + 1, c])

        d = group[i]
        img = load(d["image"])
        ax_img.imshow(img)
        ax_img.set_xticks([]); ax_img.set_yticks([])

        fc_has_base = ("face_swap" in d["fake_cls"]
                       or "face_attribute" in d["fake_cls"])
        bb = d.get("fake_image_box") or []
        if bb and fc_has_base:
            draw_bbox(ax_img, bb, FS_COLOR)
        ab = d.get("AM_mask_bbox") or []
        if ab:
            draw_bbox(ax_img, ab, FAM_COLOR)

        title = short_label(d["fake_cls"])
        tac = d.get("text_aug_cls")
        if tac and tac not in title:
            title = f"{title} · {tac}"
        is_multi = "FAM" in d["fake_cls"]
        ax_img.set_title(title, fontsize=11,
                         fontweight="bold",
                         color=TAM_COLOR if is_multi else "#2c3e50")

        # caption axes — fill with light background, inline-colored text
        ax_cap.set_xlim(0, 1); ax_cap.set_ylim(0, 1)
        ax_cap.set_xticks([]); ax_cap.set_yticks([])
        for s in ax_cap.spines.values():
            s.set_color("#dddddd")
            s.set_linewidth(0.8)
        ax_cap.set_facecolor("#f8f9fa")

        ot = d.get("origin_text") or ""
        mt = d.get("text") or ""
        added = mt[len(ot):] if mt.startswith(ot) else ""
        base_part = mt[:len(mt) - len(added)] if added else mt

        _draw_inline_colored(
            fig, ax_cap, 0.04, 0.92,
            base=base_part, added=added,
            base_color="#333", added_color=TAM_COLOR,
            fontsize=8.5, family="serif",
            width_chars=60, line_h_axes=0.22,
        )

    fig.suptitle(
        f"Candidate progression — id={group[0]['id']}  "
        f"({group[0].get('_split')} split, tag={tag})",
        fontsize=13, fontweight="bold", y=0.985,
    )
    out = os.path.join(ASSETS, out_name)
    plt.savefig(out, dpi=120, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  wrote {out}  (n={n})")


def fig_progression():
    # Original progression_full (kept for backward compat)
    grp = [d for d in SAMPLE_META
           if d.get("_curated_tag") == "progression_full"]
    if grp:
        _render_progression(grp, "progression_full", "multilevel_progression.png")

    # Candidate alternatives
    by_tag = defaultdict(list)
    for d in SAMPLE_META:
        tag = d.get("_curated_tag", "")
        if tag.startswith("progression_cand_"):
            by_tag[tag].append(d)
    for tag in sorted(by_tag):
        idx = tag.replace("progression_cand_", "")
        _render_progression(
            by_tag[tag], tag,
            f"progression_candidate_{idx}.png",
        )


# ----------------------------------------------------------------------
# 4. text manipulation examples table
# ----------------------------------------------------------------------
def fig_text_examples():
    # pull diverse TAM / NT / NT_CTRL examples directly from full val metadata
    META_DIR = "/data/dataset/dataset/DGM4_extended/metadata"
    with open(os.path.join(META_DIR, "advanced_val_AM.json"),
              "r", encoding="utf-8") as f:
        full = json.load(f)
    want = {"TAM": 2, "NT": 2, "NT_CTRL": 2}
    got: dict[str, list] = {k: [] for k in want}
    for d in full:
        tac = d.get("text_aug_cls")
        if not tac or tac not in want:
            continue
        if len(got[tac]) >= want[tac]:
            continue
        ot = d.get("origin_text") or ""
        t = d.get("text") or ""
        if not ot or ot == t:
            continue
        if len(ot) > 95 or len(t) > 110:
            continue
        got[tac].append((tac, ot, t))
        if all(len(got[k]) >= want[k] for k in want):
            break

    rows = got["TAM"] + got["NT"] + got["NT_CTRL"]
    fig_h = 1.3 + 1.15 * len(rows)
    fig, ax = plt.subplots(figsize=(14, fig_h))
    ax.axis("off")
    table_data = [["Type", "Base text", "Manipulated text"]]
    for tac, ot, t in rows:
        ot_w = textwrap.fill(ot, 55)
        t_w = textwrap.fill(t, 55)
        table_data.append([tac, ot_w, t_w])
    table = ax.table(
        cellText=table_data, loc="center",
        cellLoc="left", colWidths=[0.10, 0.45, 0.45],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.4)
    type_colors = {"TAM": "#3498db", "NT": "#2ecc71", "NT_CTRL": "#95a5a6"}
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#dddddd")
        if r == 0:
            cell.set_facecolor("#2c3e50")
            cell.set_text_props(color="white", fontweight="bold")
        else:
            cell.set_facecolor("#fafbfc" if r % 2 else "white")
            if c == 0:
                label = table_data[r][0]
                cell.set_facecolor(type_colors.get(label, "#888"))
                cell.set_text_props(color="white", fontweight="bold")
    fig.suptitle("Text augmentation examples — TAM / NT / NT_CTRL",
                 fontsize=13, fontweight="bold", y=0.99)
    plt.tight_layout()
    out = os.path.join(ASSETS, "text_manipulation_examples.png")
    plt.savefig(out, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  wrote {out}  ({len(rows)} rows)")


# ----------------------------------------------------------------------
# 5. statistics distribution bar chart (from paper Table 4)
# ----------------------------------------------------------------------
def fig_stats():
    labels = ["FAM", "TAM", "NT", "NT_CTRL"]
    # measured values, authoritative (matches verify_statistics.py)
    counts = [46_931, 32_553, 22_155, 13_847]
    total = 276_931
    pct = [c / total * 100 for c in counts]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#95a5a6"]
    bars = ax.bar(labels, counts, color=colors)
    for b, c, p in zip(bars, counts, pct):
        ax.text(b.get_x() + b.get_width() / 2,
                b.get_height() + 500,
                f"{c:,}\n({p:.2f}%)",
                ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_ylabel("# occurrences")
    ax.set_title("DGM4-Complex auxiliary manipulation distribution  "
                 f"(total {total:,})",
                 fontsize=12, fontweight="bold")
    ax.set_ylim(0, max(counts) * 1.18)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    plt.tight_layout()
    out = os.path.join(ASSETS, "stats_distribution.png")
    plt.savefig(out, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  wrote {out}")


def main():
    print("generating figures ->", ASSETS)
    fig_hero()
    fig_grid()
    fig_progression()
    fig_text_examples()
    fig_stats()


if __name__ == "__main__":
    main()
