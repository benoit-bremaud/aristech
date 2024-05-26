```markdown
# Architecture du Projet Aristech

## Introduction

Le projet Aristech vise à développer un système de détection et de neutralisation des frelons asiatiques en temps réel. Ce document décrit l'architecture globale du projet, les composants principaux, leurs interactions et inclut des diagrammes pour illustrer ces concepts.

## Composants Principaux

### 1. Détection Sonore (`sound_detection.py`)
Ce module est responsable de la reconnaissance des signatures sonores des frelons asiatiques. Il utilise des techniques de traitement du signal pour analyser les sons captés par les microphones.

### 2. Détection Visuelle (`hornet_detection.py`)
Ce module est responsable de la reconnaissance visuelle des frelons asiatiques en utilisant des techniques de traitement d'image et de vision par ordinateur.

### 3. Mesure de Distance (`distance_measurement.py`)
Ce module utilise la vision stéréo et la technologie Time-of-Flight (ToF) pour mesurer la distance des frelons par rapport à la caméra.

### 4. Contrôle du Lance-Projectile (`coil_gun_control.py`)
Ce module contrôle le lance-projectile de type coil-gun pour neutraliser les frelons identifiés.

### 5. Traitement d'Image (`image_processing.py`)
Ce module effectue le prétraitement et l'analyse des images capturées par la caméra.

### 6. Capture Vidéo (`video_capture.py`)
Ce module est responsable de la capture des flux vidéo en temps réel à partir des caméras.

### 7. Modules de Formation (`training`)
Les modules de formation sont utilisés pour entraîner les modèles de détection sonore, visuelle et de mesure de distance.

### 8. Utilitaires (`utils.py`)
Ce module contient des fonctions utilitaires utilisées par d'autres modules du projet.

### 9. Modules Additionnels (`modules`)
Les modules additionnels incluent `connect.py`, `solar.py`, `sonar.py` et `target.py`.

## Interactions Entre les Modules

1. **Détection et Capture** : Les modules de détection sonore et visuelle (sound_detection.py et hornet_detection.py) travaillent en parallèle pour détecter la présence de frelons. Le module de capture vidéo (video_capture.py) fournit les flux d'entrée nécessaires.

2. **Analyse et Mesure** : Une fois les frelons détectés, les modules de traitement d'image (image_processing.py) et de mesure de distance (distance_measurement.py) analysent les images et calculent la distance des frelons par rapport à la caméra.

3. **Neutralisation** : Le module de contrôle du lance-projectile (coil_gun_control.py) utilise les données des modules de détection et de mesure pour cibler et neutraliser les frelons.

## Diagrammes d'Architecture

### Diagramme de Flux de Données

```plaintext
+------------------+       +---------------------+       +----------------------+
| Capture Vidéo    | ----> | Traitement d'Image  | ----> | Détection Visuelle   |
| (video_capture)  |       | (image_processing)  |       | (hornet_detection)   |
+------------------+       +---------------------+       +----------------------+
                                |
                                v
+------------------+       +---------------------+       +----------------------+
| Détection Sonore |       | Mesure de Distance  |       | Contrôle Lance-      |
| (sound_detection)| ----> | (distance_measurement) | --> | Projectile          |
+------------------+       +---------------------+       | (coil_gun_control)   |
                                                         +----------------------+
```

### Diagramme de Composants

```plaintext
+-----------------+
|   Aristech      |
|    System       |
+-----------------+
        |
        v
+------------------+
| Capture Vidéo    |
| (video_capture)  |
+------------------+
        |
        v
+------------------+        +------------------+
| Traitement d'Image |     | Détection Sonore  |
| (image_processing) |     | (sound_detection) |
+------------------+        +------------------+
        |
        v
+------------------+
| Détection Visuelle|
| (hornet_detection)|
+------------------+
        |
        v
+------------------+        +------------------+
| Mesure de Distance |     | Contrôle Lance-  |
| (distance_measurement) | | Projectile      |
+------------------+        | (coil_gun_control) |
                             +------------------+
```

## Conclusion

Ce document fournit une vue d'ensemble de l'architecture du projet Aristech, décrivant les principaux modules et leurs interactions. Les diagrammes inclus aident à visualiser les flux de données et les relations entre les composants. Cette architecture modulaire permet une flexibilité et une extensibilité maximales pour le développement futur.
```