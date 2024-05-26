# Instructions d'Installation pour Aristech

## Prérequis

- Python 3.8 ou supérieur
- pip

## Étapes d'Installation

1. **Clonez le dépôt GitHub :**
    ```bash
    git clone https://github.com/votre-utilisateur/aristech.git
    cd aristech
    ```

2. **Installez les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

3. **Configuration des fichiers :**
    - Ouvrez et modifiez les fichiers de configuration suivants pour adapter le système à votre environnement :
        - `config/config.yaml`
        - `config/logging.yaml`

## Configuration

1. **Modification des fichiers de configuration :**
    - `config/config.yaml` : Contient les paramètres nécessaires pour l'application.
    - `config/logging.yaml` : Configure la journalisation pour l'application.

Assurez-vous que tous les chemins et paramètres sont correctement définis pour votre environnement.

### Exemple de `config/config.yaml`

```yaml
video_source: 0
sound_detection:
  threshold: 0.01
hornet_detection:
  model: yolov5s
distance_measurement:
  stereo_params: stereo_params.yaml
  tof_params: tof_params.yaml
coil_gun_control:
  laser_pin: 18
  coil_gun_pin: 23
  servo_pin: 24
  servo_frequency: 50
