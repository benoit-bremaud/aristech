# Maintenance — repository cleanup

## Why this document

The repository once carried two trained models (`hornet_recognition_model.h5` and `model.keras`,
~40 MB each). They left the working tree during the Clean Architecture refactor, but **their Git
blobs stay in the history (`.git/objects/`)** until the history is rewritten.

Until someone purges them, a `git clone` downloads the ~80 MB.

## Purge procedure (rewrites history)

> ⚠️ Destructive. Rewrites every commit that touches these files, and needs a force-push of
> `main`, which the branch rules forbid by default: an explicit owner decision is required first.

```bash
# 1. Back up the repository.
cp -r aristech aristech.backup

# 2. Install git-filter-repo (preferred over BFG).
pip install git-filter-repo
# or: brew install git-filter-repo

# 3. Purge the model blobs.
git filter-repo \
  --invert-paths \
  --path hornet_recognition_model.h5 \
  --path model.keras \
  --path models/hornet_recognition_model.h5 \
  --path models/model.keras \
  --path update_requirements.py \
  --path setup.py

# 4. Garbage-collect to free the space.
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Check the result.
du -sh .git
```

`.git/` should drop from ~61 MB to ~1 MB.

## Force-push to the remote

If the remote already holds these commits:

```bash
git push --force-with-lease --all
git push --force-with-lease --tags
```

`--force-with-lease` is safer than a bare `--force`: it refuses if someone else pushed in between.

## For collaborators

After the force-push, **every existing clone must be recreated**:

```bash
cd ..
rm -rf aristech
git clone <url> aristech
```

A plain `git pull` is not enough after a history rewrite.

## Future model distribution

Weights are not versioned (see [models/README.md](../models/README.md)), so they need a
distribution channel. Three options:

- **GitHub Releases**: attach the weights to a release and add a `scripts/download_model.py` that
  fetches the release URL.
- **Hugging Face Hub**: `huggingface-cli upload` of `models/`, then `huggingface-cli download` at
  runtime.
- **S3 / private object storage**: `boto3` or `mc` for push and pull.

Starting point: GitHub Releases (no infrastructure), moving to Hugging Face once the model is
published. VespAI weights are CC BY-NC-SA and cannot be redistributed as ours; only weights we
train ourselves (M5) are candidates.
