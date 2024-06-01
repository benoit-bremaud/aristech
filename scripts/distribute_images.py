import os
import shutil
import random
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

def distribute_images(source_folder, train_folder, validation_folder, test_folder, train_ratio=0.7, validation_ratio=0.2):
    """
    Répartit les images du dossier source entre les dossiers d'entraînement, de validation et de test.
    
    :param source_folder: Chemin vers le dossier source contenant les images.
    :param train_folder: Chemin vers le dossier de destination des images d'entraînement.
    :param validation_folder: Chemin vers le dossier de destination des images de validation.
    :param test_folder: Chemin vers le dossier de destination des images de test.
    :param train_ratio: Ratio des images destinées à l'entraînement.
    :param validation_ratio: Ratio des images destinées à la validation.
    :param test_ratio: Ratio des images destinées aux tests.
    """
    # Créer les dossiers s'ils n'existent pas
    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(validation_folder, exist_ok=True)
    os.makedirs(test_folder, exist_ok=True)

    # Obtenir la liste de toutes les images dans le dossier source
    all_images = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
    
    # Vérifier qu'il y a des images dans le dossier source
    if not all_images:
        print("Aucune image trouvée dans le dossier source.")
        return

    # Mélanger les images pour une répartition aléatoire
    random.shuffle(all_images)

    # Calculer les nombres d'images pour chaque set
    total_images = len(all_images)
    train_count = int(train_ratio * total_images)
    validation_count = int(validation_ratio * total_images)
    test_count = total_images - train_count - validation_count

    # Répartir les images dans les dossiers correspondants
    for i, image in enumerate(all_images):
        src_path = os.path.join(source_folder, image)
        if i < train_count:
            dest_path = os.path.join(train_folder, image)
        elif i < train_count + validation_count:
            dest_path = os.path.join(validation_folder, image)
        else:
            dest_path = os.path.join(test_folder, image)
        
        shutil.move(src_path, dest_path)

    print(f"Images réparties dans les dossiers : {train_count} pour l'entraînement, {validation_count} pour la validation, {test_count} pour le test.")

if __name__ == "__main__":
    # Charger les variables d'environnement
    source_folder = os.getenv('SOURCE_FOLDER')
    train_folder = os.getenv('TRAIN_FOLDER')
    validation_folder = os.getenv('VALIDATION_FOLDER')
    test_folder = os.getenv('TEST_FOLDER')
    
    # Vérifier que toutes les variables d'environnement sont définies
    if not all([source_folder, train_folder, validation_folder, test_folder]):
        print("Une ou plusieurs variables d'environnement ne sont pas définies.")
        exit(1)
    
    # Répartir les images
    distribute_images(source_folder, train_folder, validation_folder, test_folder)
