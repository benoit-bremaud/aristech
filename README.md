
# Aristech

Aristech est un outil de défense des apiculteurs contre le frelon asiatique. Il utilise une combinaison de technologies pour détecter, suivre et neutraliser les frelons asiatiques.

## Table des matières

- [Installation](#installation)
- [Utilisation](#utilisation)
- [Modules](#modules)
- [Contribution](#contribution)
- [Licence](#licence)
- [Aide et Support](#aide-et-support)

## Installation

### Prérequis

- Python 3.8 ou supérieur
- pip

### Étapes

1. Clonez le dépôt GitHub :
    ```bash
    git clone https://github.com/votre-utilisateur/aristech.git
    cd aristech
    ```

2. Créez un environnement virtuel :
    ```bash
    python3 -m venv venv
    ```

3. Activez l'environnement virtuel :
    - **Sous Windows** :
        ```bash
        .\venv\Scripts\activate
        ```
    - **Sous macOS et Linux** :
        ```bash
        source venv/bin/activate
        ```

4. Installez les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

5. Modifiez les fichiers de configuration pour adapter le système à votre environnement :
    - `config/config.yaml`
    - `config/logging.yaml`

### Désactivation de l'Environnement Virtuel

Pour désactiver l'environnement virtuel, utilisez la commande suivante :
```bash
deactivate
```

## Utilisation

Pour démarrer l'application, exécutez :
```bash
python src/main.py
```

Pour entraîner les modèles, exécutez les scripts dans `src/training/`. Par exemple, pour entraîner le modèle de reconnaissance sonore :
```bash
python src/training/train_sound_model.py
```

## Modules

### Module Solar

Le module `solar.py` permet d'orienter le panneau solaire vers le point le plus ensoleillé. Il utilise des capteurs de luminosité pour déterminer la meilleure orientation.

### Module Sonar

Le module `sonar.py` s'occupe de la détection sonore des frelons asiatiques. Il utilise des modèles de machine learning pour identifier le bourdonnement caractéristique des frelons.

### Module Target

Le module `target.py` gère la détection visuelle des frelons asiatiques à l'aide de modèles de détection d'objets.

### Module Connect

Le module `connect.py` est destiné à permettre la communication entre différents produits Aristech via des protocoles IoT, l'échange de données et la réception de mises à jour.

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
