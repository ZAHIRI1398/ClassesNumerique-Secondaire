# Documentation des Scripts de Diagnostic et Correction Automatique

## Contexte et Problématique

Les scripts de diagnostic et de correction automatique des chemins d'images pour les exercices de type "paires" présentaient deux problèmes majeurs :

1. **Dépendance à un serveur Flask local** : Les scripts utilisaient des requêtes HTTP HEAD pour vérifier l'accessibilité des images, nécessitant un serveur Flask en cours d'exécution.
2. **Chemin de base de données statique** : Les scripts utilisaient un chemin fixe pour accéder à la base de données SQLite, ce qui posait problème dans différents environnements de déploiement.

## Solutions Implémentées

### 1. Détection Dynamique de la Base de Données

Une fonction `find_database_path()` a été implémentée pour détecter automatiquement l'emplacement de la base de données SQLite :

```python
def find_database_path():
    """
    Détecte dynamiquement le chemin de la base de données SQLite.
    Vérifie plusieurs emplacements possibles et retourne l'URI SQLAlchemy correspondante.
    """
    # Vérifier d'abord dans le répertoire instance
    instance_db_path = os.path.abspath('instance/app.db')
    root_db_path = os.path.abspath('app.db')
    
    if os.path.exists(instance_db_path):
        print(f"[INFO] Base de données trouvée à {instance_db_path}")
        return f'sqlite:///{instance_db_path}'
    elif os.path.exists(root_db_path):
        print(f"[INFO] Base de données trouvée à {root_db_path}")
        return f'sqlite:///{root_db_path}'
    else:
        # Recherche récursive
        for db_file in pathlib.Path('.').glob('**/app.db'):
            db_path = os.path.abspath(db_file)
            print(f"[INFO] Base de données trouvée à {db_path}")
            return f'sqlite:///{db_path}'
    
    print("[ERREUR] Aucune base de données trouvée")
    return None
```

Cette fonction :
- Vérifie d'abord dans le répertoire `instance/app.db` (emplacement standard Flask)
- Vérifie ensuite à la racine du projet (`app.db`)
- Effectue une recherche récursive si nécessaire
- Retourne l'URI SQLAlchemy complète pour la connexion à la base de données

### 2. Vérification Locale des Fichiers d'Images

Au lieu d'utiliser des requêtes HTTP HEAD pour vérifier l'accessibilité des images, les scripts utilisent maintenant des vérifications directes du système de fichiers :

```python
def check_image_exists(image_path):
    """
    Vérifie si une image existe physiquement sur le système de fichiers.
    Prend en charge les chemins relatifs et absolus.
    """
    # Supprimer le préfixe '/static/' pour obtenir le chemin relatif
    if image_path.startswith('/static/'):
        relative_path = image_path[8:]  # Enlever '/static/'
    else:
        relative_path = image_path
    
    # Construire le chemin absolu
    absolute_path = os.path.join(os.getcwd(), 'static', relative_path)
    
    # Vérifier si le fichier existe
    exists = os.path.isfile(absolute_path)
    
    if exists:
        print(f"[INFO] Image trouvée : {absolute_path}")
    else:
        print(f"[ERREUR] Image non trouvée : {absolute_path}")
    
    return exists
```

Cette approche :
- Élimine la dépendance à un serveur Flask en cours d'exécution
- Fonctionne dans tous les environnements (développement, production)
- Est plus rapide et plus fiable

### 3. Sauvegarde Robuste de la Base de Données

La fonction de sauvegarde de la base de données a été améliorée pour utiliser le chemin absolu et vérifier l'existence du fichier :

```python
def backup_database():
    """
    Crée une sauvegarde de la base de données avant toute modification.
    Utilise le chemin absolu détecté dynamiquement.
    """
    # Extraire le chemin de fichier de l'URI SQLAlchemy
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    
    # Vérifier si le fichier existe
    if not os.path.exists(db_path):
        print(f"[ERREUR] Le fichier de base de données n'existe pas: {db_path}")
        return None
    
    # Créer le nom du fichier de sauvegarde avec timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"app_backup_{timestamp}.db"
    backup_path = os.path.join(os.path.dirname(db_path), backup_filename)
    
    try:
        # Copier le fichier
        shutil.copy2(db_path, backup_path)
        print(f"[INFO] Sauvegarde créée : {backup_path}")
        return backup_path
    except Exception as e:
        print(f"[ERREUR] Impossible de créer une sauvegarde : {str(e)}")
        return None
```

Cette fonction :
- Extrait le chemin de fichier de l'URI SQLAlchemy
- Vérifie l'existence du fichier avant de tenter la copie
- Crée un nom de fichier de sauvegarde avec timestamp
- Gère les erreurs de façon robuste

## Script de Diagnostic (`test_pairs_image_paths_production.py`)

Le script de diagnostic a été amélioré pour fonctionner sans serveur local et avec détection dynamique de la base de données :

```python
import os
import sys
import json
import pathlib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Fonction de détection de la base de données
def find_database_path():
    # (code de la fonction)

# Configuration de l'application Flask
app = Flask(__name__)
db_uri = find_database_path()
if not db_uri:
    print("Impossible de trouver la base de données. Vérifiez qu'elle existe.")
    sys.exit(1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Définition du modèle Exercise
class Exercise(db.Model):
    # (définition du modèle)

# Fonction principale de diagnostic
def check_pairs_image_paths():
    with app.app_context():
        # Récupérer tous les exercices de type 'pairs'
        pairs_exercises = Exercise.query.filter_by(type='pairs').all()
        print(f"Nombre d'exercices de type 'pairs' trouvés : {len(pairs_exercises)}")
        
        # Parcourir les exercices et vérifier les chemins d'images
        for exercise in pairs_exercises:
            # (code de vérification des chemins d'images)
            # Utilise check_image_exists() au lieu de requêtes HTTP
```

## Script de Correction Automatique (`fix_pairs_images_auto.py`)

Le script de correction automatique a été amélioré de la même manière :

```python
import os
import sys
import json
import shutil
import pathlib
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Fonction de détection de la base de données
def find_database_path():
    # (code de la fonction)

# Configuration de l'application Flask
app = Flask(__name__)
db_uri = find_database_path()
if not db_uri:
    print("Impossible de trouver la base de données. Vérifiez qu'elle existe.")
    sys.exit(1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Fonction de sauvegarde de la base de données
def backup_database():
    # (code de la fonction améliorée)

# Fonction de normalisation des chemins d'images
def normalize_pairs_exercise_content(content_json):
    # (code de la fonction)

# Fonction principale de correction
def fix_pairs_image_paths():
    with app.app_context():
        # Créer une sauvegarde de la base de données
        backup_path = backup_database()
        if not backup_path:
            print("Impossible de créer une sauvegarde. Opération annulée.")
            return False
        
        # Récupérer tous les exercices de type 'pairs'
        pairs_exercises = Exercise.query.filter_by(type='pairs').all()
        print(f"Nombre d'exercices de type 'pairs' trouvés : {len(pairs_exercises)}")
        
        # Parcourir les exercices et corriger les chemins d'images
        # (code de correction des chemins d'images)
```

## Intégration dans l'Interface Admin

Pour faciliter l'utilisation de ces scripts, une route Flask peut être ajoutée à l'application principale :

```python
@app.route('/admin/fix-pairs-images', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_fix_pairs_images():
    if request.method == 'POST':
        # Exécuter la correction automatique
        success, message = fix_pairs_image_paths()
        if success:
            flash('Les chemins d\'images ont été corrigés avec succès.', 'success')
        else:
            flash(f'Erreur lors de la correction des chemins d\'images : {message}', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    # Afficher la page de confirmation
    return render_template('admin/fix_pairs_images.html')
```

## Utilisation des Scripts

### Script de Diagnostic

Pour exécuter le script de diagnostic :

```bash
python test_pairs_image_paths_production.py
```

Ce script :
1. Détecte automatiquement la base de données
2. Récupère tous les exercices de type 'pairs'
3. Vérifie les chemins d'images dans chaque exercice
4. Affiche un rapport détaillé des problèmes détectés

### Script de Correction Automatique

Pour exécuter le script de correction automatique :

```bash
python fix_pairs_images_auto.py
```

Ce script :
1. Détecte automatiquement la base de données
2. Crée une sauvegarde de la base de données
3. Récupère tous les exercices de type 'pairs'
4. Corrige les chemins d'images dans chaque exercice
5. Met à jour la base de données
6. Affiche un rapport des corrections effectuées

## Avantages de la Solution

1. **Indépendance du serveur** : Les scripts fonctionnent sans nécessiter un serveur Flask en cours d'exécution
2. **Détection automatique** : La base de données est détectée automatiquement, quel que soit son emplacement
3. **Sauvegarde robuste** : Une sauvegarde est créée avant toute modification
4. **Vérification locale** : Les images sont vérifiées directement sur le système de fichiers
5. **Logs détaillés** : Des logs détaillés facilitent le diagnostic et le suivi

## Conclusion

Les améliorations apportées aux scripts de diagnostic et de correction automatique permettent une utilisation plus flexible et robuste, indépendamment de l'environnement de déploiement. La détection dynamique de la base de données et la vérification locale des fichiers d'images éliminent les dépendances externes et garantissent un fonctionnement fiable dans tous les contextes.

Ces scripts constituent une solution complète pour la gestion des chemins d'images dans les exercices de type "paires", assurant une expérience utilisateur optimale et facilitant la maintenance de l'application.
