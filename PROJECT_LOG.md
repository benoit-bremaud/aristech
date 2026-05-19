# Project Log — aristech

Chronological operational logbook for the aristech project. Complements `git log` (per-commit detail) and `CHANGELOG.md` (published versions) with the human context — reviews, decisions, deferred work — that those two cannot capture.

One entry per merged PR, tag, release, or significant decision. Entries are appended in chronological order (oldest first).

---

## 2026-05-19

First entry. Retroactive audit scope: repo inception through PR #1 merge.

- **PR #1 merged** (`f5cc31c`) — `refactor: Clean Architecture migration + packaging + repo cleanup`. Branch `refactor/clean-architecture`, 97 files changed (+1622 / -963), merged 04:38 CEST. Complete refactor of the legacy flat layout into a Clean Architecture src-layout with PEP 621 packaging, strict quality tooling, and an 80 MB repo slim-down. Delivered in 11 commits over a single overnight session, then 3 review-cycle passes before merge.

  - **Legacy cleanup** (`cf5556a`) — removed 23 empty scaffolding stubs (`src/coil_gun_control.py`, `src/hornet_detection.py`, `src/modules/*`) and broken tests inherited from the original flat layout.
  - **src-layout adoption** (`26f7fa2`) — moved `src/model_training/` under `src/aristech/training/`, extracted shared `distribute_files()` helper between `distribute_images.py` and `distribute_videos.py`, reorganised tests into `tests/unit/`, `tests/integration/`, `tests/e2e/`.
  - **Domain and application layers** (`6f0607b`) — introduced frozen-dataclass entities (`Species`, `Detection`, `Target`, `Media`, `Geometry`), 8 `Protocol` ports (`VideoSource`, `AudioSource`, `HornetDetector`, `SoundClassifier`, `DistanceSensor`, `Actuator`, `Notifier`, `Clock`), the `DetectHornetVisual` use case, and the `aristech` CLI entry point (composition root). 7 unit tests added, all green in under 0.1 s with no hardware required.
  - **Packaging modernisation** (`f4531c7`) — replaced `setup.py` with `pyproject.toml` (PEP 621), added `ruff`, `mypy --strict`, `pre-commit`, `Makefile`, and GitHub Actions CI workflow.
  - **Repo slim-down** (`9b01216`) — removed ~80 MB of tracked binaries: two duplicated model files (`hornet_recognition_model.h5`, `model.keras`, ~40 MB each) and the obsolete `update_requirements.py`. Working tree dropped from ~80 MB to 504 KB. Note: `.git/` still holds the blobs and stays around 61 MB until the `git filter-repo` procedure documented in `docs/MAINTENANCE.md` is executed.
  - **Documentation alignment** (`6c3455d`) — rewrote `README.md`, `docs/INSTALL.md`, `docs/architecture.md` to match the new layout; added `docs/MAINTENANCE.md` with the post-merge `git filter-repo` procedure.
  - **Final cleanup** (`b9304d9`) — dropped a dangling `tests/utils/__init__.py` left over from the legacy test tree.

- **Review cycle** — three corrective passes on PR #1 before merge:
  - `d65e37c` — critical findings: tightened `pyproject.toml` metadata, fixed argument handling in `DetectHornetVisual`, hardened CLI entry point, expanded use case test coverage.
  - `388c607` — polish findings: `.env.example` placeholders, CI workflow tweak, markdownlint config tightening, `distribute_videos.py` clarification, added `tests/e2e/README.md` and package marker.
  - `43e2b60` — fixed French accent regressions in the four package-level docstrings (`application`, `infrastructure`, `interface`, `training`).

- **Decisions**:
  - `clean-architecture-adoption` — adopted Bob Martin's Clean Architecture with src-layout and `Protocol` ports (DIP). Rejected alternative: keep the flat `src/<module>.py` layout. Rationale: the legacy layout coupled hardware concerns (GPIO, OpenCV, audio capture) directly to detection logic, blocking unit testing without hardware. Ports let the domain and use cases run in pure Python with fakes.
  - `packaging-pep621` — moved from `setup.py` to `pyproject.toml`. Rejected alternative: `setup.cfg`. Rationale: PEP 621 is now the canonical static metadata format; aligns with the `ruff` / `mypy` ecosystem which reads `pyproject.toml` natively.
  - `models-out-of-tree` — `.h5` / `.keras` model artefacts removed from version control. Redistribution channel **not yet chosen** (candidates: GitHub Releases, HuggingFace Hub, S3). Decision deferred until the next training pipeline run produces a canonical artefact to publish.
  - `neutralize-target-deferred` — the `NeutralizeTarget` use case is intentionally not implemented. It is gated on three open product questions: lethality (coil-gun vs non-lethal vs alert-only), multi-modal fusion (vision AND audio concordant vs either-or), and fail-safe default (`dry-run` by default, live fire behind explicit flag). See the "Open decisions" section of `docs/architecture.md` (currently authored in French under the heading "Décisions ouvertes", which is also the live anchor).

- **Deferred technical debt** (post-merge, not yet executed):
  - Run `git filter-repo` per `docs/MAINTENANCE.md` to purge the model blobs from history (expected `.git/` reduction: 61 MB → ~1 MB). History-rewriting operation; requires coordination with any other collaborator or clone of the repository before execution.
  - Regenerate `requirements.txt` on the deployment platform via `make lock`. The current lockfile was produced on Linux with CUDA-specific wheels and is not portable.
  - Delete the local `refactor/clean-architecture` branch and run `git remote prune origin` per the global post-merge cleanup workflow.

- **Layer status after PR #1**:
  - `domain/` — populated, frozen dataclasses, no I/O.
  - `application/` — 8 ports defined, 1 use case (`DetectHornetVisual`) implemented. `DetectHornetAudio` and a multi-modal `DetectHornet` are not yet started.
  - `infrastructure/` — empty (`__init__.py` only). No concrete adapter wired yet (OpenCV, Keras inference, GPIO, audio capture, MQTT notifier).
  - `interface/cli/` — minimal `aristech` entry point in place; not yet wired to real adapters.

- **PR #2 merged** (`2a5f5a7`) — `docs: initialize PROJECT_LOG.md with retrospective entry for PR #1`. Branch `docs/project-log-init`, single file added (+43 lines), squash-merged at 13:37 UTC. Bootstraps this logbook with the retroactive audit entry above.

  - **Review cycle** — single Copilot pass on the original PR branch raised two Should-Have findings, both addressed in a follow-up commit before merge (intermediate PR-branch SHAs are not durable after squash-merge; see the PR conversation at <https://github.com/benoit-bremaud/aristech/pull/2> for the inline review threads):
    - English-only consistency: the reference to `docs/architecture.md` mentioned the French heading `Décisions ouvertes`; reframed in English while keeping the French anchor visible to preserve the link target (the heading itself stays in French until `docs/architecture.md` is translated).
    - Durability of phrasing: replaced the local-perspective wording "outside this machine" with "any other collaborator or clone of the repository" so the guidance reads correctly from any environment.
  - Copilot's second pass on the corrected branch returned no further comments.

- **Project tracking** — GitHub Project `aristech` #57 created (node `PVT_kwHOB8rwIc4BYKoi`). PR #2 attached. Future aristech PRs and issues should be routed here.

- **PR #4 merged** (`76e74ab`) — `docs(research): inaugural state-of-the-art survey for hornet detection and deterrence`. Branch `research/state-of-the-art-detection`, 3 files added/changed, +770 lines, squash-merged at 18:25 UTC. First formal literature review of the project, covering five axes (Kaggle, GitHub, academic + HuggingFace, auto-aim turret prior art, French/EU legal framework). Adds `docs/research/state-of-the-art.md` (narrative survey) and `docs/research/references.md` (centralised bibliography), and disables markdownlint rule `MD060` (table column alignment) to allow variable-content tables.

  - **Review cycle** — single Copilot pass raised five Should-Have findings, all addressed in a follow-up commit before merge (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/4>): stale `pending` status header; AI/process attribution (`Agent #5`) leaked into the narrative; missing cross-link between the two new documents; `Code rural et de la pêche maritime` cited without a Légifrance URL; bibliography conventions claiming columns the actual sections do not honour. Each fix replied to inline with the corrective commit SHA. Codex did not auto-review this PR (unlike PR #3).

- **Decisions**:
  - `neutralize-target-non-lethal-water-jet` — **closes one of the three open product questions from PR #1's `neutralize-target-deferred`** (lethality). Direction validated: non-lethal water-jet deterrent. Rejected alternatives: coil-gun (lethal — unacceptable under L411-1 risk of harming non-target species) and alert-only (insufficient to protect the colony during sustained attacks). Two questions remain open: multi-modal fusion (vision-only vs vision-and-audio confirm), and fail-safe default policy (`dry-run` vs live). Final lock-in will happen in a dedicated PR amending `docs/architecture.md` once a first prototype proves the kinematics.
  - `legal-floor-hard-architectural-guard` — the survey identified that harming a protected pollinator is criminal under **Art. L411-1 + L415-3 Code de l'environnement** (up to 3 years prison + 150 000 € fine, 7 years + 750 000 € en bande organisée). The "never spray a bee" requirement is therefore not just ethics but a binding criminal-law constraint. Architectural consequence: the species classifier must default to _abstain → do not act_ on low confidence, and a geometric "no-spray" exclusion zone around the hive landing board must be enforced independently of the classifier.
  - `multimodal-vision-plus-audio-as-niche` — the survey found **no published fusion baseline** for V. velutina detection. Hall et al. 2025 reports 98.7% accuracy on hovering acoustic signature alone, complementary to vision. Architectural target retained: always-on acoustic wake-up signal trigger the vision pipeline only when an acoustic candidate is detected. Saves energy, robust to occlusion, exploits an open scientific niche.

- **Open research debt** — six second-priority axes identified by the survey, not yet investigated: behavioural biology of V. velutina at the hive entrance (A), hive geometry and ergonomy (B), hardware BOM and energy autonomy (C), real-world deterrent efficacy and habituation (D), environmental robustness (E), FMEA (F). Plus strategic axes: commercial competitors, funding sources, patent landscape, field partners, own-corpus annotation. Each will be tackled in dedicated PRs as the project progresses.
