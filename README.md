# Aristech

Aristech est un outil de défense des apiculteurs contre le frelon asiatique. Il utilise une combinaison de technologies pour détecter, suivre et neutraliser les frelons asiatiques.

## Table des matières

- [Introduction](#introduction)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Contribution](#contribution)
- [Licence](#licence)
- [Aide et Support](#aide-et-support)

## Introduction

Le projet Aristech utilise des techniques avancées de vision par ordinateur et de traitement du son pour identifier et neutraliser les frelons asiatiques. Il est conçu pour être utilisé par les apiculteurs afin de protéger leurs ruchers.

## Installation

### Prérequis

- Python 3.8 ou supérieur
- pip

### Étapes d'Installation

1. **Clonez le dépôt GitHub** :

    ```bash
    git clone https://github.com/votre-utilisateur/aristech.git
    cd aristech
    ```

2. **Créer et Activer l'Environnement Virtuel** :

    - **Sous Windows** :

        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

    - **Sous macOS et Linux** :

        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3. **Installer les Prérequis pour `pyaudio`** :

    - **Sous Ubuntu** :

        ```bash
        sudo apt-get update
        sudo apt-get install -y portaudio19-dev python3-pyaudio
        ```

4. **Utiliser le Script `update_requirements.py` pour Gérer les Dépendances** :

    - Créez le fichier `update_requirements.py` avec le contenu suivant :

    ```python
    import os
    import subprocess
    import sys

    def run_command(command):
        """Exécute une commande shell et affiche la sortie."""
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print(f"Erreur lors de l'exécution de la commande : {command}")
            print(f"Sortie standard : {stdout.decode('utf-8')}")
            print(f"Erreur standard : {stderr.decode('utf-8')}")
            raise subprocess.CalledProcessError(process.returncode, command)
        else:
            print(stdout.decode('utf-8'))

    def check_and_install(package):
        """Vérifie si un package est installé, sinon l'installe."""
        try:
            __import__(package)
        except ImportError:
            print(f"Installation de {package}...")
            run_command(f"{sys.executable} -m pip install {package}")

    def generate_requirements_with_pipreqs():
        """Génère requirements.txt avec pipreqs."""
        print("Génération de requirements.txt avec pipreqs...")
        run_command("pipreqs . --force")

    def convert_requirements_txt_to_in():
        """Convertit requirements.txt en requirements.in."""
        print("Conversion de requirements.txt en requirements.in...")
        if os.path.exists("requirements.txt"):
            os.rename("requirements.txt", "requirements.in")
        else:
            print("Le fichier requirements.txt n'existe pas.")

    def compile_requirements():
        """Génère requirements.txt à partir de requirements.in."""
        print("Génération de requirements.txt à partir de requirements.in...")
        run_command("pip-compile --strip-extras requirements.in")

    def sync_requirements():
        """Synchronise les dépendances avec requirements.txt."""
        print("Synchronisation des dépendances avec requirements.txt...")
        run_command("pip-sync requirements.txt")

    def main():
        check_and_install("pipreqs")
        check_and_install("piptools")
        generate_requirements_with_pipreqs()
        convert_requirements_txt_to_in()
        compile_requirements()
        sync_requirements()
        print("Toutes les étapes sont terminées avec succès !")

    if __name__ == "__main__":
        main()
    ```

    - Exécutez le script `update_requirements.py` :

    ```bash
    python3 update_requirements.py
    ```

### Désactivation de l'Environnement Virtuel

Pour désactiver l'environnement virtuel, utilisez la commande suivante :

```bash
deactivate
```

## Configuration

### Variables d'Environnement

1. Copiez le fichier `.env.example` en `.env` :

    ```bash
    cp .env.example .env
    ```

2. Ouvrez le fichier `.env` et modifiez les valeurs selon vos besoins. Par exemple :

    ```plaintext
    # =============================
    # Example Fichier de Configuration Environnementale
    # =============================

    # --- Configuration des Dossiers ---
    # Dossier source contenant les images de frelons asiatiques
    SOURCE_FOLDER=path/to/source_folder

    # Dossiers pour la répartition des images
    TRAIN_FOLDER=data/images/train
    VALIDATION_FOLDER=data/images/validation
    TEST_FOLDER=data/images/test

    # --- Configuration des Modèles ---
    # Chemin vers le modèle de détection sonore des frelons asiatiques
    SOUND_MODEL_PATH=models/hornet_sound_model.h5

    # Chemin vers le modèle de détection visuelle des frelons asiatiques
    IMAGE_MODEL_PATH=models/hornet_image_model.pth

    # --- Configuration de l'Application ---
    # Nom de l'application
    APP_NAME=Aristech

    # Version de l'application
    APP_VERSION=0.1.0

    # Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    LOG_LEVEL=INFO

    # --- Configuration de la Source Vidéo ---
    # Source vidéo (indice de la caméra, chemin vers un fichier vidéo ou URL du flux vidéo)
    VIDEO_SOURCE=0

    # --- Configuration des Modules ---
    # Activation des modules spécifiques
    ENABLE_SOLAR_MODULE=true
    ENABLE_SONAR_MODULE=true
    ENABLE_TARGET_MODULE=true
    ENABLE_CONNECT_MODULE=true

    # Paramètres spécifiques aux modules
    SOLAR_MAX_POWER_POINT_TRACKING=true
    SONAR_RANGE=500  # Portée maximale du sonar en cm
    TARGET_TRACKING_SPEED=0.1  # Vitesse de suivi des cibles
    CONNECT_PROTOCOL=LoRaWAN  # Protocole de communication : LoRaWAN, WiFi, Bluetooth
    CONNECT_UPDATE_INTERVAL=60  # Intervalle de mise à jour en secondes

    # --- Configuration du Contrôle du Lance-Projectiles ---
    # Broches GPIO pour les composants du lance-projectiles
    LASER_PIN=18  # Broche GPIO pour le laser de pointage
    COIL_GUN_PIN=23  # Broche GPIO pour le contrôle du lance-projectiles
    SERVO_PIN=24  # Broche GPIO pour le servo-moteur
    SERVO_FREQUENCY=50  # Fréquence du servo-moteur en Hz
    ```

### Exécution du Projet

Pour démarrer l'application, exécutez :

```bash
python src/main.py
```

## Utilisation

Pour entraîner les modèles, exécutez les scripts dans `src/training/`. Par exemple, pour entraîner le modèle de reconnaissance sonore :

```bash
python src/training/train_sound_model.py
```

## Contribution

Nous accueillons les contributions avec plaisir. Veuillez suivre les étapes ci-dessous pour contribuer :

1. **Fork** le dépôt
2. **Clonez** votre fork :

    ```bash
    git clone https://github.com/votre-utilisateur/aristech.git
    cd aristech
    ```

3. **Créez** une branche pour votre fonctionnalité :

    ```bash
    git checkout -b nouvelle-fonctionnalite
    ```

4. **Développez** et **committez** vos changements :

    ```bash
    git add .
    git commit -m "Ajout de la nouvelle fonctionnalité"
    ```

5. **Poussez** votre branche vers GitHub :

    ```bash
    git push origin nouvelle-fonctionnalite
    ```

6. **Créez** une pull request sur le dépôt original pour examiner vos modifications.

Veuillez lire `CONTRIBUTING.md` pour plus de détails sur notre code de conduite et le processus de soumission de pull requests.

## Licence

Ce projet est sous licence MIT - voir le fichier `LICENSE.md` pour plus de détails.

## Aide et Support

Pour toute question ou assistance, veuillez consulter notre [FAQ](docs/faq.md) ou ouvrir une issue sur GitHub.

---

Merci d'utiliser Aristech !
