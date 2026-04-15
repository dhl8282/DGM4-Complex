# Full dataset access

This repository is a **review-grade preview**: it contains the
full metadata, a curated 27-sample subset, paper figures, and
reproduction scripts. The complete dataset is ≈ 37 GB and is **not**
hosted here.

## During the review period

The full DGM4-Complex dataset — FAM images, SAM2 masks, replaced
origin images, and per-split evaluation subsets — is hosted on
cloud storage (Dropbox / Google Drive) rather than in this Git
repository, because the full archive is ≈ 37 GB.

**Download links will be added here.** For now, please contact the
corresponding author (see paper front matter) to request access.
Include:

- your name and affiliation
- the intended use (research / reproduction / benchmarking)
- acknowledgement of the license terms below

IEEE Access reviewers can request access through the editor and
will receive a direct download link.

### Planned archive layout

The cloud bundle will ship as several independent archives so you
can download only the parts you need:

| Archive | Contents | Approx. size |
|---|---|---|
| `dgm4-complex-metadata.tar.gz` | all `advanced_*_AM.json` + ablation splits | ~200 MB |
| `dgm4-complex-fam-images.tar` | `manipulation/FaceAdapter/{HFGI,StyleCLIP,infoswap,simswap}/` | ~5–7 GB |
| `dgm4-complex-fam-masks.tar` | `manipulation/FaceAdapter/*-mask/` | ~1 GB |
| `dgm4-complex-base-masks.tar` | `manipulation/{HFGI,StyleCLIP,infoswap,simswap}-mask/` (new SAM2 masks over base DGM4) | ~1 GB |
| `dgm4-complex-origin.tar` | `origin/{bbc,guardian,usa_today,washington_post}/` + articles | ~20 GB |

The **base DGM4 face manipulations**
(`manipulation/{HFGI,StyleCLIP,infoswap,simswap}/`, ≈ 6 GB) are
intentionally **not** redistributed. See below.

## After acceptance

The download links in this document will be updated. We may also
mirror the bundle on a persistent host (Zenodo or Hugging Face
Datasets) for long-term archival.

## What you get

```
DGM4_extended/
├── metadata/
│   ├── advanced_{train,val,test}_AM.json        # full dataset — matches paper
│   ├── advanced_{train,val,test}_{FAM,TAM,NT}_{pure,any}.json  # ablation splits
│   └── advanced_{train,val,test}_CTRL.json      # NT_CTRL split
├── manipulation/
│   ├── {HFGI,StyleCLIP,infoswap,simswap}-mask/  # SAM2 masks (new in DGM4-Complex)
│   └── FaceAdapter/
│       ├── {HFGI,StyleCLIP,infoswap,simswap}/       # FAM images
│       └── {HFGI,StyleCLIP,infoswap,simswap}-mask/  # FAM SAM2 masks
└── origin/
    ├── bbc/ guardian/ usa_today/ washington_post/
    └── <source>/articles/                        # source article texts
```

The **base DGM4 face manipulations**
(`manipulation/{HFGI,StyleCLIP,infoswap,simswap}/`) are
intentionally **not** included. They are already provided by the
original DGM4 release:
<https://github.com/rshaojimmy/MultiModal-DeepFake>.
Our metadata references them by path; simply place the DGM4 release
under the same root and every relative path resolves.

## License summary

- **Metadata, FAM images, SAM2 masks** — Research use only,
  non-commercial. Inherits the DGM4 license.
- **Origin images, article texts** — Derivatives of
  [Visual News](https://github.com/FuxiaoLiu/VisualNews-Repository).
  Must be used under Visual News's terms.
- **Base DGM4 images** — Not included. Subject to the
  [DGM4 / MultiModal-DeepFake](https://github.com/rshaojimmy/MultiModal-DeepFake)
  license.
- **Code in this repository** — Apache-2.0.
