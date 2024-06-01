import os
import shutil
import random
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

def distribute_images(source_folder, train_folder, validation_folder, test_folder, train_ratio=0.7, validation_ratio=0.2):
    # Création des dossiers s'ils n'existent pas
    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(validation_folder, exist_ok=True)
    os.makedirs(test_folder, exist_ok=True)

    # Obtenir la liste de toutes les images dans le dossier source
    all_images = os.listdir(source_folder)

    # Mélanger les images pour une répartition aléatoire
    random.shuffle(all_images)

    # Calculer les nombres d'images pour chaque set
    total_images = len(all_images)
    train_count = int(train_ratio * total_images)
    validation_count = int(validation_ratio * total_images)
    test_count = total_images - train_count - validation_count

    # Répartir les images dans les dossiers correspondants
    for i, image in enumerate(all_images):
        if i < train_count:
            shutil.move(os.path.join(source_folder, image), os.path.join(train_folder, image))
        elif i < train_count + validation_count:
            shutil.move(os.path.join(source_folder, image), os.path.join(validation_folder, image))
        else:
            shutil.move(os.path.join(source_folder, image), os.path.join(test_folder, image))

    print(f"Images réparties dans les dossiers : {train_count} pour l'entraînement, {validation_count} pour la validation, {test_count} pour le test.")

if __name__ == "__main__":
    source_folder = os.getenv('SOURCE_FOLDER')
    train_folder = os.getenv('TRAIN_FOLDER')
    validation_folder = os.getenv('VALIDATION_FOLDER')
    test_folder = os.getenv('TEST_FOLDER')
    
    distribute_images(source_folder, train_folder, validation_folder, test_folder)
