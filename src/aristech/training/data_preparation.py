import os

from dotenv import load_dotenv
from tensorflow.keras.preprocessing.image import ImageDataGenerator


def prepare_data():
    load_dotenv()

    train_dir = os.getenv("TRAIN_FOLDER")
    validation_dir = os.getenv("VALIDATION_FOLDER")
    test_dir = os.getenv("TEST_FOLDER")

    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode="nearest",
    )

    validation_datagen = ImageDataGenerator(rescale=1.0 / 255)
    test_datagen = ImageDataGenerator(rescale=1.0 / 255)

    train_generator = train_datagen.flow_from_directory(
        train_dir, target_size=(150, 150), batch_size=32, class_mode="binary"
    )

    validation_generator = validation_datagen.flow_from_directory(
        validation_dir, target_size=(150, 150), batch_size=32, class_mode="binary"
    )

    test_generator = test_datagen.flow_from_directory(
        test_dir, target_size=(150, 150), batch_size=32, class_mode="binary"
    )

    print(f"Found {train_generator.samples} images in training directory.")
    print(f"Found {validation_generator.samples} images in validation directory.")
    print(f"Found {test_generator.samples} images in test directory.")

    return train_generator, validation_generator, test_generator
