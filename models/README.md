# models/

Ce dossier accueille les poids de modèles locaux. **Aucun n'est versionné.**

## Convention

| Fichier attendu | Source | Statut Git |
| --- | --- | --- |
| poids VespAI (`*.pt`) | fournis par l'opérateur (CC BY-NC-SA), passés via `--weights` | gitignoré |

Patterns ignorés : `models/*.keras`, `models/*.h5`, `models/*.pth`,
`models/*.pt` — voir [`.gitignore`](../.gitignore).

Le pipeline d'entraînement Keras historique a été retiré (ADR-0010) ; le
fine-tune YOLO sur données propres est prévu en M5.

## Récupérer un modèle pré-entraîné (à venir)

Une fois la stratégie de distribution choisie (GitHub Releases, HuggingFace
Hub, S3…), un script `scripts/download_model.py` fera le `wget` / `huggingface-cli
download` correspondant.
