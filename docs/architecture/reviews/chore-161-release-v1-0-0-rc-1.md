# Pre-push review — chore/161-release-v1-0-0-rc-1

Review of the diff against `dev` (issue #161) before the first push: release PR for `v1.0.0-rc.1`.

## Checks

- `just gate`: green (364 tests, SonarQube quality gate passed).
- Diff read in full: version bump, new `CHANGELOG.md`, new `.github/tag-protection.md`.

## Findings

| # | Priority | Finding | Resolution |
|---|---|---|---|
| 1 | Should | The tag uses the SemVer form, the package the PEP 440 form; a reader may see a mismatch | Stated at the top of `CHANGELOG.md` |
| 2 | Should | `tag-protection.md` must match the live ruleset | Checked against ruleset `protect-release-tags` (rules, bypass, target) |
| 3 | Nice | Test fixtures keep `software_version="0.1.0"` | Not changed: arbitrary fixture values, not the package version |

No Must Have finding. No QA pass on a running product: the diff changes no behaviour.
