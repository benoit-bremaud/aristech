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
  - `neutralize-target-non-lethal-water-jet` — **closes one of the three open product questions from PR #1's `neutralize-target-deferred`** (lethality). Direction validated: non-lethal water-jet deterrent. Rejected alternatives: coil-gun (lethal — unacceptable under L411-1 risk of harming non-target species) and alert-only (insufficient to protect the colony during sustained attacks). Documented as decided in `docs/architecture.md` by this same PR. The two remaining questions stay open: multi-modal fusion (vision-only vs vision-and-audio confirm), and fail-safe default policy (`dry-run` vs live). They will be locked in dedicated PRs once a first prototype produces evidence on kinematics and false-positive rates.
  - `legal-floor-hard-architectural-guard` — the survey identified that harming a protected pollinator is criminal under **Art. L411-1 + L415-3 Code de l'environnement** (up to 3 years prison + 150 000 € fine, 7 years + 750 000 € en bande organisée). The "never spray a bee" requirement is therefore not just ethics but a binding criminal-law constraint. Architectural consequence: the species classifier must default to _abstain → do not act_ on low confidence, and a geometric "no-spray" exclusion zone around the hive landing board must be enforced independently of the classifier.
  - `multimodal-vision-plus-audio-as-niche` — the survey found **no published fusion baseline** for V. velutina detection. Hall et al. 2025 reports 98.7% accuracy on hovering acoustic signature alone, complementary to vision. Architectural target retained: always-on acoustic wake-up signal trigger the vision pipeline only when an acoustic candidate is detected. Saves energy, robust to occlusion, exploits an open scientific niche.

- **Open research debt** — six second-priority axes identified by the survey, not yet investigated: behavioural biology of V. velutina at the hive entrance (A), hive geometry and ergonomy (B), hardware BOM and energy autonomy (C), real-world deterrent efficacy and habituation (D), environmental robustness (E), FMEA (F). Plus strategic axes: commercial competitors, funding sources, patent landscape, field partners, own-corpus annotation. Each will be tackled in dedicated PRs as the project progresses.

- **PR #6 merged** (`9daf5a5`) — `docs(research): prototype foundations on biology, geometry, BOM`. Branch `research/prototype-foundations`, 2 files added/modified, +835 lines, squash-merged at 20:55 UTC. Closes the three Priority-1 axes (A, B, C) identified by PR #4, plus a focused synthesis of Éric Darrouzet's body of work on the French side.

  - **Added** `docs/research/prototype-foundations.md` (729 lines): four sections of applied engineering inputs — A. Behavioural biology at the hive entrance (predation cycle, diel/seasonal/weather pattern, flight kinematics, visual discrimination, colony stress response, deterrent efficacy); A.bis. Synthesis of Éric Darrouzet (IRBI / Université de Tours) — 11 peer-reviewed papers 2015-2024, books, talks, operational positions on selective trapping / spring queens / harps / acoustic / nest localisation; B. Hive geometry and sensor mounting (Dadant 10 cadres dominant FR, FOV/lens sizing, mounting strategies, IP65 enclosure, calibration flow); C. Hardware BOM and energy autonomy (Pi 5 + Hailo-8L AI HAT+ recommended, Pi HQ + 6 mm lens, MG996R + PCA9685 v1 servos, VL53L5CX ToF, SPH0645 mic, 12 V diaphragm pump fluid path, 100 W panel + 100 Ah LiFePO4 solar stack).
  - **Extended** `docs/research/references.md` with four new sections (13-16) centralising every new source.
  - **Review cycle** — single Codex pass raised two P1 findings, both addressed in `a624c94` before merge (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/6>): daily Wh totals were internally inconsistent (143 / 179 Wh actual vs the stated 180 / 215; sizing arithmetic propagated); Total BOM table understated versus documented per-component minima (rebuilt: v1 perception+actuation without solar 447-500 EUR vs stated 360; v1 autonomous with solar 787-880 EUR vs stated 720). Copilot did not auto-review this PR.

- **Decisions** (informed by PR #6, formal lock-in in this entry):
  - `strike-rate-baseline` — adopted **2.4% overall predation success at hive entrance, density-dependent peak around ~8 simultaneous hornets** ([Robinet/Darrouzet 2023, Sci. Reports][lpr6-1]) as the engineering "miss-reduction" baseline. Aristech's deterrent efficacy will be measured as percentage drop in successful strikes when active vs the same colony without it.
  - `selectivity-floor-vs-harp-benchmark` — adopted **> 90% V. velutina in catch, < 2% non-target** ([Thiéry & Darrouzet 2023, Entomologia Generalis][lpr6-2]) as the published selectivity bar. Aristech's vision classifier must meet or exceed this without making contact with any insect.
  - `camera-lens-v1` — Pi HQ Camera (IMX477) + 6 mm M12 wide lens, 30° downward tilt, ~80 cm in front of the planche d'envol. Hornet projects to ~47 px at 1 m, comfortably above the YOLO recall floor (30 px). Reconciles the geometry vs BOM survey divergence (wide FOV wins over telephoto because the hovering volume must be observed, not just the impact zone).
  - `compute-platform-v1` — Raspberry Pi 5 8GB + AI HAT+ Hailo-8L (13 TOPS NPU). Best perf/€/W; Jetson Orin Nano wins on raw FPS but doubles power draw and halves the solar budget.
  - `aristech-positioning-vs-harp` — non-lethal, non-contact **complement** to the electric harp (Darrouzet's published benchmark), not a competitor. Value proposition: zero non-target kill, no carcass disposal, no daily maintenance. Side-by-side validation against a harp on the same rucher is the planned protocol.

[lpr6-1]: https://pmc.ncbi.nlm.nih.gov/articles/PMC10049882/
[lpr6-2]: https://www.schweizerbart.de/papers/entomologia/detail/43/103168/

- **In-house first-publication opportunities** — four open biological measurements that no peer-reviewed paper has produced, all directly available from aristech's annotated video + audio corpus: hover distance / height in front of the planche, strike rate per minute per hornet, hover jitter / turn radius / reaction latency, V. velutina wingbeat fundamental frequency. Each would be a publishable contribution. Decision on annotation pipeline (LabelStudio / CVAT / Roboflow Annotate) deferred to a dedicated PR.

- **Documentation tooling** — `aristech-research-navigation` skill added at `~/.claude/skills/aristech-research-navigation/SKILL.md` (outside the repo, machine-local). Acts as the authoring rules and doc map for the three-document research discipline (SOTA + foundations + bibliography). `docs/INDEX.md` added in the same follow-up PR as this log entry — entry-point map for every doc in the repo.

---

## 2026-05-20

State-of-the-art audit session (codename: audit-2026-05-20). Closed the two PRs left open from the previous day and ran the full merge gate on each (CI green + automated review posted + every comment addressed inline + explicit owner approval before merge).

- **PR #7 merged** (`2837afb`) — `docs: add docs/INDEX.md and log PR #6 in PROJECT_LOG.md`. Branch `docs/index-and-log-pr-6`, squash-merged. Adds `docs/INDEX.md` (documentation entry-point map) plus the PR #6 log entry above.

  - **Review cycle** — two automated review passes. The first raised one P2: the INDEX Reports section linked to `coverage_report.txt` / `coverage.xml`, which do not exist — fixed on the branch before merge by repointing to the artefacts actually present in `docs/reports/`. The second pass posted five comments; four addressed in one commit (list `docs/README.md` and narrow the "every document" claim to "key documents"; mark the empty `docs/usage.md` as a placeholder; replace the French "tranché" with "decided" for English-only consistency; relax the one-sentence-per-row maintenance rule to allow the existing "Authority on …" qualifier). The fifth — a claimed line-count drift on `prototype-foundations.md` — was declined after verifying the count matched the file; exact line counts are noted as brittle and avoided in future entries.

- **PR #8 merged** (`23d8ed4`) — `docs: reframe README + CONTRIBUTING for private R&D, add PR template`. Branch `docs/p1-public-presentation` (the "public" in the branch name is a misnomer kept from before the private re-scoping; content is explicitly private-framed). Squash-merged. Reframes `README.md` and `docs/CONTRIBUTING.md` from open-source contributor recruitment to a private solo-maintainer R&D project, repairs the broken `CONTRIBUTING.md` (the MIT licence text had been pasted into the middle of the contribution steps), and adds `.github/PULL_REQUEST_TEMPLATE.md`.

  - **Review cycle** — the automated review flagged that `README.md` and `CONTRIBUTING.md` linked to `docs/INDEX.md` while that file did not yet exist on the branch; resolved by merging `main` into the branch once PR #7 had landed INDEX.md (dependency ordering, no content change). A second pass posted two comments, both addressed: capitalise "Aristech" as a proper noun in the positioning prose (lowercase `aristech` retained for package / CLI identifiers such as `python -m aristech`); add an inline caveat to the cleanup snippet that `git branch -d` may report a branch as unmerged after a squash-merge (use `-D` if needed).

- **Audit findings (not yet actioned)** — the session's repo audit surfaced quick-win debt for a follow-up PR: empty placeholders (`docs/usage.md` is 0 lines; both `docs/reports/*.pdf` are 0 bytes) and missing domain unit tests (the `geometry`, `species`, `target`, `media` entities have no test module — only `detection` does). Larger items stay explicitly deferred: the empty `infrastructure/` layer (first vision adapter is a foundation-sized chunk), the `git filter-repo` history purge of the model blobs (still ~61 MB in `.git/`), and UML diagrams — held until the open product decisions (multi-modal fusion, fail-safe default) stabilise the scope enough for diagrams to be worth drawing.

- **PR #9 merged** (`471b326`) — `docs: log PR #7 and #8 closure in PROJECT_LOG.md`. Branch `docs/log-pr-7-8`, squash-merged. Adds the two PR #7 / #8 entries above.

  - **Review cycle** — automated review posted two comments, both addressed before merge (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/9>): the draft entry named the review tools, breaking the agent-agnostic log rule — redacted to generic wording ("automated review"); and an exact line-count claim was flagged as brittle — the figure was dropped, exact counts avoided in future entries.

- **PR #10 merged** (`11cc61a`) — `chore: clear empty doc placeholders and add domain entity tests`. Branch `chore/quick-wins-cleanup`, squash-merged. Closes two of the quick-win audit findings above: removes three empty placeholders (`docs/usage.md` and the two 0-byte `docs/reports/*.pdf`) with their `docs/INDEX.md` rows and `docs/README.md` references; adds unit tests for the `geometry`, `species`, `target`, and `media` domain entities (previously only `detection` was covered). 33 unit tests pass; ruff clean. Verified locally in a venv before push.

  - **Review cycle** — automated review posted no comments.

---

## 2026-05-21

Audit session continued past midnight: closed the planning and hygiene work opened the day before.

- **PR #11 merged** (`804b864`) — `docs: add v1 requirements and detection-first roadmap`. Branch `docs/v1-requirements-and-roadmap`, squash-merged. The project's first written plan, produced from a needs-first brainstorming session: `docs/requirements.md` (vision, scope, functional / non-functional needs, hard constraints, detection decisions with rationale) and `docs/ROADMAP.md` (the detection staircase M0–M6, each step with sub-tasks and an explicit gate), plus a Planning section in `docs/INDEX.md`. Method: Dependency Inversion applied at project level — needs are the stable high-level policy; the stack (board, sensors, model) is a downstream detail that conforms to them.

  - **Decisions** (detection v1): wrap the VespAI baseline first, fine-tune on own data later; vision first, audio later; three classes (velutina / bee / other); detection output = 2D bbox + species + confidence (the `Detection` entity), 3D distance deferred; fixed camera over the flight volume; operating point = ~100% precision on bee (legal floor) with relaxed hornet recall + abstention by default. v1 scope = detection + alert (no actuator); alert kept provisional.
  - **Review cycle** — automated review posted four comments, all addressed before merge (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/11>): a wrong PR reference for the non-lethal decision (decided in PR #4, not #5) was corrected and pointed at `docs/architecture.md`; three English-consistency fixes (replaced French terms in the otherwise-English docs).

- **PR #12 merged** (`1681c3f`) — `fix: repair .gitignore patterns neutralised by inline comments`. Branch `chore/fix-gitignore`, squash-merged. An audit finding turned out to be larger than expected: nearly every `.gitignore` pattern carried a trailing inline comment, which Git treats literally (it only honours `#` at line start), so the patterns were inert — `__pycache__/`, `*.egg-info/`, build artefacts, `data/**`, and **notably `.env`** were not ignored (a latent secret-leak risk, now closed). Moved every comment to its own line, fixed two stray negation (`!`) bugs, and removed a few duplicates.

  - **Review cycle** — automated review posted one P2: the directory-level ignores (`data/foo/`) made the `!.../.gitkeep` re-includes ineffective, because Git will not re-include a file beneath an ignored parent directory. Fixed before merge (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/12>) by ignoring content (`data/**` + `!data/**/` + `!data/**/.gitkeep`) so Git still descends and the markers survive at any depth, including for newly added files. Verified with `git check-ignore --no-index`.
