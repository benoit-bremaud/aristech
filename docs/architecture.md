# Architecture — Aristech

## Objectif

Détecter et **éloigner** le frelon asiatique (*Vespa velutina*) en
temps réel à proximité d'un rucher, à partir de capteurs vidéo, audio,
et de mesure de distance, puis piloter un actionneur **non létal**
(jet d'eau orienté, servo de visée pan/tilt). Cf.
[Décisions ouvertes](#décisions-ouvertes).

## Principe : Clean Architecture

Le code est organisé en quatre couches concentriques. **La règle de
dépendance va toujours de l'extérieur vers l'intérieur** :

```text
┌─────────────────────────────────────────────────────────────┐
│  interface/   (CLI, composition root, futur API)            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  infrastructure/   (OpenCV, PyAudio, GPIO, TF, MQTT)  │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  application/   (use cases + ports)             │  │  │
│  │  │  ┌───────────────────────────────────────────┐  │  │  │
│  │  │  │  domain/   (entités, valeur, aucun I/O)   │  │  │  │
│  │  │  └───────────────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

`domain` ne dépend de rien. `application` ne dépend que de `domain`.
`infrastructure` implémente les ports déclarés dans `application`.
`interface` assemble le tout (composition root).

## Couches

### `domain/` — Entités

Modèles métier purs, sans I/O ni dépendance externe (hors stdlib +
`dataclasses`). Implémentés :

- `Species` — `VESPA_VELUTINA`, `VESPA_CRABRO`, `APIS_MELLIFERA`,
  `UNKNOWN`.
- `BoundingBox`, `Point2D`, `Point3D` — géométrie.
- `VideoFrame`, `AudioSample` — données capteur.
- `Detection` — `species + bbox + confidence + timestamp`, avec
  `is_hornet()` et `is_threat()`.
- `Target` — entité de piste (UUID + position 3D + confiance + last_seen).

### `application/` — Use cases et ports

#### `use_cases/`

Cas d'usage = orchestrations sans connaissance des frameworks.

| Implémenté | Use case | Rôle |
| --- | --- | --- |
| ✓ | `DetectHornetVisual` | Frames → détections filtrées par seuil → notification |
|   | `DetectHornetAudio` | Sample → classification → score |
|   | `MeasureTargetDistance` | Fusion stéréo + ToF sur une bbox |
|   | `TrackTarget` | Association temporelle des détections |
|   | `NeutralizeTarget` | Décision + commande actionneur (use case sensible, voir [Décisions ouvertes](#décisions-ouvertes)) |

#### `ports/`

Interfaces (`Protocol`) que `infrastructure` doit implémenter. Permet
de mocker proprement en test (les fakes des tests sont des classes
locales qui implémentent simplement le protocole — duck typing structurel).

| Port | Méthode(s) |
| --- | --- |
| `VideoSource` | `frames() -> Iterator[VideoFrame]`, `close()` |
| `AudioSource` | `samples() -> Iterator[AudioSample]`, `close()` |
| `HornetDetector` | `detect(frame) -> Sequence[Detection]` |
| `SoundClassifier` | `classify(sample) -> tuple[Species, float]` |
| `DistanceSensor` | `distance_to(bbox) -> float \| None` |
| `Actuator` | `aim(target)`, `fire()`, `safe()` |
| `Notifier` | `notify_detection(detection)` |
| `Clock` | `now() -> datetime` (testabilité du temps) |

### `infrastructure/` — Adaptateurs

Implémentations concrètes des ports. Tout ce qui touche au matériel ou
à une lib externe vit ici. Sous-dossiers prévus :

- `vision/` — OpenCV, YOLO (Torch/TensorFlow).
- `audio/` — PyAudio, librosa.
- `distance/` — caméras stéréo, capteurs ToF.
- `hardware/` — RPi.GPIO pour servos pan/tilt, pompe + solénoïde du jet
  d'eau, capteurs et panneau solaire.
- `connectivity/` — paho-mqtt, LoRaWAN.
- `config/` — chargement YAML.

Pour l'instant, aucun adaptateur n'est livré ; la stratégie est de
**wrapper des baselines existantes** (VespAI pour la vision, modèles
audio Nottingham Trent / Coimbra) plutôt que de tout réécrire.

### `interface/` — Entrées

- `cli/main.py` — point d'entrée `python -m aristech` / `aristech`.
- Composition root : c'est ici qu'on **instancie** les adaptateurs et
  qu'on les injecte dans les use cases. C'est le **seul** endroit où
  `interface` importe `infrastructure`.

### `training/`

Pipelines d'entraînement des modèles (vision, audio, distance). Isolés
du runtime temps réel pour qu'on puisse retravailler les modèles sans
toucher au cœur applicatif.

## SOLID en pratique

Les principes apparaissent naturellement dans le découpage :

- **SRP** — chaque port a une seule raison de changer (capter vidéo,
  classer un son, mesurer une distance…).
- **OCP** — ajouter un nouveau modèle de détection = un nouvel
  adaptateur qui implémente `HornetDetector`. Zéro modification du
  use case.
- **LSP** — les fakes des tests substituent les adaptateurs réels sans
  changement (cf. [`tests/unit/application/test_detect_hornet_visual.py`](../tests/unit/application/test_detect_hornet_visual.py)).
- **ISP** — `VideoSource`, `HornetDetector`, `Notifier` sont 3 ports
  séparés. Rien ne force un implémenteur de notifier à connaître le
  format vidéo.
- **DIP** — `DetectHornetVisual` dépend de 3 Protocols abstraits,
  jamais d'OpenCV ou d'un modèle concret.

## Diagramme de flux runtime

```text
┌──────────────┐  frame   ┌────────────────────┐  detection  ┌──────────────┐
│ VideoSource  │─────────▶│ DetectHornetVisual │────────────▶│ TrackTarget  │
│ (OpenCV)     │          │ (use case)         │             │              │
└──────────────┘          └────────────────────┘             └──────┬───────┘
                                                                    │
┌──────────────┐  sample  ┌────────────────────┐  score             │
│ AudioSource  │─────────▶│ DetectHornetAudio  │────┐               │
│ (PyAudio)    │          │ (use case)         │    │               │
└──────────────┘          └────────────────────┘    ▼               ▼
                                              ┌────────────────────────────┐
┌────────────────┐ range  ┌────────────────────┐ NeutralizeTarget          │
│ DistanceSensor │───────▶│ MeasureDistance    │ (fusion + politique tir)  │
│ (Stéréo+ToF)   │        │ (use case)         └───────────┬──────────────┘
└────────────────┘        └────────────────────┘           │
                                                           ▼
                                                    ┌─────────────┐
                                                    │  Actuator   │
                                                    │ (jet d'eau) │
                                                    └─────────────┘
```

## Tests

| Niveau | Périmètre | Vitesse | Marqueur pytest |
| --- | --- | --- | --- |
| `tests/unit/domain/` | Entités pures | µs | (aucun) |
| `tests/unit/application/` | Use cases via fakes des ports | ms | (aucun) |
| `tests/unit/infrastructure/` | Adaptateurs, parfois besoin de fixtures | ms-s | `integration` si matériel |
| `tests/integration/` | Plusieurs couches enchaînées, pas de hardware | s | `integration` |
| `tests/e2e/` | Bout en bout, peut nécessiter du matériel | min | `e2e` |

Exécution : `make test-unit` (rapide, par défaut), `pytest -m integration`
ou `pytest -m e2e` pour les niveaux plus lourds.

## Décisions ouvertes

Le use case `NeutralizeTarget` n'est volontairement pas implémenté
tant que les choix produit suivants ne sont pas tranchés. Cf.
[docs/research/state-of-the-art.md](research/state-of-the-art.md)
pour la veille technique et juridique qui informe ces décisions, et
[PROJECT_LOG.md](../PROJECT_LOG.md) pour le verrouillage chronologique.

1. **Létalité** — ~~coil-gun (létal) vs laser de dispersion / jet d'eau
   (non létal) vs alerte seulement.~~ **Tranché (PR #4, 2026-05-19) :
   jet d'eau non létal.** Alternatives rejetées : coil-gun (incompatible
   avec le plancher légal — risque pénal sur espèces protégées) ;
   alerte seule (insuffisant pour protéger la colonie pendant les
   attaques soutenues).
2. **Fusion multi-modale** — la décision de tirer exige-t-elle vision
   **ET** audio concordants, ou un seul des deux suffit ? **Ouvert.**
   La veille a confirmé l'absence de baseline publiée multimodale
   (vision + acoustique) pour *V. velutina* — niche scientifique
   ouverte. Architecture cible privilégiée : acoustique en *wake-up
   signal* toujours allumé, vision déclenchée en aval pour confirmer
   l'espèce avant tir.
3. **Fail-safe** — mode `dry-run` par défaut, tir activé seulement par
   un flag explicite dans la config ? **Ouvert** — sera tranché lors
   de la première itération de prototype.
4. **Espèces protégées** — `Detection.is_threat()` ne renvoie `True`
   que pour `VESPA_VELUTINA`. Cette règle métier doit rester
   centralisée et auditable.
5. **Média du dissuasif** (`deterrent-medium-pure-water-vs-projectile`)
   — la **modalité** (jet non létal) est tranchée (cf. point 1), mais le
   **média** ne l'est pas : eau pure (défaut) vs média à impact visible
   (souffle/anneau d'air, bille hydrogel, pellet biodégradable).
   **Ouvert — défaut = eau pure.** Tout projectile solide est **bloqué**
   par trois gardes dures : (a) le plancher légal *eau pure uniquement,
   no biocide* (Code rural L253-1, cf. ci-dessous) restreint ce qu'on
   peut disperser ; (b) la contrainte *ne laisse aucune trace* (l'eau et
   l'air ne laissent rien, un solide dispersé est irrécupérable au
   rucher) ; (c) l'enveloppe non létale (un projectile à vitesse utile
   devient létal pour un frelon de 30 mm). Sera tranché par un **D0
   multi-bras** (eau pulsée vs souffle d'air vs pellet bridé) — protocole
   dans [docs/research/prototype-foundations.md § A](research/prototype-foundations.md).

## Plancher légal — contrainte d'architecture (PR #4)

La veille juridique (cf. [docs/research/state-of-the-art.md § Legal
framework](research/state-of-the-art.md)) a établi que **blesser ou
capturer un pollinisateur protégé est pénal** sous **Art. L411-1 +
L415-3 du Code de l'environnement** (3 ans de prison + 150 000 €
d'amende, 7 ans + 750 000 € en bande organisée). La règle « ne jamais
arroser une abeille » n'est donc plus une contrainte éthique mais une
contrainte criminelle.

Conséquences sur l'architecture :

- Le classifier d'espèces doit avoir un **default d'abstention** :
  toute confiance sous le seuil (≥ 0.9 visé pour `VESPA_VELUTINA`)
  bloque l'actionneur. *Mieux vaut un tir manqué qu'un tir illégal.*
- Une **zone d'exclusion géométrique** autour de la planche d'envol
  doit être appliquée indépendamment du classifier, par sécurité
  défense en profondeur. Si une bbox `APIS_MELLIFERA` chevauche le
  cône de tir, arrêt immédiat de l'actionneur.
- Toute activité de type « piège » doit être **sélective** (Art.
  L411-9-1 du Code env., introduit par la **Loi n° 2025-237 du
  14 mars 2025**) ; la valeur exacte du seuil de sélectivité sera
  définie par le *plan national de lutte* (publication attendue
  courant 2026 — cible mobile à surveiller).
- Pas de **biocide ou phytosanitaire** dans le jet d'eau sans
  homologation (Code rural L253-1+). Eau pure uniquement.
