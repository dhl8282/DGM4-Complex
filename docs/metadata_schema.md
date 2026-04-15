# Metadata schema — `advanced_{train,val,test}_AM.json`

Each metadata file is a JSON array. One entry = one sample in the
DGM4-Complex benchmark. Fields follow the structure of the original
DGM4 metadata, extended with new fields for the added origin data,
segmentation masks, FaceAdapter (FAM) manipulations, and text
augmentations.

## Quick reference

| field | type | description |
|---|---|---|
| `id` | int | Sample ID. **Shared across all variants derived from the same origin image** (base face manip + FAM variants all carry the same id). |
| `image` | str | Path (relative to dataset root) of the displayed sample. Points to `origin/...` for `orig`/text-only samples, to `manipulation/<gen>/...` for base face manip, to `manipulation/FaceAdapter/<gen>/...` for FAM. |
| `text` | str | Caption shown with the image. May be augmented (TAM / NT) relative to `origin_text`. |
| `origin_text` | str | Ground-truth caption from Visual News, **unaugmented**. Use this with `text` to derive TAM/NT character-level diffs. |
| `origin_image` | str | Path to the clean Visual News origin image (relative to dataset root). |
| `article` | str | Path to the source news article (`.txt`) used to generate `origin_text`. |
| `topic` | str | Topic label from Visual News (e.g. `law_crime`, `arts_culture`, `media`, `politics`, ...). |
| `fake_cls` | str | Compound label joined with `&`. See [fake_cls grammar](#fake_cls-grammar). |
| `fake_image_box` | list[int] | `[x1, y1, x2, y2]` bounding box of the manipulated face region. Empty list when the sample is not visually manipulated. |
| `fake_text_pos` | list[int] | Token indices of manipulated tokens in `text` (token-level grounding label). Empty list when text is unaltered. |
| `mtcnn_boxes` | list[list[int]] | MTCNN-detected face boxes in `image` (all faces, not just manipulated ones). Up to K=2 faces per sample. |
| `binary_mask` | str\|null | Path to the SAM2 binary mask for the **base** (non-FAM) face manipulation, or `null` if not applicable. |
| `AM` | bool | `true` iff the sample belongs to the new FAM (FaceAdapter additional manipulation) split. |
| `AM_mask_bbox` | list[int] | Bounding box of the FAM-manipulated region. Empty list when `AM=false`. |
| `AM_binary_mask` | str\|null | Path to the SAM2 binary mask of the FAM region, or `null`. |
| `text_aug_cls` | str\|null | One of `"TAM"`, `"NT"`, `"NT_CTRL"`, or `null`. Indicates which text augmentation (if any) was applied. |

All path fields are stored with the legacy prefix `DGM4_extended/...`.
Resolve them by prepending your dataset root (see
`docs/full_dataset_access.md`).

## `fake_cls` grammar

`fake_cls` is a `&`-joined composition of **atoms** describing every
manipulation applied to the sample. Possible atoms:

| atom | meaning | source |
|---|---|---|
| `orig` | Pristine sample (no visual or textual manipulation). | baseline |
| `face_attribute` | Face attribute edit (HFGI or StyleCLIP). | DGM4 base |
| `face_swap` | Face swap (infoswap or simswap). | DGM4 base |
| `FAM` | Diffusion-based Face Additional Manipulation via FaceAdapter. Always combined with a base face manip. | **DGM4-Complex** |
| `text_attribute` | Attribute-style text edit. | DGM4 base |
| `text_swap` | Entity/phrase swap in text. | DGM4 base |
| `TAM` | Text Audience Mismatch — appends a "with N people in attendance"-style phrase whose number contradicts the image. | **DGM4-Complex** |
| `NT` | Nonspecific Tail — appends a semantically weakening phrase (e.g. "with limited context"). | **DGM4-Complex** |
| `NT_CTRL` | Control variant of NT appended to an otherwise pristine sample. Used to measure stylistic bias. | **DGM4-Complex** |

### Examples

```
orig                                   — pristine
face_attribute                         — single-level: HFGI/StyleCLIP edit
face_swap&text_swap                    — multi-level, single-modality per side
FAM&face_attribute                     — FAM stacked on HFGI/StyleCLIP
FAM&face_swap&text_swap                — cross-modal + FAM (multi-level)
FAM&face_attribute&text_swap&TAM       — 4-way multi-level
orig&TAM                               — image pristine, text augmented
orig&NT_CTRL                           — control for stylistic bias
```

See `scripts/verify_statistics.py` for the full top-15 `fake_cls`
distribution.

## Relationship to the base DGM4 metadata

DGM4-Complex **extends** the DGM4 JSON schema; it does not rewrite
existing entries. Reviewers already familiar with DGM4 can diff:

- added fields: `origin_text`, `article`, `topic`, `binary_mask`, `AM`,
  `AM_mask_bbox`, `AM_binary_mask`, `text_aug_cls`
- added `fake_cls` atoms: `FAM`, `TAM`, `NT`, `NT_CTRL`
- `origin_image` now points to the **Visual News replacement** (clean
  origin) rather than the grayscale/blurred origin of stock DGM4

## File listing

```
advanced_train_AM.json      189,339 samples
advanced_val_AM.json         26,519 samples
advanced_test_AM.json        61,073 samples
                            ─────────
                            276,931 total  (matches paper Table 3)
```

Evaluation subsets used in the paper's ablations are also provided:

```
advanced_{train,val,test}_FAM_pure.json   FAM-only subsets
advanced_{train,val,test}_FAM_any.json    samples containing FAM
advanced_{train,val,test}_TAM_pure.json
advanced_{train,val,test}_TAM_any.json
advanced_{train,val,test}_NT_pure.json
advanced_{train,val,test}_NT_any.json
advanced_{train,val,test}_CTRL.json       NT_CTRL control split
```
