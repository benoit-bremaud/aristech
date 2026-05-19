# models/

Ce dossier accueille les modèles ML entraînés. **Aucun n'est versionné**
— les binaires Keras / Torch sont des artefacts reproductibles à partir
des scripts d'entraînement (cf. `scripts/train_model.py`).

## Convention

| Fichier attendu | Source | Statut Git |
| --- | --- | --- |
| `hornet_image_model.keras` | `scripts/train_model.py` (CNN binaire Keras) | gitignoré |
| `hornet_sound_model.keras` | (à venir) classification audio | gitignoré |

Patterns ignorés : `models/*.keras`, `models/*.h5`, `models/*.pth`,
`models/*.pt` — voir [`.gitignore`](../.gitignore).

## Comment obtenir les modèles

### Reproduire par entraînement

```bash
# Prérequis : .env peuplé (TRAIN/VALIDATION/TEST_FOLDER), données dans data/
make train      # ou : python scripts/train_model.py
```

Le modèle est écrit dans `models/hornet_image_model.keras`.

### Récupérer un modèle pré-entraîné (à venir)

Une fois la stratégie de distribution choisie (GitHub Releases, HuggingFace
Hub, S3…), un script `scripts/download_model.py` fera le `wget` / `huggingface-cli
download` correspondant.
