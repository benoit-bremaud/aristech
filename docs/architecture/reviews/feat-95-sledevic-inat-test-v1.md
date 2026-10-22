# Local review — aristech (branch `feat/95-sledevic-inat-test-v1`)

- Date: 2026-10-22
- Scope: branch diff `main...HEAD`:
  - `scripts/inat_fetch.py`;
  - the `observation` group rule;
  - the `split_by_group` frozen-set fix;
  - registry outputs (licences, manifest, attribution, test-v1);
  - ADR-0023, spec, UML, gate;
  - QA tools.
- Checks run: design · docs · tests · security · correctness
- Verdict: **ship after the fixes below (applied)** · Must 1 (fixed) · Should 3 (fixed) · Nice 4

## Pre-merge gate

| Step | Result |
|---|---|
| 1 Tests | ✅ 239 unit passed, 2 skipped |
| 2 Coverage | new tests cover the fetch skip/limit, keyset paging, a failed photo and an API crash, plus the frozen-set split |
| 3 SonarQube | run on `main` after merge (Community Build analyses `main` only) |
| 4 Secrets | ✅ gitleaks clean · diff read: text registries only, no images, weights or third-party pixels committed |
| 5 QA pass | ✅ `docs/architecture/qa/2026-10-22-annotation-pipeline-pr3.md` |

## 🔴 Must Have (fixed)

- `scripts/inat_fetch.py` fetch `[correctness]`:
  - Problem: a failure mid-run left downloaded photos without attribution rows (AC10).
  - Fix: `try/finally` writes the attribution file, a failed photo download is logged and
    skipped, and images are written as `.part` and then moved with `os.replace`.

## 🟡 Should Have (fixed)

- Paging `[correctness]`:
  - Problem: `page` paging hits the API's 10,000-result cap, and pages shift.
  - Fix: keyset paging (`id_above`, `order_by=id asc`); the run stops on a short page.
- Tests `[tests]`: added a failed photo (the earlier row is kept), an API crash (rows survive),
  and a two-page run.
- `split_by_group` `[correctness]`:
  - Problem: a re-split with a frozen set grew test from 288 to 556.
  - Fix: once a set is frozen, the other groups go to train/validation only (two tests added).

## 🔵 Nice to Have

- LICENCES comment corrected (source id = directory name).
- `cc-by` may mean CC BY 3.0: recorded as a risk in ADR-0023.
- `_get` sleeps after the last request: harmless, kept.
- `scripts/` is not linted by CI (pre-existing; `prepare_*.py` fail ruff on `main`): follow-up.

## ⚪ Disagree / Intentional

- QA tools (`docs/architecture/qa/tools/`) are evidence scripts, not product code: they are
  untested and kept outside `src/`.
