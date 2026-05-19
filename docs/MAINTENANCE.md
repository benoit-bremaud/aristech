# Maintenance — nettoyage du dépôt

## Pourquoi ce document

Le dépôt a porté pendant un temps deux modèles entraînés (`hornet_recognition_model.h5`
et `model.keras`, ~40 MB chacun). Ils ont été retirés du working tree dans la
refonte Clean Architecture, mais **les blobs Git restent dans l'historique
(`.git/objects/`)** tant que l'historique n'est pas réécrit.

Tant que personne ne purge, un `git clone` télécharge les ~80 MB.

## Procédure de purge (réécrit l'historique)

> ⚠️ Destructif. Réécrit tous les commits qui touchent ces fichiers.
> À faire en pleine conscience, idéalement juste après le merge de
> `refactor/clean-architecture` sur `main`, **avant** de pousser le
> nouveau `main` à des collaborateurs.

```bash
# 1. Sauvegarde du repo, par sécurité.
cp -r aristech aristech.backup

# 2. Installer git-filter-repo (recommandé sur BFG).
pip install git-filter-repo
# ou: brew install git-filter-repo

# 3. Purger les blobs des modèles.
git filter-repo \
  --invert-paths \
  --path hornet_recognition_model.h5 \
  --path model.keras \
  --path models/hornet_recognition_model.h5 \
  --path models/model.keras \
  --path update_requirements.py \
  --path setup.py

# 4. Garbage-collect pour libérer l'espace.
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Vérifier le résultat.
du -sh .git
```

Le `.git/` devrait tomber de ~61 MB à ~1 MB.

## Force-push si remote

Si tu as un remote (origin) avec ces commits déjà poussés :

```bash
git push --force-with-lease --all
git push --force-with-lease --tags
```

`--force-with-lease` est plus sûr que `--force` brut : il refuse si quelqu'un
d'autre a poussé entre temps.

## Pour les collaborateurs (s'il y en a)

Après le force-push, **chaque clone existant doit être refait** :

```bash
cd ..
rm -rf aristech
git clone <url> aristech
```

Un simple `git pull` ne suffit pas après une réécriture d'historique.

## Distribution future des modèles

Comme les `.keras` ne sont plus versionnés (cf. `models/README.md`), il faut
un canal de distribution. Trois pistes :

- **GitHub Releases** : attache le `.keras` à une release, ajoute un
  `scripts/download_model.py` qui fait un `curl -L` sur l'URL de release.
- **HuggingFace Hub** : `huggingface-cli upload` du dossier `models/`,
  puis `huggingface-cli download` au runtime.
- **S3 / object storage privé** : `boto3` ou `mc` pour push/pull.

Mon conseil : commencer par GitHub Releases (zéro infra), migrer vers
HuggingFace quand on veut publier le modèle.
