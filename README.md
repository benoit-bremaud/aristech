# Aristech

Aristech est un dispositif de défense des apiculteurs contre le frelon
asiatique (*Vespa velutina*). Il combine vision par ordinateur, détection
audio, mesure de distance (stéréo + ToF) et un actionneur (coil-gun, servo,
laser de visée) pour détecter et neutraliser les frelons à proximité
d'un rucher.

## État

Pre-alpha. L'ossature **Clean Architecture** est en place ; les adaptateurs
matériels (caméras, micros, GPIO, MQTT/LoRaWAN) restent à implémenter.

## Architecture

Quatre couches concentriques, dépendances dirigées vers le centre :

```text
interface ─▶ infrastructure ─▶ application ─▶ domain
```

- **`domain/`** — entités pures (dataclasses, aucun I/O).
- **`application/`** — use cases et **ports** (`Protocol`). On y spécifie
  *ce que* le système fait, jamais *comment*.
- **`infrastructure/`** — adaptateurs concrets : OpenCV, PyAudio, GPIO,
  TensorFlow/Torch, MQTT/LoRaWAN.
- **`interface/cli/`** — point d'entrée et composition root.

Détail complet : [`docs/architecture.md`](docs/architecture.md).

## Layout

```text
aristech/
├── pyproject.toml              # PEP 621 — config projet et outils
├── requirements.{in,txt}       # gérés par pip-tools (make lock)
├── Makefile                    # raccourcis dev
├── src/aristech/
│   ├── __main__.py             # `python -m aristech`
│   ├── domain/                 # entités
│   ├── application/
│   │   ├── use_cases/
│   │   └── ports/              # Protocols
│   ├── infrastructure/         # adaptateurs (vide pour l'instant)
│   ├── interface/cli/main.py   # composition root
│   └── training/               # pipelines ML
├── tests/{unit,integration,e2e}/
├── config/                     # config.yaml, logging.yaml
└── docs/                       # architecture, BOM, DIY, INSTALL
```

## Installation

Prérequis : Python ≥ 3.10.

```bash
git clone https://github.com/benoit-bremaud/aristech.git
cd aristech

python -m venv venv
source venv/bin/activate            # Linux/macOS
# .\venv\Scripts\activate           # Windows

pip install -e ".[dev]"
pre-commit install
```

Extra GPU (Linux x86_64 uniquement) :

```bash
pip install -e ".[dev,gpu]"
```

Détails plateforme + dépendances système (`portaudio` pour `pyaudio`,
etc.) : [`docs/INSTALL.md`](docs/INSTALL.md).

## Utilisation

```bash
# Lancer la boucle principale
python -m aristech --config config/config.yaml
# ou (après pip install) :
aristech --config config/config.yaml
```

Configuration : éditer [`config/config.yaml`](config/config.yaml) et
[`config/logging.yaml`](config/logging.yaml). Pour les chemins data, voir
[`.env.example`](.env.example).

## Entraînement

```bash
# Préparer la répartition train/val/test des images
python scripts/distribute_images.py

# Lancer l'entraînement (lit .env, écrit dans models/)
make train     # ou : python scripts/train_model.py
```

Les modèles entraînés (`models/*.keras`) ne sont **pas** versionnés —
ils se régénèrent depuis le pipeline `aristech.training.*`. Voir
[`models/README.md`](models/README.md) pour la convention.

## Développement

```bash
make test          # tous les tests
make test-unit     # rapides, sans matériel
make lint          # ruff
make type-check    # mypy strict
make format        # ruff format + autofix
make lock          # pip-compile requirements.in
```

CI : GitHub Actions exécute ruff, ruff-format, mypy strict et pytest sur
Python 3.10–3.12 à chaque push et pull request
([`.github/workflows/ci.yml`](.github/workflows/ci.yml)).

## Contribution

Voir [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md). Convention de
commits : [Conventional Commits](https://www.conventionalcommits.org/).

Maintenance / purge d'historique : [`docs/MAINTENANCE.md`](docs/MAINTENANCE.md).

1. Fork → branche `feat/<sujet>` ou `fix/<sujet>`
2. Faire passer `make lint test type-check` localement
3. Pull request ciblant `main`

## Licence

MIT — voir [`LICENSE`](LICENSE).
