# Full dataset access

This repository is a **review-grade preview**: it contains the
full metadata schema, a curated sample set, paper figures, and
reproduction scripts. The complete dataset is ≈ 18.8 GB on disk
(packaged as 5 tar archives) and is hosted on Google Drive.

## Download

All archives are hosted on Google Drive. Files are stored without
further compression so that download size matches on-disk size.

| Archive | Contents | Size | Download |
|---|---|---:|---|
| `dgm4-complex-metadata.tar.gz` | `train.json`, `val.json`, `test.json` (276,931 samples total) | **20 MB** | [Drive link](https://drive.google.com/open?id=1gsrfWZoH-d8S-PQeaIAFlUvIqfQ9oLng) |
| `dgm4-complex-fam-masks.tar` | SAM2 masks for the FAM (FaceAdapter) images | **385 MB** | [Drive link](https://drive.google.com/open?id=1Vw1g5K0moBRQCboLgvQLCAoY01NwGvHL) |
| `dgm4-complex-base-masks.tar` | SAM2 masks over the base DGM4 face manipulations (new in DGM4-Complex) | **630 MB** | [Drive link](https://drive.google.com/open?id=1n19jtJibrz3k-454K7Z3KKvsk_z3MSCx) |
| `dgm4-complex-fam-images.tar` | FAM (FaceAdapter diffusion) manipulated images, 4 base variants | **3.7 GB** | [Drive link](https://drive.google.com/open?id=1N31e6GjC-nX7PvoRNj-UOkfWzuepRpZX) |
| `dgm4-complex-origin.tar` | Clean origin images from Visual News + source articles | **14 GB** | [Drive link](https://drive.google.com/open?id=1bBY4BZV-eaDCRfhNT511q_hGw39IbVPu) |
| `dgm4-complex-SHA256SUMS.txt` | manifest — verify archive integrity | 466 B | [Drive link](https://drive.google.com/open?id=1kqArsQpkv9KNMG2o0oZzXLmF43s3bijl) |

### SHA256 manifest (for local verification)

```
fc233a5e842ae84e0909c5a48404a6ff037fcd821935141025ab2df5490bab66  dgm4-complex-base-masks.tar
1f89f971de65976d6515c3458c29d41e2b551bac0b5bd8372a870e69cf8a3fb2  dgm4-complex-fam-images.tar
2028c776db40e6f69cb9d400834177f9b59baa744d02270ab2e99b96ea4cecb1  dgm4-complex-fam-masks.tar
e9db736e921f0aa8f018f5e6dc4dee538d4fa7c65a40d6934c67edcb28706301  dgm4-complex-metadata.tar.gz
8fbda61c4e821bfd920142b5cfbaba93cdba729bf039170477044bd97d89d348  dgm4-complex-origin.tar
```

After downloading, verify with `sha256sum -c dgm4-complex-SHA256SUMS.txt`.

## Unpacking

All archives share a single top-level tree. Extract them into the
same root directory:

```bash
mkdir dgm4-complex
cd dgm4-complex
tar xzf /path/to/dgm4-complex-metadata.tar.gz
tar xf  /path/to/dgm4-complex-fam-images.tar
tar xf  /path/to/dgm4-complex-fam-masks.tar
tar xf  /path/to/dgm4-complex-base-masks.tar
tar xf  /path/to/dgm4-complex-origin.tar
```

Result:

```
dgm4-complex/
├── metadata/
│   ├── train.json                                   # 189,339 samples
│   ├── val.json                                     # 26,519 samples
│   └── test.json                                    # 61,073 samples
├── manipulation/
│   ├── {HFGI,StyleCLIP,infoswap,simswap}-mask/      # new SAM2 masks over DGM4 base
│   └── FaceAdapter/
│       ├── {HFGI,StyleCLIP,infoswap,simswap}/       # FAM images (diffusion)
│       └── {HFGI,StyleCLIP,infoswap,simswap}-mask/  # FAM SAM2 masks
└── origin/
    ├── bbc/ guardian/ usa_today/ washington_post/   # Visual News origin images
    └── <source>/articles/                           # source article texts
```

After unpacking, verify the counts match paper Table 3 / Table 4:

```bash
python /path/to/dgm4-complex/scripts/verify_statistics.py --meta-dir dgm4-complex/metadata
```

## What's NOT in these archives

The **base DGM4 face manipulation images**
(`manipulation/{HFGI,StyleCLIP,infoswap,simswap}/`, ≈ 6 GB) are
intentionally **not** redistributed. They are already provided by
the original DGM4 release:
<https://github.com/rshaojimmy/MultiModal-DeepFake>.
Our metadata references those files by path; simply place the DGM4
release under the same `dgm4-complex/` root and every relative
path resolves.

## License summary

- **Metadata, FAM images, SAM2 masks** — research use only,
  non-commercial. Inherits the DGM4 license.
- **Origin images, article texts** (`dgm4-complex-origin.tar`) —
  derivatives of
  [Visual News](https://github.com/FuxiaoLiu/VisualNews-Repository).
  Redistributed here for research reproduction of this work and
  must be used under Visual News's terms. If the upstream dataset
  updates its policy, access here will follow suit.
- **Base DGM4 images** — not included. Subject to the
  [DGM4 / MultiModal-DeepFake](https://github.com/rshaojimmy/MultiModal-DeepFake)
  license.
- **Code in this repository** — Apache-2.0.

By downloading any archive you agree to:
1. use the data for non-commercial research only;
2. cite the GraDual paper and the original DGM4 paper;
3. not redistribute the base DGM4 images;
4. respect the Visual News license when using origin images or articles;
5. make reasonable efforts to protect the privacy of individuals whose
   likenesses appear in the data.

## After paper acceptance

We will mirror the archives on a persistent public host (Zenodo or
Hugging Face Datasets) and add the mirror URLs to this file.
