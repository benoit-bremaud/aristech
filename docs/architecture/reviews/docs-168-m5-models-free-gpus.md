# Pre-push review — docs/168-m5-models-free-gpus

Pre-push review of the M5 models and free-GPU survey (issue #168), base `dev` (`feddaf8`), first
head `9f6ee7f`.

## Round 1 — adversarial review (findings)

Verdict: Must 4 · Should 11 · Nice 4 · Disagree 1. `just check` green.

| # | Level | Finding | Resolution |
|---|---|---|---|
| M1 | Must | Note rejected the Sledevič set ("Vilnius") already in use under CC BY 4.0 (ADR-0021) | Fixed: row "in use", Vilnius removed |
| M2 | Must | hornet-behavior v1 (in use, `test-v1`) treated as unverified, "≈ 1 k each" unsupported | Fixed: row split, in-use v1 vs badge-only others |
| M3 | Must | Objects365 caveat penalised B/C but not RF-DETR | Fixed: A licence 4; rerun → A 400, D 370; sensitivity now flips at Hailo 30 (stated) |
| M4 | Must | `references.md` / `state-of-the-art.md` RF-DETR rows still unqualified Apache-2.0 | Fixed: rows qualified (N/S/M/L only) |
| S1 | Should | Kaggle facts marked V while raw notes said unverified | Kept V: re-read on kaggle.com docs in a browser during this brick (30 h/week, 12 h, 20 GB); URLs cited |
| S2 | Should | V/E marks wrong or missing | Fixed: marks corrected, reading note added |
| S3 | Should | Hailo entry is `yolox_s_leaky`, not stock YOLOX-S | Fixed |
| S4 | Should | Hailo score 2 vs 1 unjustified among DETRs | Fixed: all DETR options 2 (DETR compiles in the Zoo), justified |
| S5 | Should | D2 ordering vs sensitivity, hidden weight changes | Fixed: full vectors shown, Kaggle-first reason stated |
| S6 | Should | iNaturalist counts are occurrences, fetch path is ADR-0023 | Fixed |
| S7 | Should | ADR-0019 register is per source, not per image | Fixed |
| S8 | Should | Exported YOLO view is symlinks | Fixed: `cp -rL` step in the run plan |
| S9 | Should | Review report missing | This file |
| S10 | Should | Zenodo row misplaced, YOLOX caveat, compute URLs missing in `references.md` | Fixed |
| S11 | Should | Cloud training is a structuring decision with no ADR | Fixed: stated as a plan; ADR required before the first cloud run (follow-up) |
| N1–N4 | Nice | YOLOX date, Zoo version, option letters, Ayoubkassi repo / Lightning card | Fixed |
| D1 | Disagree | No new ADR for D1 — confirmed (RF-DETR stays top, ADR-0022 stands) | — |

Out of scope (pre-existing): Hornet3000+ and `vespCV/vespcv` licence rows in `references.md` —
listed as a follow-up in the note.

## Round 2 — verification

See below.
