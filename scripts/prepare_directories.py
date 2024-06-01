import os
import shutil

def create_directories(base_dir, class_name):
    os.makedirs(os.path.join(base_dir, class_name), exist_ok=True)

def move_images_to_class_directory(base_dir, class_name):
    class_dir = os.path.join(base_dir, class_name)
    for file in os.listdir(base_dir):
        file_path = os.path.join(base_dir, file)
        if os.path.isfile(file_path) and (file.endswith(".jpeg") or file.endswith(".jpg") or file.endswith(".png")):
            shutil.move(file_path, os.path.join(class_dir, file))

if __name__ == "__main__":
    base_dir = "data/images"
    class_name = "vespa-velutina"
    
    for split in ["train", "validation", "test"]:
        split_dir = os.path.join(base_dir, split)
        create_directories(split_dir, class_name)
        move_images_to_class_directory(split_dir, class_name)
    
    print("Images have been moved to the appropriate directories.")
