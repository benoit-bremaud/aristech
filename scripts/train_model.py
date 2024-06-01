from src.model_training.data_preparation import prepare_data
from src.model_training.model_architecture import create_model
from src.model_training.train import compile_model, train_model
from src.model_training.evaluate import evaluate_model
from src.model_training.save_model import save_model

def main():
    train_generator, validation_generator, test_generator = prepare_data()
    
    model = create_model()
    model = compile_model(model)
    
    history = train_model(model, train_generator, validation_generator)
    
    test_loss, test_acc = evaluate_model(model, test_generator)
    print(f"Test Accuracy: {test_acc}")
    
    save_model(model)

if __name__ == "__main__":
    main()
