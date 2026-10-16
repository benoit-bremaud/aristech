# Workflow de développement

Notes de workflow internes pour aristech. Le dépôt est **privé** et
mené en R&D ; ce document décrit les conventions appliquées (du commit
au merge), pas une procédure de recrutement de contributeurs externes.
Il sert de référence au mainteneur et à tout collaborateur qui
rejoindrait le projet plus tard.

## Installation dev

```bash
git clone git@github.com:benoit-bremaud/aristech.git
cd aristech

python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## Conventions de branche

Toujours brancher depuis `main`. Jamais de commit direct sur `main`.

| Préfixe            | Pour quoi                                          |
| ------------------ | -------------------------------------------------- |
| `feat/<sujet>`     | nouvelle fonctionnalité                            |
| `fix/<sujet>`      | correction de bug                                  |
| `docs/<sujet>`     | documentation seulement                            |
| `research/<sujet>` | veille technique, ajout d'une étude                |
| `chore/<sujet>`    | hygiène repo, refactor sans changement fonctionnel |
| `ci/<sujet>`       | modification des workflows CI                      |

## Cycle de travail

1. Créer la branche dédiée.
2. Développer. Faire passer localement :

   ```bash
   make lint type-check test
   ```

3. Commit au format [Conventional Commits](https://www.conventionalcommits.org/) :

   ```text
   feat(application): add DetectHornetAudio use case
   fix(infrastructure): close OpenCV VideoCapture on exception
   docs(research): add Hall et al. 2025 to acoustic section
   ```

4. Pull request vers `main`. Le template
   (`.github/PULL_REQUEST_TEMPLATE.md`) s'applique automatiquement —
   compléter chaque section.

5. Revue : CI (ruff, mypy, pytest 3.10-3.12) + revue automatique
   (Copilot, parfois Codex). Adresser chaque commentaire inline avec la
   référence du commit qui le corrige.

6. Merge `squash & delete branch` par défaut, puis cleanup local :

   ```bash
   git checkout main && git pull
   git branch -d <branche>   # -D si besoin : un squash-merge laisse souvent la branche « non mergée » aux yeux de git
   git remote prune origin
   ```

## Standards de code

### Python

- **mypy strict** doit passer sur `src/` (sauf override explicite dans
  `pyproject.toml` pour `infrastructure/`).
- **Pas de `Any` non justifié.** Si nécessaire, commenter pourquoi.
- **Exports nommés** explicites via `__all__`.
- **Conventions Clean Architecture** ([architecture.md](architecture.md)) :
  le `domain` ne dépend de rien ; les `application/ports` sont des
  `Protocol` ; les implémentations concrètes vivent dans
  `infrastructure/`.

### Style

- **ruff** pour le lint et le format (`pyproject.toml`). Faire passer
  `make format lint` avant commit.
- **Pas de commentaire évident** : un commentaire explique un *pourquoi*
  non trivial, jamais un *quoi* déductible du code.
- **Docstrings** courtes et factuelles sur les ports et use cases.

### Tests

- **Tests obligatoires** pour toute nouvelle fonctionnalité ou
  correction de bug.
- **Hiérarchie** :

  | Niveau                       | Périmètre                                     | Marqueur pytest     |
  | ---------------------------- | --------------------------------------------- | ------------------- |
  | `tests/unit/domain/`         | entités pures                                 | aucun               |
  | `tests/unit/application/`    | use cases avec fakes des ports                | aucun               |
  | `tests/unit/infrastructure/` | adaptateurs, parfois fixtures                 | `integration` si HW |
  | `tests/integration/`         | plusieurs couches enchaînées, sans hardware   | `integration`       |
  | `tests/e2e/`                 | bout en bout, peut nécessiter du matériel     | `e2e`               |

- **Fakes plutôt que mocks** : implémenter le `Protocol` cible dans une
  classe locale au test. Plus lisible, plus typesafe.

## Sécurité

- **Jamais de secrets** dans le code, les commits, ou les exemples.
  `.env.example` ne contient que des placeholders.
- **Pas de force-push sur `main`.**
- **Plancher légal aristech** (Art. L411-1 + L415-3 Code env.) : toute
  fonctionnalité pouvant blesser un pollinisateur doit défaut à
  l'abstention. Voir [architecture.md § Plancher légal](architecture.md).

## Discipline documentaire

Voir [docs/INDEX.md](INDEX.md) pour la carte des documents. Règles :

- Pas de `[[wikilinks]]` Obsidian — uniquement des liens Markdown
  standards `[text](path.md)`.
- Toute URL citée dans un narratif va aussi dans
  [docs/research/references.md](research/references.md).
- Les décisions architecturales sont consignées **à la fois** dans
  [PROJECT_LOG.md](../PROJECT_LOG.md) (sous-bullet de l'entrée PR) et
  dans [architecture.md](architecture.md) (section "Décisions
  ouvertes").
- `markdownlint` doit passer (`npx markdownlint-cli <file>`) avant
  commit.

## Suivi interne

Le suivi des tâches et des PRs passe par le GitHub Project
**aristech #57**. Les bugs et idées de fonctionnalités se notent en issues
rattachées au projet, classées par couche Clean Architecture concernée
(`domain` / `application` / `infrastructure` / `interface`) — utile pour
savoir où une modification atterrit.
