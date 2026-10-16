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

- **Project tracking** — the detection plan in `docs/ROADMAP.md` was mirrored as a GitHub **Epic #19** (v1 Detection — vision) with five native sub-issues **M0–M4 (#14–#18)** on Project #57. Each sub-issue carries the milestone's sub-tasks and gate.

- **PR #20 merged** (`2336ddd`) — `docs(requirements): record M0 VespAI findings (classes, licence)`. Branch `docs/m0-vespai-findings`, squash-merged. Closes **#14 (M0)**. The VespAI feasibility spike: the model is usable for v1 (detects _V. velutina_ + _V. crabro_, weights provided, F1 ≥ 0.99, Pi-4 deployable), with two plan adjustments — its output classes are **only velutina + crabro (no bee class)**, so the bee is handled as a negative and an explicit bee class is deferred to the M5 fine-tune; and its **CC BY-NC-SA** licence is accepted for non-commercial v1 only (a permissively-licensed model is needed before any product). `requirements.md` revised and the research SOTA doc aligned.

  - **Review cycle** — automated review posted three comments, all addressed before merge (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/20>): clarified that _V. crabro_ is a non-target, reworded the operating point in v1 (alert, no actuator) terms, and aligned the SOTA doc on VespAI's actual classes.

- **PR #21 merged** (`34ec9b3`) — `docs(research): M1 data-inventory findings`. Branch `docs/m1-data-inventory`, squash-merged. Part of **#15 (M1)**. Recorded that vespCV's training dataset is not shared (code + a pretrained YOLOv11s model only) and that a Roboflow Universe set labels three classes including the bee (~118 images; exact URL + licence still `to-verify`) — the most direct seed for the deferred explicit-bee class (M5). The "run VespAI on a batch" half of M1 was then completed in an isolated spike (the model confirmed: two output classes, high-confidence _V. velutina_ detection, distinguishes the two hornet species), closing **#15**.

  - **Review cycle** — automated review posted one comment, addressed before merge (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/21>): made the GPL-3.0 copyleft wording precise and consistent between the repo table and the synthesis.

- **PR #22 merged** (`aba2e28`) — `feat(vision): VespAI detection adapters wired into DetectHornetVisual`. Branch `feat/m2-vision-adapters`, squash-merged. Closes **#16 (M2)**. The first real infrastructure code: `OpenCVVideoSource` + `VespAIDetector` + `LoggingNotifier` wired into the `DetectHornetVisual` use case via the CLI composition root — **aristech now detects hornets end-to-end** (verified: 60 _V. velutina_ threats logged on a clip). Heavy dependencies were reorganised into optional extras (`vision` / `audio` / `training` / `connectivity`); the core install is now light. VespAI weights (CC BY-NC-SA) are loaded from a supplied path, never bundled; torch / YOLOv5 (BSD / AGPL) are wrapped at runtime, not vendored.

  - **Decisions** — `torch` moved to an optional `vision` extra rather than a base dependency, realising the project's DIP / Clean-Architecture decision (infrastructure is an interchangeable detail); the bee stays a negative in v1 (confirmed by the model's two output classes).
  - **Review cycle** — two automated review passes posted seven comments total, all addressed before merge (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/22>): a `--confidence` out-of-range crash, a too-narrow logging fallback, an ambiguous camera-index/path heuristic, missing `--weights` / `--yolov5-dir` path validation, a non-thread-safe `torch.load` monkeypatch (now lock-guarded), a security warning on `weights_only=False` pickle loading, and a misleading "threat" log label (now neutral with a `threat=<bool>` field).

---

## 2026-05-22

- **PR #23 merged** (`71850ce`) — `docs: log PR #20-#22 (M0/M1/M2 milestones) in PROJECT_LOG.md`. Branch `docs/log-pr-20-to-22`, squash-merged. Logbook catch-up for the M0/M1/M2 milestones plus the Epic #19 tracking note above.

  - **Review cycle** — automated review posted one comment, addressed before merge (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/23>): mirror the `to-verify` qualifier on the Roboflow set, so the log does not overstate dataset certainty.

- **PR #24 merged** (`6bf9469`) — `feat(evaluation): detection metrics harness`. Branch `feat/m3-eval-harness`, squash-merged. Part of **#17 (M3)** — the **code half**. Adds `aristech.evaluation`: a pure metrics harness — IoU, greedy confidence-ordered location-based matching of predictions to ground truth, per-class precision / recall / F1, and a confusion matrix (with a `background` label for false positives and misses), plus threshold validation. No I/O, no torch → unit-tested in CI, including the legal-floor case (a bee location predicted as a hornet counts as a _V. velutina_ false positive). The **dataset half** of M3 (an annotated test set + a runner producing the per-class report on a frozen set — the gate) stays open on **#17**, pending a Roboflow download or own footage.

  - **Review cycle** — two automated review passes posted four comments total, all addressed before merge (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/24>): validate the IoU / confidence thresholds and fail fast (which also closed an IoU=0 matching loophole), add `slots=True` to `EvaluationReport`, and annotate the test helpers.

- **PR #25 merged** (`9183075`) — `docs: log PR #23-#24 (M3 code half) in PROJECT_LOG.md`. Branch `docs/log-pr-24`, squash-merged. Logbook catch-up for PR #23 and the M3 code half (#24).

  - **Review cycle** — automated review posted one comment, addressed before merge (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/25>): give the PR #23 entry its full title and a nested Review-cycle bullet, consistent with the other entries.

- **PR #26 merged** (`930c676`) — `docs(requirements): adopt observability/health model over per-detection alerts`. Branch `docs/observability-health-decision`, squash-merged. Reframes notifications for an autonomous, unattended, outdoor device, in `requirements.md` and `ROADMAP.md`.

  - **Decisions** — `observability-over-alerts` — three distinct signal types: **detections → structured local log** (statistics + the data flywheel, never pushed); **heartbeat** (periodic liveness ping; liveness judged by its _absence_ via a server-side watchdog — a dead man's switch); **faults → push notification** only when something is wrong, and only for faults the device can both detect and deliver (connectivity loss is surfaced by the watchdog instead). Rejected the earlier provisional "alert" defaults (Telegram push of aggregated detections) as the wrong model — "no per-detection notification". v1 scope = detection + logging; the heartbeat / fault-alerting / watchdog are implemented with the embedded deployment (M6).
  - **Review cycle** — three comments across two automated review passes, all addressed before merge (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/26>): a v1-vs-M6 scope contradiction, a leftover deterrence fragment on the health requirement, and the connectivity-loss-can't-self-push nuance.

- **PR #27 merged** (`b6c1f70`) — `docs: log PR #25-#26 (observability/health decision) in PROJECT_LOG.md`. Branch `docs/log-pr-25-26`, squash-merged. Logbook catch-up for PR #25 and the observability/health decision (PR #26). One review comment (a verb-agreement fix) addressed before merge (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/27>).

- **PR #28 merged** (`b10e853`) — `feat(evaluation): YOLO label reader`. Branch `feat/m3-yolo-label-reader`, squash-merged. Part of **#17 (M3)** — the dataset plumbing. Adds `aristech.evaluation.parse_yolo_labels`: a pure parser turning normalised YOLO label lines (`<class_id> <cx> <cy> <w> <h>`) into pixel-space domain `Annotation`s (configurable class-id → `Species` map, unknown ids → `UNKNOWN`), ready to feed `evaluate`. Malformed lines / out-of-range values / non-positive image size raise `ValueError` with line context. Unit-tested in CI. The full runner (walk a dataset, run VespAI, evaluate → report) still stays open on **#17**, deferred until the real dataset layout is known.

  - **Review cycle** — automated review posted one comment, addressed before merge (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/28>): wrap the numeric `int()`/`float()` parse failures so a non-numeric field raises a `ValueError` naming the offending line, consistent with the other validation branches.

- **PR #29 merged** (`bba1ac6`) — `docs: log PR #27-#28 (YOLO label reader) in PROJECT_LOG.md`. Branch `docs/log-pr-28`, squash-merged. Logbook catch-up for PR #27 and the YOLO label reader (PR #28). One review comment (disambiguate PR refs) addressed before merge (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/29>).

- **PR #30 merged** (`7726714`) — `docs: product strategy from debrief — deterrence D0 gate, v1 standalone, DIP decoupling`. Branch `docs/product-strategy-from-debrief`, squash-merged. Captures, in `requirements.md` and `ROADMAP.md`, the strategy decided in a product debrief with the owner.

  - **Decisions**:
    - `deterrence-efficacy-objective-90pct` — deterrence efficacy is measured as the **% drop in successful strikes** (a hornet snatching a forager) on an equipped hive vs the same hive without the system, against the published ~2.4% predation-success baseline. Aspirational target **~90%**, explicitly an _objective_, **not** an acceptance gate.
    - `deterrence-hypothesis-unvalidated` — that a non-lethal water jet actually deters _V. velutina_ (it breaks off and leaves rather than habituates) has never been observed and is the project's **risk #1**. A new ROADMAP milestone **D0** (a cheap, manual, seasonal field test) gates it: **no actuator / aiming engineering starts until D0 is positive**; otherwise reorient (another modality, or monitoring-only).
    - `v1-monitoring-standalone-value` — the v1 (detection + structured logging) is a **deployable monitoring deliverable** on its own (hornet-pressure statistics + gold footage for the M5 fine-tune), not just a stepping stone.
    - `detection-deterrence-decoupling-dip` — detection and deterrence are **complementary, decoupled modules** wired only by the detection signal: deterrence depends on the abstractions the detector emits (`Detection` / `Target`) and on the ports, never on the concrete detector (Dependency Inversion). Detection is validated/shipped alone; deterrence plugs into its output later.
  - **Review cycle** — automated review posted two comments, both addressed before merge (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/30>): reword the D0 break-off / return / habituation criteria into plain grammatical English, and cite the strike-rate baseline to its actual section (§ A) rather than a non-existent anchor.

- **PR #31 merged** (`84ee4a3`) — `docs: log PR #29-#30 (product strategy decisions) in PROJECT_LOG.md`. Branch `docs/log-pr-30`, squash-merged. Logbook catch-up for PR #29 and the product-strategy decisions (PR #30); merged without review comments (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/31>).

---

## 2026-05-23

- **PR #32 merged** (`dbf3b74`) — `feat(evaluation): dataset runner (M3 — detector × YOLO dataset → report)`. Branch `feat/m3-eval-runner`, squash-merged. Closes **#17 (M3)** — the **dataset half**, completing the milestone. Adds `aristech.evaluation.evaluate_on_dataset`: walks a YOLO-format dataset (Roboflow YOLOv5 layout — `<split>/images` + `<split>/labels`), runs an injected `HornetDetector` per frame, parses the labels as ground truth, and aggregates into one `EvaluationReport` — the one-command, recomputable per-class precision / recall the M3 gate asked for. Both the detector (port) and the image reader are injected (Dependency Inversion); the default reader lazy-imports cv2, so the orchestration is unit-tested with fakes (no torch / cv2 in CI). Exercised end-to-end against a 364-image annotated Roboflow _V. crabro_ / _V. velutina_ set; the formal frozen-set figures are the next deliverable (the M3 gate evidence).

  - **Note** — **#17** had been closed prematurely after the code half (#24); it was reopened so this PR could close it on completion of the runner, keeping the issue trail coherent.
  - **Review cycle** — two automated review passes posted three comments total, all addressed before merge (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/32>): a missing requested split is now a fail-fast `FileNotFoundError` instead of a silent all-zero report (which would otherwise corrupt a misconfigured run, e.g. default `splits=("test",)` on a `valid`-only dataset); a missing label file now logs a warning before being treated as a negative image (so a truncated export isn't mistaken for legitimately empty images), with a dedicated test; and the samples are now streamed across splits (`itertools.chain.from_iterable`) rather than materialised into a list, since `evaluate` consumes the iterable exactly once — keeping memory flat over large datasets.

- **PR #33 merged** (`2245152`) — `docs: log PR #31-#32 (M3 milestone complete) in PROJECT_LOG.md`. Branch `docs/log-pr-31-32`, squash-merged. Logbook catch-up for PR #31 and the M3-completing dataset runner (PR #32).

  - **Review cycle** — automated review posted one comment, addressed before merge (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/33>): the new PR #31 entry was missing its PR-conversation URL, restored for traceability consistency with the surrounding entries.

- **PR #34 merged** (`31854c2`) — `docs(deterrent): research biodegradable impact media + D0 multi-arm comparison`. Branch `docs/deterrent-media-hydrogel-research`, squash-merged. Sourced research, triggered by an owner idea to replace the pure-water jet with swelling gel beads, on whether a more **visibly impactful** deterrent medium could be both effective and biodegradable. Extends `state-of-the-art.md` (new "Deterrent media beyond pure water" survey), `prototype-foundations.md` (§ A efficacy-table row + D0 multi-arm comparison grid and protocol notes), `architecture.md` (open decision #5), and `references.md` (§ 9.6, 12 sources).

  - **Decisions**:
    - `deterrent-medium-pure-water-vs-projectile` — the deterrent **modality** (non-lethal jet) is settled (cf. decision #1), but the **medium** is **open, default = pure water**. Research finding: pure water and an **air pulse / vortex** are the only candidates as eco-clean as water; solid projectiles cumulate poor hit-probability on an agile flying target, a lethal-velocity tension with the non-lethal guard, and dispersed waste. The cheap "Orbeez"-type bead (sodium polyacrylate) is **excluded outright** as a non-biodegradable microplastic; calcium-alginate is too fragile (dissolves); starch-SAP and gelatin/PEG pellets are genuinely biodegradable but remain dispersed single-use consumables. Any solid projectile is **hard-blocked** by three guards (legal floor _pure water only_ / leave-no-trace / non-lethal envelope), so it is **not a D0 arm**; the **D0 multi-arm** field test compares only the eco-clean arms (pulsed water vs air pulse). Nothing is committed — the medium is decided later by D0.
  - **Review cycle** — Copilot posted a clean review (0 comments); Codex posted one comment, addressed before merge (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/34>): the "hard-blocked solid projectile" language contradicted listing a throttled-pellet D0 arm — resolved by putting solid-projectile arms explicitly out of D0 scope in both `architecture.md` and `prototype-foundations.md`, so the protocol is unambiguous.

- **PR #35 merged** (`4713a20`) — `docs: log PR #33-#34 (deterrent media research) in PROJECT_LOG.md`. Branch `docs/log-pr-33-34`, squash-merged. Logbook catch-up for PR #33 and the deterrent-media research (PR #34); merged without review comments (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/35>).

---

## 2026-05-24

- **PR #36 merged** (`e3ab5d9`) — `feat(evaluation): operating-point selection + explicit abstention policy (M4)`. Branch `feat/m4-operating-point`, squash-merged. Part of **#18 (M4)**. Adds `aristech.evaluation.operating_point` (`threshold_sweep`, `bees_as_target_count`, `select_operating_point`): the operating point is the lowest confidence threshold at which **zero honeybees are classified as the target** (_V. velutina_), maximising hornet recall under that legal-floor zero; it raises when no threshold reaches zero. `collect_samples()` is extracted from the runner so detection runs once at confidence 0 and thresholds are swept downstream. `application/decision.py` adds a `Decision` enum (ACT / ABSTAIN / IGNORE) and a pure `decide()`; a below-threshold target now explicitly abstains. `DetectHornetVisual` routes through `decide()` with unchanged behaviour.

  - **Review cycle** — automated review raised one comment (the detector must run unfiltered during threshold sweeps), handled before merge through the confidence-0 contract of `collect_samples` (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/36>).

---

## 2026-10-15

- **Project resumed after audit** — aristech was paused on 2026-05-24 and audited on 2026-10-15. The owner decided the project follows the full method (design dossier, ADRs, UML, review gates) given its size and complexity. Brick order: close PR #37, security CI baseline, method foundation, live-path double-threshold fix, tests, YAGNI cleanup, docs.

- **Repository made public** — per the owner rule that personal repositories stay public until their first production deployment. Full-history secret scan clean; CI secret detection is still missing and lands with the security CI baseline brick.

- **PR #37 merged** (`b131ad1`) — `chore(scripts): add measure_operating_point for the M4 on-set sweep`. Branch `feat/m4-measure-script`, squash-merged. Part of **#18 (M4)**. Adds `scripts/measure_operating_point.py`: runs VespAI once at confidence 0 over a YOLO dataset, prints the per-threshold curve and the selected legal-floor operating point. Runs locally only (needs the `vision` extra, operator-supplied weights and the annotated set). **#18 stays open**: the on-set measurement and the live-path double-threshold fix are still pending.

  - **Review cycle** — automated review raised one comment, addressed before merge (see PR conversation at <https://github.com/benoit-bremaud/aristech/pull/37>): the class map is now validated after parsing — no `vespa_velutina` id fails fast with exit 2; no `apis_mellifera` id only warns, since bees-as-target is then vacuously 0 and the legal-floor gate is not exercised (the Roboflow set has no bee class). Unit tests added for the parser and both paths.

---

## 2026-10-16

- **PR #39 merged** (`d5ede54`) — `ci(security): add Gitleaks, CodeQL, dependency review, Scorecard and Dependabot`. Branch `ci/security-baseline`, squash-merged. Security CI baseline brick of the post-audit plan, closing the last open item of the public-release checklist (CI secret detection). Adds one workflow per tool: Gitleaks (full history, blocking, SARIF), CodeQL Python (`security-extended`), dependency review on PRs (fails on high/critical), OSSF Scorecard (main + weekly), plus Dependabot weekly grouped updates for `pip` and `github-actions`. All actions pinned by SHA, least-privilege job permissions; `ci.yml` unchanged. Repository settings enabled alongside: secret scanning, push protection, Dependabot security updates.
  - **Decisions** — Gitleaks via its official action rather than a pinned CLI (weighted matrix 430 vs 420); Scorecard included now rather than deferred (340 vs 310).
  - **Review cycle** — automated reviewers unavailable (out of credit); the owner accepted the local pre-push review report as the review (Must 0, Should 1 handled through the repository settings, Nice 1 filed as #40 — SARIF upload fails on fork PRs). See PR conversation at <https://github.com/benoit-bremaud/aristech/pull/39>.

- **PR #44 merged** (`6c8c208`) — `docs: log PR #39 (security CI baseline) in PROJECT_LOG.md`. Logbook catch-up for PR #39.

- **Dependabot security PRs #41, #42, #43 merged** (`9b95572`, `4254a11`, `007c5f0`) — transitive security bumps of urllib3 (2.2.1 → 2.8.0), werkzeug (3.0.3 → 3.1.9) and fsspec (2024.5.0 → 2026.6.0), CI green. Triage of the backlog opened by the new Dependabot configuration (weighted matrix: merge now 470 vs defer 320 vs group with the pip bump 265).
  - **Deferred** — grouped pip bump #45 fails dependency review (keras 3.12.4, two high advisories, plus major torch / opencv / tensorflow jumps): tracked in #47. Grouped github-actions bump #46 left to the owner (workflow files).

- **PR #51 merged** (`268b1b1`) — `chore(sonar): onboard aristech on the local SonarQube`. Branch `chore/sonarqube-onboarding`, squash-merged. Adds `sonar-project.properties` (key `aristech`, Python 3.10, coverage report, legacy `training/` excluded) and a `make sonar` target (unit-test coverage XML, then the scanner; token read from `SONAR_TOKEN`). First scan of `main`: quality gate passed, coverage 84.3 %, 0 bugs, 0 vulnerabilities, 0 security hotspots, 0 % duplication, 2 code smells (tracked in #50 for the test-hygiene brick).
  - **Decisions** — local scanner rather than a pinned container (weighted matrix 410 vs 400 vs docs-only 335); no CI scan, since hosted runners cannot reach the local instance and the Community Build analyses `main` only.

- **PR #49 merged** (`4a4d162`) — `docs: method foundation — CLAUDE.md, design dossier skeleton, audit report (B1 part 1)`. Branch `docs/b1-foundation`, squash-merged. First of three method-foundation PRs (audit finding M7): project `CLAUDE.md`, the `docs/architecture/` dossier skeleton (specs, diagrams, traceability, gates, reviews) and the `docs/decisions/` ADR index; ships the 2026-10-15 audit report (`docs/architecture/reviews/audit-2026-10-15.md`, original commit cherry-picked); `docs/INDEX.md` marks `architecture.md` as legacy and routes decisions to ADRs.
  - **Decisions** — audit imported by cherry-pick (weighted matrix 470 vs merge 380 vs copy 330); the local pre-push review report is the review for the B1 PRs (415 vs 330).
  - **Review cycle** — local report: Must 2, Should 4, Nice 2, all handled before push except one intentional (dev-env install command). Automated reviewer unavailable (usage limit). See <https://github.com/benoit-bremaud/aristech/pull/49>.

- **PR #52 merged** (`3f347c0`) — `docs(decisions): retroactive ADRs 0001-0008 (B1 part 2)`. Branch `docs/b1-adrs`, squash-merged. Records the eight decisions taken before the ADR practice: Clean Architecture + optional extras, VespAI baseline, legal floor (abstain by default), zero-bee operating point, non-lethal decoupled deterrent gated by D0, observability over alerts, security CI + local SonarQube, adoption of the working method. Scores are reconstructed retroactively and flagged as such; totals recomputed by script (12 addition errors corrected before review, no ranking change). `CLAUDE.md` documents `make sonar`.
  - **Review cycle** — local report: Must 0, Should 3 (2 fixed, 1 deferred to this log entry), Nice 3 fixed. The root `pytest` collection error (audit M1, pre-existing) stays in the test-hygiene brick by owner decision (430 vs 420).

- **PR #53 merged** (`3fd36f7`) — `docs(detection/architecture): add as-built UML deliverables for detection (B1 part 3)`. Branch `docs/b1-uml`, squash-merged. Use-case, sequence (live loop), component and class diagrams of the current detection path, plus the first traceability matrix. The sequence diagram makes the double confidence filter visible: the detector and `decide()` filter at the same threshold, so ABSTAIN never fires live (audit M3) — the input of the next brick (B4).
  - **Review cycle** — local report checked every arrow against the code: Must 2, Should 4, Nice 1, all fixed before push; diagrams render-checked.

- **PR #55 merged** (`8c66fe3`) — `chore(sonar): read the aristech project token file in make sonar`. Branch `chore/sonar-project-token`, squash-merged. `make sonar` reads the project analysis token `project-aristech-local-2026` from `~/.config/sonar-tokens/aristech` (mode 600, outside the repo) and falls back to `SONAR_TOKEN`. The auto-created SonarQube project was private with no grants (invisible in the UI); it is now public on the local instance. Control scan with the project token: analysis successful.
  - **Decisions** — dedicated project token rather than the global analysis token (owner choice).
  - **Review cycle** — local report: no Must/Should; one Nice (reading results needs a user token, out of scope). Automated reviewer unavailable (usage limit).

- **PR #46 merged** (`92ae322`) — `chore(ci): bump the github-actions group with 2 updates`. Dependabot, squash-merged. `actions/checkout` v4 → v7 and `actions/setup-python` v5 → v7 in `ci.yml`; all checks green on the Python 3.10–3.12 matrix.
- **Branch cleanup** — local `docs/audit-2026-10-15` and its detached worktree branch deleted: the audit commit landed on `main` by cherry-pick in #49.
  - **Decisions** — closure plan "merge #46 + delete the audit branches, defer the shell-profile change" (weighted matrix 455 vs everything 395 vs #46 only 385 vs defer all 255).

- **PR #58 merged** (`96bf8d7`) — `fix(cli): separate detector floor from operating threshold so ABSTAIN fires live`. Branch `fix/b4-double-threshold`, squash-merged. Brick B4, audit M3 fixed: new `--detector-floor` (default `min(0.1, --confidence)`, must be `<= --confidence`); the detector runs at the floor and only `decide()` applies the operating threshold, so uncertain *V. velutina* detections now reach ABSTAIN. `Notifier.notify_abstention()` logs them at INFO; `DetectHornetVisual.run()` returns `DetectionRun` counts (threats, abstentions). Dossier: spec `live-abstain`, ADR-0009, sequence + class diagrams, traceability, conception gate signed by the owner before code.
  - **Decisions** — ADR-0009: separate floor flag (440 vs detector at 0.0 410 vs derived floor 370); abstentions through the notifier port (470 vs returned list 370 vs direct logging 300); abstentions logged at INFO (owner choice at the gate).
  - **Review cycle** — local report: Must 1 (run results kept in memory without bound on a live camera → counts), Should 3 fixed, 1 disagree (INFO volume, intentional); Nice items deferred to the test-hygiene brick. CI green. Post-merge SonarQube on `main`: gate OK, coverage 88.5 %.
  - **Issue #18** — kept open by owner decision (470 vs split 430 vs close 240): abstention sub-tasks ticked; the measured zero-bee threshold still waits for an annotated own-data set (M5).
- **PR #60 merged** (`85b0226`) — `test: fix root collection, deselect integration by default, fill test gaps (B3)`. Branch `test/b3-test-hygiene`, squash-merged. Brick B3, audit M1, M2, S5, S7, N3, N4 fixed: root `pytest` collects without tensorflow; `integration`/`e2e` deselected by default (`make test-integration` still selects them); CI and `make sonar` run the default selection, with headless OpenCV so the video-source tests run on every PR; `VespAIDetector` load/detect unit-tested with fake `torch`/`cv2` modules (including the `torch.load` restore on failure); B4 deferred test items done. S6 left to the `training/` removal brick. Dossier: spec `test-hygiene`, conception gate signed by the owner before code.
  - **Decisions** — `importorskip` + default marker deselection (455 vs `collect_ignore` 380 vs deleting the training tests 305); detector tests in this brick with boundary fakes (370 vs deferring to own-data integration 360); headless OpenCV in CI (440 vs local-only 310 vs fake cv2 270).
  - **Review cycle** — local report: Must 0, Should 4 fixed (tautological operating-point invariant, explicit-path deselection documented, `make sonar` aligned with CI, OpenCV tests not run in CI). CI green. Post-merge SonarQube on `main`: gate OK, coverage 96.9 %.
