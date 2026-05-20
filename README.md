# Aristech

Aristech est un dispositif de **défense non létale** des apiculteurs
contre le frelon asiatique (*Vespa velutina*). Il combine :

- **vision par ordinateur** (discrimination *V. velutina* vs *Apis
  mellifera* à l'entrée de la ruche),
- **détection acoustique** (signature de vol stationnaire, complément
  vision et signal de réveil),
- **mesure de distance** (capteur ToF pour la cible 3D),
- et un **actionneur non létal** (jet d'eau orienté par servos pan/tilt)

pour **dissuader** les frelons qui chassent les butineuses au-dessus
de la planche d'envol, **sans jamais blesser une abeille ni un autre
pollinisateur protégé**.

## Positionnement

- **Non létal**, **non contact** : aristech ne tue pas le frelon, il
  l'éloigne. Pas de cadavre à gérer, pas d'entretien quotidien.
- **Complément de la harpe électrique** (benchmark publié par
  l'IRBI Tours : > 90 % *V. velutina* dans la capture, < 2 % non-cible),
  pas un concurrent. Comparaison side-by-side prévue en campagne de
  validation.
- **Plancher légal hardcodé** : blesser un pollinisateur protégé est
  pénal (Art. L411-1 + L415-3 Code de l'environnement, jusqu'à 3 ans
  de prison + 150 000 €). Le classifier d'espèces a un défaut
  d'abstention ; une zone d'exclusion géométrique autour de la planche
  est appliquée indépendamment.

## État

**Pre-alpha — phase recherche close, phase prototype à démarrer.**

| Couche | État |
|---|---|
| Architecture Clean (4 couches, 8 ports) | ✅ en place ([docs/architecture.md](docs/architecture.md)) |
| Domain + Application + 1 use case (`DetectHornetVisual`) | ✅ implémentés, 7 tests unitaires verts |
| Infrastructure (adaptateurs concrets) | ❌ vides, à câbler |
| Veille technique + juridique | ✅ 5 axes ([docs/research/state-of-the-art.md](docs/research/state-of-the-art.md)) |
| Constantes d'engineering (biologie / géométrie / BOM) | ✅ ([docs/research/prototype-foundations.md](docs/research/prototype-foundations.md)) |
| Hardware prototype | 🚧 BOM dimensionné, sourcing à faire |
| Validation terrain | 🔲 à venir (partenariat apiculteur) |

## Documentation

[**docs/INDEX.md**](docs/INDEX.md) — entrée unique vers tous les
documents du projet, par rôle.

Trois axes principaux :

1. **Architecture & design** → [docs/architecture.md](docs/architecture.md)
2. **Recherche** → [docs/research/state-of-the-art.md](docs/research/state-of-the-art.md) (veille) + [docs/research/prototype-foundations.md](docs/research/prototype-foundations.md) (constantes prototype) + [docs/research/references.md](docs/research/references.md) (bibliographie)
3. **Logbook opérationnel** → [PROJECT_LOG.md](PROJECT_LOG.md) (chronologie PR par PR)

## Architecture en bref

Quatre couches concentriques, dépendances dirigées vers le centre :

```text
interface ─▶ infrastructure ─▶ application ─▶ domain
```

- **`domain/`** — entités pures (frozen dataclasses, aucun I/O).
- **`application/`** — use cases et **ports** (`Protocol`). *Ce que*
  fait le système, jamais *comment*.
- **`infrastructure/`** — adaptateurs concrets : OpenCV, micro I²S,
  ToF, servos GPIO, pompe + solénoïde, MQTT.
- **`interface/cli/`** — composition root.

Détail complet : [docs/architecture.md](docs/architecture.md).

## Layout

```text
aristech/
├── pyproject.toml              # PEP 621 — config projet et outils
├── requirements.{in,txt}       # gérés par pip-tools (make lock)
├── Makefile                    # raccourcis dev
├── PROJECT_LOG.md              # logbook chronologique
├── src/aristech/
│   ├── __main__.py             # `python -m aristech`
│   ├── domain/                 # entités
│   ├── application/
│   │   ├── use_cases/
│   │   └── ports/              # Protocols (DIP)
│   ├── infrastructure/         # adaptateurs (vide pour l'instant)
│   ├── interface/cli/main.py   # composition root
│   └── training/               # pipelines ML
├── tests/{unit,integration,e2e}/
├── config/                     # config.yaml, logging.yaml
└── docs/                       # INDEX, architecture, research/, INSTALL, MAINTENANCE
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
etc.) : [docs/INSTALL.md](docs/INSTALL.md).

## Utilisation

```bash
# Lancer la boucle principale (composition root encore minimale)
python -m aristech --config config/config.yaml
# ou (après pip install) :
aristech --config config/config.yaml
```

Configuration : éditer [config/config.yaml](config/config.yaml) et
[config/logging.yaml](config/logging.yaml). Pour les chemins data, voir
[.env.example](.env.example).

## Entraînement

```bash
# Préparer la répartition train/val/test des images
python scripts/distribute_images.py

# Lancer l'entraînement (lit .env, écrit dans models/)
make train     # ou : python scripts/train_model.py
```

Les modèles entraînés (`models/*.keras`) ne sont **pas** versionnés ;
ils se régénèrent depuis le pipeline `aristech.training.*`. Convention
de distribution à trancher (cf. décision `models-out-of-tree` dans
[PROJECT_LOG.md](PROJECT_LOG.md)).

## Développement

```bash
make test          # tous les tests
make test-unit     # rapides, sans matériel
make lint          # ruff
make type-check    # mypy strict
make format        # ruff format + autofix
make lock          # pip-compile requirements.in
```

CI : GitHub Actions exécute ruff, ruff-format, mypy strict et pytest
sur Python 3.10-3.12 à chaque push et pull request
([.github/workflows/ci.yml](.github/workflows/ci.yml)).

## Développement interne

Projet **privé**, en R&D. Le workflow de développement (conventions de
branche, Conventional Commits, standards de code, hiérarchie de tests,
discipline documentaire) est décrit dans
[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

Discipline PR (appliquée même en solo) :

1. Branche `feat/<sujet>` / `fix/<sujet>` / `docs/<sujet>` / `research/<sujet>` depuis `main`
2. `make lint type-check test` localement avant push
3. Pull request ciblant `main` ([template](.github/PULL_REQUEST_TEMPLATE.md))

Maintenance et purge d'historique : [docs/MAINTENANCE.md](docs/MAINTENANCE.md).

## Licence

MIT (fichier [LICENSE](LICENSE)). Le dépôt reste **privé** : la licence
MIT documente l'intention de réutilisation mais n'implique aucune
publication tant que la visibilité n'est pas changée.
