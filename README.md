# aristech

aristech detects the Asian hornet (*Vespa velutina*) in real time in front of a beehive, as the
first step towards a **non-lethal** deterrent (an aimed water jet) that keeps hornets away from
the foragers above the landing board **without ever harming a bee or another protected
pollinator**.

## Positioning

- **Non-lethal, non-contact**: aristech does not kill the hornet, it drives it away. No bodies to
  handle, no daily upkeep.
- **A complement to the electric harp** (benchmark published by IRBI Tours: > 90 % *V. velutina*
  in the catch, < 2 % non-target), not a competitor. A side-by-side comparison is planned for the
  field validation.
- **Hard-coded legal floor**: harming a protected pollinator is a criminal offence in France
  (Code de l'environnement L411-1 + L415-3, up to 3 years in prison and € 150,000). The decision
  abstains by default when a target is uncertain; a geometric exclusion zone around the landing
  board will apply independently.

## Status

**Pre-alpha — detection pipeline built, prototype not started.**

| Area | Status |
|---|---|
| Clean Architecture (4 layers, 3 ports) | ✅ ([docs/architecture.md](docs/architecture.md)) |
| Live detection: `DetectHornetVisual`, legal-floor `decide()`, OpenCV source, VespAI YOLOv5 detector, logging notifier | ✅ |
| Offline evaluation and operating-point selection | ✅ (`aristech.evaluation`) |
| VespAI transfer to other footage | ⚠️ low recall measured; fine-tune on own data planned (M5) |
| Technical and legal survey | ✅ ([docs/research/state-of-the-art.md](docs/research/state-of-the-art.md)) |
| Engineering constants (biology / geometry / BOM) | ✅ ([docs/research/prototype-foundations.md](docs/research/prototype-foundations.md)) |
| Hardware prototype and deterrent | 🔲 gated on the D0 field test |

## Documentation

[**docs/INDEX.md**](docs/INDEX.md) is the single entry point to every document, by role. Main
axes:

1. **Architecture and design** → [docs/architecture.md](docs/architecture.md) (overview),
   [docs/architecture/](docs/architecture/README.md) (design dossier),
   [docs/decisions/](docs/decisions/README.md) (ADRs)
2. **Research** → [state of the art](docs/research/state-of-the-art.md),
   [prototype foundations](docs/research/prototype-foundations.md),
   [references](docs/research/references.md)
3. **Operational logbook** → [PROJECT_LOG.md](PROJECT_LOG.md) (PR by PR)

## Layout

```text
aristech/
├── pyproject.toml              # PEP 621 project and tool configuration
├── requirements.{in,txt}       # pinned lock of the vision stack (make lock)
├── Makefile                    # dev shortcuts
├── PROJECT_LOG.md              # chronological logbook
├── src/aristech/
│   ├── domain/                 # pure types, stdlib only
│   ├── application/            # use case, decide(), ports
│   ├── infrastructure/         # OpenCV, VespAI, logging adapters
│   ├── interface/cli/main.py   # composition root
│   ├── evaluation/             # offline metrics
│   └── datasets/               # train/validation/test split
├── scripts/                    # dataset split, operating-point measurement
├── tests/{unit,integration,e2e}/
├── config/                     # config.yaml, logging.yaml
└── docs/                       # INDEX, architecture, decisions, research, INSTALL, MAINTENANCE
```

## Installation

Requires Python ≥ 3.11.

```bash
git clone https://github.com/benoit-bremaud/aristech.git
cd aristech
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,vision]"
mise install                         # local CI tools (mise.toml)
mise x -- lefthook install           # git hooks: just fast on commit, just check on push
```

Platform details and the GPU extra: [docs/INSTALL.md](docs/INSTALL.md).

## Usage

```bash
aristech --video path/to/clip.mp4 --weights path/to/vespai.pt --yolov5-dir path/to/yolov5
```

`--video` also accepts a camera index. VespAI weights are CC BY-NC-SA: they are loaded from a path
and never committed (see [models/README.md](models/README.md)). Configuration lives in
[config/config.yaml](config/config.yaml) and [config/logging.yaml](config/logging.yaml);
dataset paths in [.env.example](.env.example). `aristech --help` lists every flag.

## Development

```bash
mise x -- just check   # local CI, also run by the pre-push hook
mise x -- just gate    # before merge: check + Python 3.12 tests + SonarQube
make test-unit         # fast tests, no hardware
make format            # ruff format + autofix
make lock              # relock requirements.txt
```

Checks run locally (ADR-0027, ADR-0028); GitHub Actions keeps only the public-repository security
baseline (CodeQL, OpenSSF Scorecard, dependency review). Workflow, branches and conventions: [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).
History purge procedure: [docs/MAINTENANCE.md](docs/MAINTENANCE.md).

## License

MIT ([LICENSE](LICENSE)). VespAI weights, when used, keep their own CC BY-NC-SA licence.
