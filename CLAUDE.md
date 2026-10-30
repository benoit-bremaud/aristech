# CLAUDE.md — aristech

Project-only rules. Global rules (`~/.claude/CLAUDE.md`, `~/.agent-rules/common.md`) apply
on top; this file only adds what is specific to aristech.

## What the project is

Real-time detection of the Asian hornet (*Vespa velutina*) in front of beehives. Python 3.11+,
Clean Architecture (`domain` → `application` → `infrastructure` / `interface`), plus
`evaluation/` (offline metrics, heavy imports lazy) and `datasets/` (stdlib dataset split
helper). First adapter: the VespAI YOLOv5 detector.
Scope, roadmap and milestones: `docs/INDEX.md`, `docs/ROADMAP.md`, `docs/requirements.md`.

## Working method (owner decision 2026-10-15)

aristech follows the full V-SEA / cubbies method; treat it as a large, complex project and never
skip a gate because a change looks small.

- **Design dossier first** — `docs/architecture/` (see its `README.md`). UML-first: model a
  feature in `docs/architecture/diagrams/<feature>/` and pass the conception gate
  (`docs/architecture/gates/`) before writing implementation code.
- **ADRs** — every structuring decision gets `docs/decisions/ADR-NNNN-<slug>.md` with the scored
  options (MCDA). Supersede an accepted ADR, never edit it.
- **One chat per brick**. Git workflow (branches, Conventional Commits): `docs/CONTRIBUTING.md`.
- **Pre-push review report** per branch in `docs/architecture/reviews/<branch>.md`; ask the owner
  per PR which review counts (review-local, Copilot, Codex).
- **Merge** only on `just gate` green + GitHub security checks green + every comment handled + explicit owner OK; then a
  `PROJECT_LOG.md` entry (agent-agnostic: no tool or reviewer names).

## Non-negotiables

- The dependency rule holds: `domain/` imports stdlib and `domain/` only, `application/` imports
  `domain/` only, heavy libraries (torch, cv2, yolov5) live in `infrastructure/` or behind a lazy
  import (`evaluation/runner.py`).
- A new port needs a present force (a second implementation, a test fake, an optional extra).
  No speculative ports.
- Heavy dependencies go in an optional extra (e.g. `vision`), never in the core
  `dependencies`.
- VespAI weights are CC BY-NC-SA: load them from a path, never commit or vendor them.
- Hand-written fakes at the ports; never mock the domain.

## Commands

No `python` on PATH: use the venv.

```bash
uv venv -p 3.11 .venv
uv pip install -e . --no-deps pytest pytest-cov pyyaml python-dotenv
mise install && mise x -- lefthook install
mise x -- just check        # L1: lint, mypy, typos, actionlint, zizmor, tests ≥ 80 %, semgrep, osv, gitleaks
mise x -- just gate         # L2 before merge: check + SonarQube quality gate
```

Local CI (ADR-0027): `just fast` runs on commit, `just check` on push; tools pinned in `mise.toml`
/ `mise.lock`. `make format` fixes the formatting.

Quality: `make sonar` (unit-test coverage + scan of the local SonarQube, key `aristech`) reads the
project token `project-aristech-local-2026` from `~/.config/sonar-tokens/aristech`, falling back
to `SONAR_TOKEN`; Community Build analyses `main` only. The project must grant Browse to
`sonar-users` for its results to be visible.
