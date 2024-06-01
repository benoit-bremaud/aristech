import os
import shutil
import random
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

def distribute_videos(source_folder, train_folder, validation_folder, test_folder, train_ratio=0.7, validation_ratio=0.2):
    """
    Répartit les vidéos du dossier source entre les dossiers d'entraînement, de validation et de test.
    
    :param source_folder: Chemin vers le dossier source contenant les vidéos.
    :param train_folder: Chemin vers le dossier de destination des vidéos d'entraînement.
    :param validation_folder: Chemin vers le dossier de destination des vidéos de validation.
    :param test_folder: Chemin vers le dossier de destination des vidéos de test.
    :param train_ratio: Ratio des vidéos destinées à l'entraînement.
    :param validation_ratio: Ratio des vidéos destinées à la validation.
    :param test_ratio: Ratio des vidéos destinées aux tests.
    """
    # Créer les dossiers s'ils n'existent pas
    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(validation_folder, exist_ok=True)
    os.makedirs(test_folder, exist_ok=True)

    # Obtenir la liste de toutes les vidéos dans le dossier source
    all_videos = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
    
    # Vérifier qu'il y a des vidéos dans le dossier source
    if not all_videos:
        print("Aucune vidéo trouvée dans le dossier source.")
        return

    # Mélanger les vidéos pour une répartition aléatoire
    random.shuffle(all_videos)

    # Calculer les nombres de vidéos pour chaque set
    total_videos = len(all_videos)
    train_count = int(train_ratio * total_videos)
    validation_count = int(validation_ratio * total_videos)
    test_count = total_videos - train_count - validation_count

    # Répartir les vidéos dans les dossiers correspondants
    for i, video in enumerate(all_videos):
        src_path = os.path.join(source_folder, video)
        if i < train_count:
            dest_path = os.path.join(train_folder, video)
        elif i < train_count + validation_count:
            dest_path = os.path.join(validation_folder, video)
        else:
            dest_path = os.path.join(test_folder, video)
        
        shutil.move(src_path, dest_path)

    print(f"Vidéos réparties dans les dossiers : {train_count} pour l'entraînement, {validation_count} pour la validation, {test_count} pour le test.")

if __name__ == "__main__":
    # Charger les variables d'environnement
    source_folder = os.getenv('VIDEO_SOURCE_FOLDER')
    train_folder = os.getenv('VIDEO_TRAIN_FOLDER')
    validation_folder = os.getenv('VIDEO_VALIDATION_FOLDER')
    test_folder = os.getenv('VIDEO_TEST_FOLDER')
    
    # Vérifier que toutes les variables d'environnement sont définies
    if not all([source_folder, train_folder, validation_folder, test_folder]):
        print("Une ou plusieurs variables d'environnement pour les vidéos ne sont pas définies.")
        exit(1)
    
    # Répartir les vidéos
    distribute_videos(source_folder, train_folder, validation_folder, test_folder)
