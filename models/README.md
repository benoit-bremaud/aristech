# models/

Local model weights live here. **None is versioned.**

## Convention

| Expected file | Source | Git status |
| --- | --- | --- |
| VespAI weights (`*.pt`) | supplied by the operator (CC BY-NC-SA), passed with `--weights` | ignored |

Ignored patterns: `models/*.keras`, `models/*.h5`, `models/*.pth`, `models/*.pt` — see
[`.gitignore`](../.gitignore).

The legacy Keras training pipeline was removed (ADR-0010); a YOLO fine-tune on own data is planned
for M5.

## Fetching a pre-trained model (planned)

Once a distribution channel is chosen (GitHub Releases, Hugging Face Hub, S3…), a
`scripts/download_model.py` will fetch the weights.
