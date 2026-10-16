# Architecture — aristech (overview)

One-page overview of the system **as built**. The design dossier in
[docs/architecture/](architecture/README.md) (specs, UML, gates, reviews) and the
[ADRs](decisions/README.md) are the source of truth; this page only orients a new reader.

## Purpose

Detect the Asian hornet (*Vespa velutina*) in real time in front of a beehive from a video feed,
and decide, under a legal floor, whether a non-lethal deterrent may act. Today the system detects
and reports; no deterrent is wired yet (see [Open decisions](#open-decisions)).

## Layers

Clean Architecture; dependencies point inwards only.

```text
interface/       CLI, composition root
infrastructure/  OpenCV video source, VespAI YOLOv5 detector, logging notifier
application/     DetectHornetVisual use case, decide(), ports
domain/          Species, Detection, BoundingBox, Point2D, VideoFrame (stdlib only)
```

- **`domain/`** — pure types. `Detection.is_threat()` is true for `VESPA_VELUTINA` only; this
  species rule stays central and auditable.
- **`application/`** — `DetectHornetVisual` reads frames, runs the detector and applies
  `decide()`: `ACT` (target at or above the threshold), `ABSTAIN` (target below it) or `IGNORE`
  (any other species). Ports are `Protocol`s:

  | Port | Methods | Adapter |
  | --- | --- | --- |
  | `VideoSource` | `frames()`, `close()` | `OpenCVVideoSource` |
  | `HornetDetector` | `detect(frame)` | `VespAIDetector` (YOLOv5, weights loaded from a path) |
  | `Notifier` | `notify_detection()`, `notify_abstention()` | `LoggingNotifier` |

- **`infrastructure/`** — the only layer that imports heavy libraries (`torch`, `cv2`, YOLOv5),
  installed through the `vision` extra.
- **`interface/cli/`** — `aristech` entry point and composition root: builds the adapters and
  injects them. Flags include `--weights`, `--yolov5-dir`, `--confidence` (operating threshold)
  and `--detector-floor` (the lower detector cut that keeps abstentions visible, ADR-0009).

Outside the runtime path:

- **`evaluation/`** — offline metrics (IoU matching, precision/recall per class), operating-point
  selection (lowest threshold with zero bees taken as targets, ADR-0004) and a YOLO-label dataset
  runner; heavy imports are lazy.
- **`datasets/`** — stdlib train/validation/test file splitter used by `scripts/distribute_*.py`.

Speculative ports (audio, distance, actuator, clock) were removed by ADR-0010; each comes back
with the use case that consumes it.

## Runtime flow

```text
VideoSource ──frame──▶ HornetDetector ──detections──▶ decide() ──ACT──────▶ Notifier.notify_detection
                                                              ├─ABSTAIN──▶ Notifier.notify_abstention
                                                              └─IGNORE
```

Sequence and component diagrams: [docs/architecture/diagrams/detection/](architecture/diagrams/detection/).

## Tests

| Level | Scope | pytest marker |
| --- | --- | --- |
| `tests/unit/` | Domain, use cases with hand-written fakes at the ports, evaluation | none (default run) |
| `tests/integration/` | Real adapters, needs `.env`, weights or data | `integration` |
| `tests/e2e/` | End to end, may need hardware | `e2e` |

`make test-unit` runs the fast suite; `pytest -m integration` or `-m e2e` the heavier levels.

## Legal floor

Harming or capturing a protected pollinator is a criminal offence in France (Code de
l'environnement L411-1, L415-3), so "never act on a bee" is an architecture constraint, not a
preference:

- abstain by default: an uncertain target never acts (ADR-0003);
- the operating threshold is the lowest one with zero bees taken as targets (ADR-0004);
- the detector floor is separate from that threshold so abstentions stay observable (ADR-0009);
- a future deterrent adds a geometric exclusion zone around the landing board, independent of the
  classifier, and uses pure water only (no biocide).

Legal analysis: [docs/research/state-of-the-art.md](research/state-of-the-art.md) § Legal framework.

## Open decisions

The deterrent is a non-lethal water jet, decoupled from detection and gated by a D0 experiment
(ADR-0005). Still open:

1. **Multimodal fusion** — whether acting needs vision and audio to agree; no published
   multimodal baseline exists for *V. velutina*.
2. **Fail-safe** — dry-run by default, acting only behind an explicit configuration flag; settled
   with the first prototype.
3. **Deterrent medium** — pure water (default) vs an air pulse, chosen by the D0 multi-arm
   comparison; solid projectiles are blocked by the legal floor, the no-trace rule and the
   non-lethal envelope. Protocol: [docs/research/prototype-foundations.md](research/prototype-foundations.md) § A.
