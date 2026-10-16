# Installation

## Prérequis

- Python ≥ 3.10
- `pip` ≥ 23
- Sous Linux x86_64 avec GPU NVIDIA : drivers CUDA récents si l'extra
  `gpu` est installé.
- `portaudio` pour PyAudio :

  ```bash
  sudo apt-get install -y portaudio19-dev   # Debian/Ubuntu
  brew install portaudio                    # macOS
  ```

## Étapes

```bash
git clone https://github.com/benoit-bremaud/aristech.git
cd aristech

python -m venv venv
source venv/bin/activate            # Linux/macOS
# .\venv\Scripts\activate           # Windows

pip install -e ".[dev]"
pre-commit install
```

### Extras disponibles

- `dev` — pytest, ruff, mypy, pip-tools.
- `gpu` — libs NVIDIA CUDA (Linux x86_64 uniquement).

```bash
pip install -e ".[dev,docs]"
pip install -e ".[dev,gpu]"     # cible Linux GPU
```

## Configuration

Deux fichiers YAML pilotent l'application :

- [`config/config.yaml`](../config/config.yaml) — caméras, seuils de
  détection, broches GPIO, modules (solar, sonar, connect…).
- [`config/logging.yaml`](../config/logging.yaml) — journalisation.

Le code charge `config/config.yaml` par défaut ; un autre chemin peut
être passé :

```bash
aristech --config /chemin/vers/mon-config.yaml
```

### Variables d'environnement

Les sujets sensibles (clé API LoRaWAN, identifiants MQTT…) ont leur place
dans un fichier `.env` non versionné, chargé par l'application au
démarrage. Aucun `.env` n'est requis pour la chaîne par défaut (caméra
locale, modèles sur disque).

## Reproductibilité du lock

`requirements.in` liste les dépendances de haut niveau.
`requirements.txt` est un **lock** généré par `pip-compile` ; le
régénérer sur la plateforme cible :

```bash
make lock
```

Ne **pas** coller un `pip freeze` brut : il inclurait les libs CUDA
spécifiques à la machine, qui doivent rester dans l'extra `gpu`.

## Vérification

```bash
make test-unit
aristech --help
```

Si `aristech --help` affiche l'usage, l'install est bonne.
