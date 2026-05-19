"""Entraîne le modèle de détection visuelle et sauvegarde dans models/.

Prérequis : `pip install -e ".[dev]"` (le package `aristech` doit être
importable). Variables d'environnement requises (cf. `.env.example`) :
TRAIN_FOLDER, VALIDATION_FOLDER, TEST_FOLDER.
"""

from pathlib import Path

from aristech.training.data_preparation import prepare_data
from aristech.training.evaluate import evaluate_model
from aristech.training.model_architecture import create_model
from aristech.training.save_model import save_model
from aristech.training.train import compile_model, train_model


def main() -> None:
    train_generator, validation_generator, test_generator = prepare_data()

    model = create_model()
    model = compile_model(model)

    train_model(model, train_generator, validation_generator)

    _, test_acc = evaluate_model(model, test_generator)
    print(f"Test Accuracy: {test_acc}")

    output = Path("models/hornet_image_model.keras")
    output.parent.mkdir(parents=True, exist_ok=True)
    save_model(model, filepath=str(output))


if __name__ == "__main__":
    main()
