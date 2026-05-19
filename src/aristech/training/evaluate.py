def evaluate_model(model, test_generator, steps=50):
    test_loss, test_acc = model.evaluate(test_generator, steps=steps)
    return test_loss, test_acc
