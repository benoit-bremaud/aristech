def compile_model(model):
    model.compile(
        loss="binary_crossentropy",
        optimizer="adam",
        metrics=["accuracy"],
    )
    return model


def train_model(
    model,
    train_generator,
    validation_generator,
    epochs=30,
    steps_per_epoch=100,
    validation_steps=50,
):
    return model.fit(
        train_generator,
        steps_per_epoch=steps_per_epoch,
        epochs=epochs,
        validation_data=validation_generator,
        validation_steps=validation_steps,
    )
