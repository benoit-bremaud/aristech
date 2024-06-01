import sys
import os

# Ajouter le répertoire racine du projet au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.model_training.data_preparation import prepare_data
from src.model_training.model_architecture import create_model
from src.model_training.train import compile_model, train_model
from src.model_training.evaluate import evaluate_model
from src.model_training.save_model import save_model

def main():
    # Préparer les données
    train_generator, validation_generator, test_generator = prepare_data()
    
    # Créer et compiler le modèle
    model = create_model()
    model = compile_model(model)
    
    # Entraîner le modèle
    history = train_model(model, train_generator, validation_generator)
    
    # Évaluer le modèle
    test_loss, test_acc = evaluate_model(model, test_generator)
    print(f"Test Accuracy: {test_acc}")
    
    # Sauvegarder le modèle
    save_model(model)

if __name__ == "__main__":
    main()