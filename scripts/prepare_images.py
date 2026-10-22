import os

import cv2
from dotenv import load_dotenv


def prepare_images(directory, target_size=(150, 150)):
    for subdir, _, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(subdir, file)
            try:
                img = cv2.imread(filepath)
                if img is None:
                    print(f"Failed to read {filepath}")
                    continue
                resized_img = cv2.resize(img, target_size)
                cv2.imwrite(filepath, resized_img)
                print(f"Processed {filepath}")
            except Exception as e:
                print(f"Error processing {filepath}: {e}")


if __name__ == "__main__":
    load_dotenv()
    train_dir = os.getenv("TRAIN_FOLDER")
    validation_dir = os.getenv("VALIDATION_FOLDER")
    test_dir = os.getenv("TEST_FOLDER")

    prepare_images(train_dir)
    prepare_images(validation_dir)
    prepare_images(test_dir)
