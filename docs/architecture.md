# Architecture — Aristech

## Objectif

Détecter et neutraliser le frelon asiatique (*Vespa velutina*) en temps
réel à proximité d'un rucher, à partir de capteurs vidéo, audio, et de
mesure de distance, puis piloter un actionneur (laser de visée, coil-gun,
servo).

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
- `hardware/` — RPi.GPIO pour coil-gun, servo, laser, panneau solaire.
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
                                                    ┌────────────┐
                                                    │  Actuator  │
                                                    │ (coil-gun) │
                                                    └────────────┘
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
tant que les choix produit suivants ne sont pas tranchés :

1. **Létalité** — coil-gun (létal) vs laser de dispersion / jet d'eau
   (non létal) vs alerte seulement.
2. **Fusion multi-modale** — la décision de tirer exige-t-elle vision
   **ET** audio concordants, ou un seul des deux suffit ?
3. **Fail-safe** — mode `dry-run` par défaut, tir activé seulement par
   un flag explicite dans la config ?
4. **Espèces protégées** — `Detection.is_threat()` ne renvoie `True`
   que pour `VESPA_VELUTINA`. Cette règle métier doit rester
   centralisée et auditable.
