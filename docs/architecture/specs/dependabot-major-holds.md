# Spec — Dependabot holds for the ADR-0012 majors (brick B7, follow-up)

> **Brick**: B7 follow-up · **Decision**: ADR-0012 (consequence: `numpy<2`, `opencv-python<5`) ·
> **Out of scope**: the numpy 2 / opencv 5 migration itself (future ADR)

## Need

ADR-0012 holds numpy below 2 and opencv-python below 5. Dependabot's weekly pip group still
proposes both majors (PR #75: numpy 1.26.4 → 2.2.6, opencv-python 4.9.0.80 → 5.0.0.93, plus pandas,
PyYAML, setuptools), which contradicts the accepted decision and would come back every week. The
maintainer wants Dependabot to keep proposing every other update, and those two majors only when a
new ADR lifts the hold.

## Actors

- **Maintainer** — triages Dependabot PRs and owns the ADRs.
- **Dependabot** — opens grouped version-update and security-update PRs.

## Main scenario

1. `.github/dependabot.yml` ignores `version-update:semver-major` for `numpy` and
   `opencv-python` in the pip ecosystem.
2. The next weekly run proposes the remaining pip updates (minors, patches, other majors) in one
   group PR, without the two held majors.
3. PR #75 is closed with a comment that points to ADR-0012 and this spec.

## Alternative scenarios

- **A1** A security advisory on numpy 1.x or opencv 4.x whose only fix is in the next major →
  the ignore also suppresses Dependabot's security PR, but the alert stays visible in the
  Dependabot alerts list; the maintainer then opens a new ADR (lift the hold) or accepts the alert
  with a reason.
- **A2** A new ADR adopts numpy 2 or opencv 5 → the matching ignore entry is removed in the same PR.

## Acceptance criteria

- **AC1** `.github/dependabot.yml` carries the two ignore entries with a comment citing ADR-0012;
  `actionlint` is not concerned (not a workflow), the YAML parses.
- **AC2** PR #75 is closed with a reason referring to ADR-0012.
- **AC3** CI green; gitleaks clean.

## Design impact

Repository configuration only; no code, no UML, no new ADR (this applies ADR-0012).
