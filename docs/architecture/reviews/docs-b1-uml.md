# Local review — aristech (branch diff main...docs/b1-uml)

- Date: 2026-10-16
- Commit: 78d3f63 (fixes below landed in the next commit)
- Scope: branch diff `main...HEAD` — `docs/architecture/diagrams/detection/01..04`,
  `docs/architecture/traceability/{matrix,README}.md`
- Checks run: docs · correctness (every arrow and signature checked against `src/aristech`; UML 2.5
  orthodoxy; all four diagrams rendered with mermaid-cli) (design · tests · security not
  applicable)
- Verdict: ship after fixes · Must 2 (fixed) · Should 4 (fixed) · Nice 1 (fixed)

## 🔴 Must Have

- `02-sequence-live-detection.md` `[correctness]` · `frames()` drawn as called per frame; the code
  calls it once and iterates (`detect_hornet_visual.py:42`) · fixed.
- `02-sequence-live-detection.md` `[correctness]` · video source creation (camera index vs path,
  `main.py:103-130`) missing · fixed.

## 🟡 Should Have

- `03-component.md` `[correctness]` · `operating_point → runner` arrow does not exist in code ·
  fixed: both depend on `metrics`.
- `03-component.md` `[correctness]` · missing `evaluation → domain` dependency · fixed.
- `04-class.md` `[correctness]` · `center` / `area` are read-only properties, not methods · fixed.
- `04-class.md` `[correctness]` · `Detection` drawn as depending on `Decision` · fixed: `«utility»
  decision` depends on both.

## 🔵 Nice to Have

- `02-sequence-live-detection.md` `[docs]` · ABSTAIN branch only in a note · fixed: shown as an
  unreachable `alt` branch.

## ⚪ Disagree / Intentional

- `04-class.md` `[docs]` · no state or data-flow diagram · no lifecycle and no personal data on this
  path (stated in the notes).
- Out of scope · French docstrings in `DetectHornetVisual` and the CLI · audit M9, docs brick.

## Per-dimension summary

- Docs: four diagrams + matrix, all paths exist · Correctness: 6 drawing errors fixed; the double
  filter (audit M3) confirmed at `vespai_detector.py:109` and `main.py:134,137`.
