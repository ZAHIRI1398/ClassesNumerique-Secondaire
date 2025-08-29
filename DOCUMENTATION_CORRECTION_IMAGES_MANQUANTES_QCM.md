# Documentation : Correction des images manquantes dans les exercices QCM

## Problématique

Certaines images des exercices QCM n'étaient pas correctement affichées pour les raisons suivantes :

1. Les chemins d'images n'étaient pas cohérents dans la base de données (différents formats de chemins)
2. Les images physiques étaient stockées dans différents répertoires
3. Le gestionnaire de fallback ne recherchait pas dans tous les répertoires potentiels
4. Certaines images référencées n'existaient pas physiquement sur le serveur

## Solutions implémentées

### 1. Amélioration du gestionnaire de fallback d'images

Le gestionnaire de fallback a été amélioré pour rechercher les images dans plusieurs répertoires alternatifs :

- `/static/uploads/exercises/qcm/` (chemin principal pour les images QCM)
- `/static/uploads/exercises/` (chemin sans le type d'exercice)
- `/static/uploads/` (chemin racine des uploads)
- `/static/exercises/` (ancien chemin utilisé)
- `/static/exercise-images/` et `/static/exercise_images/` (autres chemins alternatifs)

Cette amélioration permet de trouver les images même si elles sont stockées dans un répertoire différent de celui référencé dans la base de données.

### 2. Script de correction des chemins d'images

Un script (`fix_missing_qcm_images.py`) a été créé pour :

- Identifier tous les exercices QCM avec des images
- Rechercher les images physiques dans différents répertoires
- Copier les images trouvées vers le répertoire standard `/static/uploads/exercises/qcm/`
- Mettre à jour les chemins d'images dans la base de données pour pointer vers le nouvel emplacement

Ce script permet de normaliser les chemins d'images et de s'assurer que toutes les images sont physiquement présentes dans le répertoire standard.

### 3. Création d'images placeholder pour les images manquantes

Pour les images qui ne peuvent pas être trouvées physiquement sur le serveur, un script (`create_placeholder_for_exercise_58.py`) a été créé pour :

- Générer une image placeholder avec un contenu visuel pertinent
- Sauvegarder cette image dans le répertoire standard
- Mettre à jour le chemin d'image dans la base de données

Cette solution garantit qu'aucun exercice ne sera affiché avec une image manquante, même si l'image originale n'existe plus.

## Implémentation technique

### Script de correction des chemins d'images

```python
import os
import shutil
import json
import sqlite3
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Répertoires d'images sources et cible
SOURCE_DIRS = [
    'static/uploads',
    'static/exercises',
    'static/exercise-images',
    'static/exercise_images',
]
TARGET_DIR = 'static/uploads/exercises/qcm'

# Fonction principale qui parcourt tous les exercices QCM
def fix_qcm_images():
    # Récupérer tous les exercices QCM
    # Pour chaque exercice avec une image :
    #   - Rechercher l'image dans les répertoires sources
    #   - Copier l'image vers le répertoire cible
    #   - Mettre à jour le chemin d'image dans la base de données
```

### Script de création d'images placeholder

```python
from PIL import Image, ImageDraw, ImageFont
import json
import sqlite3
import os
import logging

# Création d'une image placeholder thématique
def create_placeholder_image(filename, title="Système solaire"):
    # Créer une image avec un fond bleu foncé
    # Dessiner des éléments visuels (soleil, planètes)
    # Ajouter du texte explicatif
    # Sauvegarder l'image dans le répertoire cible
```

## Résultats

Les scripts ont été exécutés avec succès :

1. Une image a été trouvée et copiée pour l'exercice 87
2. Une image placeholder a été créée pour l'exercice 58 dont l'image originale était introuvable

## Recommandations pour l'avenir

1. **Standardisation des chemins d'images** : Utiliser systématiquement le format `/static/uploads/exercises/{type_exercice}/` pour toutes les nouvelles images.

2. **Vérification périodique** : Exécuter régulièrement un script de vérification pour s'assurer que toutes les images référencées existent physiquement.

3. **Backup des images** : Mettre en place un système de sauvegarde des images pour éviter la perte d'images.

4. **Migration vers Cloudinary** : Envisager la migration complète vers Cloudinary pour une gestion plus robuste des images.

5. **Amélioration du gestionnaire de fallback** : Continuer à améliorer le gestionnaire de fallback pour qu'il puisse générer automatiquement des images placeholder pour les images manquantes.

## Conclusion

Les modifications apportées permettent désormais :

1. D'afficher correctement les images existantes dans les exercices QCM
2. De fournir des images placeholder pour les images manquantes
3. De normaliser progressivement les chemins d'images pour une meilleure maintenance

Ces améliorations contribuent à une expérience utilisateur plus cohérente et à une maintenance plus facile du code.
