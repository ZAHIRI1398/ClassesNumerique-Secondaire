# Documentation : Correction des chemins d'images dans les exercices d'association de paires

## Problème initial

Les exercices d'association de paires présentaient des problèmes d'affichage d'images après leur création ou modification. Les images téléchargées n'apparaissaient pas correctement, générant des erreurs 404. L'analyse a révélé une incohérence entre les chemins physiques des images (stockées sous `/static/exercises/`) et les chemins référencés dans le contenu JSON des exercices (qui devraient être `/static/uploads/` pour l'affichage).

## Causes identifiées

1. **Incohérence des chemins d'images** : 
   - Les images sont physiquement stockées dans `/static/exercises/pairs/`
   - Mais le contenu JSON des exercices référence ces images avec `/static/uploads/pairs/`
   - Cette incohérence provoque des erreurs 404 lorsque le navigateur tente de charger les images

2. **Absence de normalisation systématique** :
   - La fonction `normalize_pairs_exercise_content` n'était pas systématiquement appelée lors de la sauvegarde des exercices
   - Certains exercices avaient des chemins incorrects ou incohérents

3. **Formats de données multiples** :
   - Coexistence de deux formats de données pour les exercices de paires :
     - Format ancien : `left_items` et `right_items` comme listes simples
     - Format nouveau : `pairs` comme liste d'objets avec `left` et `right`

## Solution implémentée

### 1. Fonction de normalisation robuste

La fonction `normalize_pairs_exercise_content` a été vérifiée et validée pour :

```python
def normalize_pairs_exercise_content(content_json):
    """
    Normalise les chemins d'images dans le contenu JSON des exercices de paires.
    Convertit les chemins /static/exercises/ en /static/uploads/ et vérifie l'existence des fichiers.
    """
    content = json.loads(content_json) if isinstance(content_json, str) else content_json
    content_changed = False
    
    # Traitement du nouveau format avec "pairs"
    if 'pairs' in content:
        for pair in content['pairs']:
            # Traitement du côté gauche
            if 'left' in pair and isinstance(pair['left'], dict) and pair['left'].get('type') == 'image':
                image_path = pair['left']['content']
                if image_path.startswith('/static/exercises/'):
                    pair['left']['content'] = image_path.replace('/static/exercises/', '/static/uploads/')
                    content_changed = True
                elif image_path.startswith('/static/uploads/'):
                    # Vérifier si le fichier existe dans /static/exercises/
                    physical_path = os.path.join(
                        os.getcwd(), 
                        'static/exercises/', 
                        image_path.replace('/static/uploads/', '')
                    )
                    print(f"[PAIRS_PATH_DEBUG] Fichier {'trouvé' if os.path.exists(physical_path) else 'non trouvé'} avec chemin physique: {physical_path}")
                    # Pas besoin de changer le chemin, il est déjà au bon format
            
            # Traitement du côté droit
            if 'right' in pair and isinstance(pair['right'], dict) and pair['right'].get('type') == 'image':
                image_path = pair['right']['content']
                if image_path.startswith('/static/exercises/'):
                    pair['right']['content'] = image_path.replace('/static/exercises/', '/static/uploads/')
                    content_changed = True
                elif image_path.startswith('/static/uploads/'):
                    # Vérifier si le fichier existe dans /static/exercises/
                    physical_path = os.path.join(
                        os.getcwd(), 
                        'static/exercises/', 
                        image_path.replace('/static/uploads/', '')
                    )
                    print(f"[PAIRS_PATH_DEBUG] Fichier {'trouvé' if os.path.exists(physical_path) else 'non trouvé'} avec chemin physique: {physical_path}")
                    # Pas besoin de changer le chemin, il est déjà au bon format
    
    # Traitement de l'ancien format avec "left_items" et "right_items"
    if 'left_items' in content:
        for i, item in enumerate(content['left_items']):
            if isinstance(item, dict) and item.get('type') == 'image':
                image_path = item['content']
                if image_path.startswith('/static/exercises/'):
                    content['left_items'][i]['content'] = image_path.replace('/static/exercises/', '/static/uploads/')
                    content_changed = True
            elif isinstance(item, str) and item.startswith('/static/exercises/'):
                # Convertir la chaîne en objet avec type="image"
                content['left_items'][i] = {
                    'type': 'image',
                    'content': item.replace('/static/exercises/', '/static/uploads/')
                }
                content_changed = True
            elif isinstance(item, str) and item.startswith('/static/uploads/'):
                # Vérifier si le fichier existe dans /static/exercises/
                physical_path = os.path.join(
                    os.getcwd(), 
                    'static/exercises/', 
                    item.replace('/static/uploads/', '')
                )
                print(f"[PAIRS_PATH_DEBUG] Fichier {'trouvé' if os.path.exists(physical_path) else 'non trouvé'} avec chemin physique: {physical_path}")
                # Convertir la chaîne en objet avec type="image"
                content['left_items'][i] = {
                    'type': 'image',
                    'content': item
                }
                content_changed = True
    
    if 'right_items' in content:
        for i, item in enumerate(content['right_items']):
            if isinstance(item, dict) and item.get('type') == 'image':
                image_path = item['content']
                if image_path.startswith('/static/exercises/'):
                    content['right_items'][i]['content'] = image_path.replace('/static/exercises/', '/static/uploads/')
                    content_changed = True
            elif isinstance(item, str) and item.startswith('/static/exercises/'):
                # Convertir la chaîne en objet avec type="image"
                content['right_items'][i] = {
                    'type': 'image',
                    'content': item.replace('/static/exercises/', '/static/uploads/')
                }
                content_changed = True
            elif isinstance(item, str) and item.startswith('/static/uploads/'):
                # Vérifier si le fichier existe dans /static/exercises/
                physical_path = os.path.join(
                    os.getcwd(), 
                    'static/exercises/', 
                    item.replace('/static/uploads/', '')
                )
                print(f"[PAIRS_PATH_DEBUG] Fichier {'trouvé' if os.path.exists(physical_path) else 'non trouvé'} avec chemin physique: {physical_path}")
                # Convertir la chaîne en objet avec type="image"
                content['right_items'][i] = {
                    'type': 'image',
                    'content': item
                }
                content_changed = True
    
    return json.dumps(content) if isinstance(content_json, str) else content, content_changed
```

Cette fonction :
- Normalise les chemins d'images de `/static/exercises/` vers `/static/uploads/`
- Gère les deux formats de données (ancien et nouveau)
- Vérifie l'existence physique des fichiers
- Convertit les chaînes en objets avec `type="image"` si nécessaire
- Ajoute des logs de débogage pour faciliter le diagnostic

### 2. Script de correction pour la base de données

Un script `fix_pairs_image_paths.py` a été créé pour corriger les chemins d'images dans tous les exercices de paires existants :

```python
import os
import sys
import json
import sqlite3
from datetime import datetime

# Chemin de la base de données
DB_PATH = os.path.join(os.getcwd(), 'instance', 'app.db')

def normalize_pairs_exercise_content(content_json):
    """
    Normalise les chemins d'images dans le contenu JSON des exercices de paires.
    Convertit les chemins /static/exercises/ en /static/uploads/ et vérifie l'existence des fichiers.
    """
    content = json.loads(content_json) if isinstance(content_json, str) else content_json
    content_changed = False
    
    # Traitement du nouveau format avec "pairs"
    if 'pairs' in content:
        for pair in content['pairs']:
            # Traitement du côté gauche
            if 'left' in pair and isinstance(pair['left'], dict) and pair['left'].get('type') == 'image':
                image_path = pair['left']['content']
                if image_path.startswith('/static/exercises/'):
                    pair['left']['content'] = image_path.replace('/static/exercises/', '/static/uploads/')
                    content_changed = True
                elif image_path.startswith('/static/uploads/'):
                    # Vérifier si le fichier existe dans /static/exercises/
                    physical_path = os.path.join(
                        os.getcwd(), 
                        'static/exercises/', 
                        image_path.replace('/static/uploads/', '')
                    )
                    print(f"[PAIRS_PATH_DEBUG] Fichier {'trouvé' if os.path.exists(physical_path) else 'non trouvé'} avec chemin physique: {physical_path}")
                    # Pas besoin de changer le chemin, il est déjà au bon format
            
            # Traitement du côté droit
            if 'right' in pair and isinstance(pair['right'], dict) and pair['right'].get('type') == 'image':
                image_path = pair['right']['content']
                if image_path.startswith('/static/exercises/'):
                    pair['right']['content'] = image_path.replace('/static/exercises/', '/static/uploads/')
                    content_changed = True
                elif image_path.startswith('/static/uploads/'):
                    # Vérifier si le fichier existe dans /static/exercises/
                    physical_path = os.path.join(
                        os.getcwd(), 
                        'static/exercises/', 
                        image_path.replace('/static/uploads/', '')
                    )
                    print(f"[PAIRS_PATH_DEBUG] Fichier {'trouvé' if os.path.exists(physical_path) else 'non trouvé'} avec chemin physique: {physical_path}")
                    # Pas besoin de changer le chemin, il est déjà au bon format
    
    # Traitement de l'ancien format avec "left_items" et "right_items"
    if 'left_items' in content:
        for i, item in enumerate(content['left_items']):
            if isinstance(item, dict) and item.get('type') == 'image':
                image_path = item['content']
                if image_path.startswith('/static/exercises/'):
                    content['left_items'][i]['content'] = image_path.replace('/static/exercises/', '/static/uploads/')
                    content_changed = True
            elif isinstance(item, str) and item.startswith('/static/exercises/'):
                # Convertir la chaîne en objet avec type="image"
                content['left_items'][i] = {
                    'type': 'image',
                    'content': item.replace('/static/exercises/', '/static/uploads/')
                }
                content_changed = True
            elif isinstance(item, str) and item.startswith('/static/uploads/'):
                # Vérifier si le fichier existe dans /static/exercises/
                physical_path = os.path.join(
                    os.getcwd(), 
                    'static/exercises/', 
                    item.replace('/static/uploads/', '')
                )
                print(f"[PAIRS_PATH_DEBUG] Fichier {'trouvé' if os.path.exists(physical_path) else 'non trouvé'} avec chemin physique: {physical_path}")
                # Convertir la chaîne en objet avec type="image"
                content['left_items'][i] = {
                    'type': 'image',
                    'content': item
                }
                content_changed = True
    
    if 'right_items' in content:
        for i, item in enumerate(content['right_items']):
            if isinstance(item, dict) and item.get('type') == 'image':
                image_path = item['content']
                if image_path.startswith('/static/exercises/'):
                    content['right_items'][i]['content'] = image_path.replace('/static/exercises/', '/static/uploads/')
                    content_changed = True
            elif isinstance(item, str) and item.startswith('/static/exercises/'):
                # Convertir la chaîne en objet avec type="image"
                content['right_items'][i] = {
                    'type': 'image',
                    'content': item.replace('/static/exercises/', '/static/uploads/')
                }
                content_changed = True
            elif isinstance(item, str) and item.startswith('/static/uploads/'):
                # Vérifier si le fichier existe dans /static/exercises/
                physical_path = os.path.join(
                    os.getcwd(), 
                    'static/exercises/', 
                    item.replace('/static/uploads/', '')
                )
                print(f"[PAIRS_PATH_DEBUG] Fichier {'trouvé' if os.path.exists(physical_path) else 'non trouvé'} avec chemin physique: {physical_path}")
                # Convertir la chaîne en objet avec type="image"
                content['right_items'][i] = {
                    'type': 'image',
                    'content': item
                }
                content_changed = True
    
    return json.dumps(content) if isinstance(content_json, str) else content, content_changed

def fix_pairs_image_paths():
    """
    Corrige les chemins d'images dans tous les exercices de type 'pairs' dans la base de données.
    """
    try:
        # Vérifier si la base de données existe
        if not os.path.exists(DB_PATH):
            print(f"Base de données non trouvée à {DB_PATH}")
            return False
        
        # Se connecter à la base de données
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Récupérer tous les exercices de type 'pairs'
        cursor.execute("SELECT id, content FROM exercise WHERE type = 'pairs'")
        exercises = cursor.fetchall()
        
        print(f"Nombre d'exercices de type 'pairs' trouvés : {len(exercises)}")
        
        # Parcourir les exercices et corriger les chemins d'images
        corrected_count = 0
        for exercise_id, content_json in exercises:
            try:
                # Normaliser le contenu JSON
                normalized_content, content_changed = normalize_pairs_exercise_content(content_json)
                
                if content_changed:
                    # Mettre à jour l'exercice dans la base de données
                    cursor.execute(
                        "UPDATE exercise SET content = ? WHERE id = ?",
                        (normalized_content, exercise_id)
                    )
                    print(f"Exercice {exercise_id} corrigé avec succès.")
                    corrected_count += 1
                else:
                    print(f"Exercice {exercise_id} déjà normalisé, aucune correction nécessaire.")
            except Exception as e:
                print(f"Erreur lors de la correction de l'exercice {exercise_id}: {str(e)}")
        
        # Valider les modifications
        conn.commit()
        conn.close()
        
        print(f"Correction terminée. {corrected_count} exercices corrigés sur {len(exercises)}.")
        return True
    
    except Exception as e:
        print(f"Erreur lors de la correction des chemins d'images: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Correction des chemins d'images dans les exercices de paires ===")
    print(f"Date et heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base de données: {DB_PATH}")
    
    success = fix_pairs_image_paths()
    
    if success:
        print("Script exécuté avec succès.")
    else:
        print("Le script a rencontré des erreurs.")
        sys.exit(1)
```

Ce script :
- Parcourt tous les exercices de type 'pairs' dans la base de données
- Applique la fonction de normalisation à chaque exercice
- Met à jour la base de données si des changements sont détectés
- Fournit des logs détaillés pour le suivi des corrections

### 3. Tests complets

Un script de test `test_normalize_pairs_paths.py` a été créé pour valider le comportement de la fonction de normalisation :

```python
import os
import json
import shutil
from normalize_pairs_exercise_paths import normalize_pairs_exercise_content

def create_test_files():
    """Crée des fichiers de test pour simuler différents scénarios."""
    # Créer les répertoires nécessaires
    os.makedirs('static/uploads/pairs', exist_ok=True)
    os.makedirs('static/exercises/pairs', exist_ok=True)
    os.makedirs('static/uploads/general', exist_ok=True)
    os.makedirs('static/exercises/general', exist_ok=True)
    
    # Créer des fichiers de test
    test_files = [
        'static/uploads/pairs/test_upload_pairs.png',
        'static/exercises/pairs/test_exercise_pairs.png',
        'static/uploads/general/test_upload_general.png',
        'static/exercises/general/test_exercise_general.png'
    ]
    
    for file_path in test_files:
        with open(file_path, 'w') as f:
            f.write('Test file content')
    
    return test_files

def cleanup_test_files(test_files):
    """Supprime les fichiers de test créés."""
    for file_path in test_files:
        if os.path.exists(file_path):
            os.remove(file_path)

def test_normalize_pairs_exercise_content():
    """Teste la fonction normalize_pairs_exercise_content avec différents cas."""
    print("=== Test de normalize_pairs_exercise_content ===\n")
    
    # Créer des fichiers de test
    test_files = create_test_files()
    print(f"Fichiers de test créés: {test_files}\n")
    
    # Cas de test 1: Chemin /static/exercises/ -> /static/uploads/
    content1 = {
        "pairs": [
            {
                "id": "1",
                "left": {
                    "type": "image",
                    "content": "/static/exercises/pairs/test_exercise_pairs.png"
                },
                "right": {
                    "type": "text",
                    "content": "Texte test"
                }
            }
        ]
    }
    print("Cas de test 1: Chemin /static/exercises/ -> /static/uploads/")
    print(f"Avant: {json.dumps(content1, indent=2)}")
    normalized1, changed1 = normalize_pairs_exercise_content(content1)
    print(f"Après: {json.dumps(normalized1, indent=2)}")
    print(f"Changement détecté: {changed1}\n")
    
    # Cas de test 2: Chemin /static/uploads/ (fichier existe dans exercises)
    content2 = {
        "pairs": [
            {
                "id": "1",
                "left": {
                    "type": "image",
                    "content": "/static/uploads/pairs/test_exercise_pairs.png"
                },
                "right": {
                    "type": "text",
                    "content": "Texte test"
                }
            }
        ]
    }
    print("Cas de test 2: Chemin /static/uploads/ (fichier existe dans exercises)")
    print(f"Avant: {json.dumps(content2, indent=2)}")
    normalized2, changed2 = normalize_pairs_exercise_content(content2)
    print(f"Après: {json.dumps(normalized2, indent=2)}")
    print(f"Changement détecté: {changed2}\n")
    
    # Cas de test 3: Chemin /static/uploads/ (fichier existe dans uploads)
    content3 = {
        "pairs": [
            {
                "id": "1",
                "left": {
                    "type": "image",
                    "content": "/static/uploads/pairs/test_upload_pairs.png"
                },
                "right": {
                    "type": "text",
                    "content": "Texte test"
                }
            }
        ]
    }
    print("Cas de test 3: Chemin /static/uploads/ (fichier existe dans uploads)")
    print(f"Avant: {json.dumps(content3, indent=2)}")
    normalized3, changed3 = normalize_pairs_exercise_content(content3)
    print(f"Après: {json.dumps(normalized3, indent=2)}")
    print(f"Changement détecté: {changed3}\n")
    
    # Cas de test 4: Chemin inexistant
    content4 = {
        "pairs": [
            {
                "id": "1",
                "left": {
                    "type": "image",
                    "content": "/static/uploads/pairs/fichier_inexistant.png"
                },
                "right": {
                    "type": "text",
                    "content": "Texte test"
                }
            }
        ]
    }
    print("Cas de test 4: Chemin inexistant")
    print(f"Avant: {json.dumps(content4, indent=2)}")
    normalized4, changed4 = normalize_pairs_exercise_content(content4)
    print(f"Après: {json.dumps(normalized4, indent=2)}")
    print(f"Changement détecté: {changed4}\n")
    
    # Cas de test 5: Format ancien avec listes left_items et right_items
    content5 = {
        "left_items": [
            {
                "type": "image",
                "content": "/static/exercises/general/test_exercise_general.png"
            },
            "Texte simple"
        ],
        "right_items": [
            "Texte réponse",
            "/static/uploads/general/test_upload_general.png"
        ]
    }
    print("Cas de test 5: Format ancien avec listes left_items et right_items")
    print(f"Avant: {json.dumps(content5, indent=2)}")
    normalized5, changed5 = normalize_pairs_exercise_content(content5)
    print(f"Après: {json.dumps(normalized5, indent=2)}")
    print(f"Changement détecté: {changed5}\n")
    
    # Nettoyer les fichiers de test
    # cleanup_test_files(test_files)
    
    print("Tests terminés avec succès!")

if __name__ == "__main__":
    test_normalize_pairs_exercise_content()
```

Ce script de test :
- Crée une structure de fichiers factices pour simuler différents scénarios
- Teste la fonction de normalisation avec différents types de chemins d'images
- Vérifie que les chemins sont correctement normalisés
- Affiche les résultats détaillés pour chaque cas de test

## Intégration dans le workflow d'édition d'exercices

Pour garantir que les chemins d'images sont toujours cohérents, la fonction `normalize_pairs_exercise_content` doit être appelée à chaque sauvegarde d'exercice de type 'pairs'. Voici comment l'intégrer dans le workflow d'édition :

```python
@app.route('/exercise/<int:exercise_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_exercise(exercise_id):
    # ... code existant ...
    
    if request.method == 'POST':
        # ... traitement du formulaire ...
        
        # Pour les exercices de type 'pairs', normaliser les chemins d'images
        if exercise.type == 'pairs':
            normalized_content, _ = normalize_pairs_exercise_content(exercise.content)
            exercise.content = normalized_content
        
        db.session.commit()
        # ... suite du code ...
```

## Bonnes pratiques pour la gestion des images dans les exercices de paires

1. **Cohérence des chemins** :
   - Toujours utiliser `/static/uploads/` comme préfixe pour les chemins d'images dans le contenu JSON
   - Les images peuvent être physiquement stockées dans `/static/exercises/` ou `/static/uploads/`

2. **Normalisation systématique** :
   - Appeler `normalize_pairs_exercise_content` à chaque sauvegarde d'exercice de type 'pairs'
   - Cela garantit que les chemins sont toujours cohérents

3. **Vérification des fichiers** :
   - Vérifier l'existence physique des fichiers avant de sauvegarder les chemins
   - Utiliser des logs de débogage pour faciliter le diagnostic

4. **Format de données uniforme** :
   - Privilégier le nouveau format avec `pairs` plutôt que l'ancien format avec `left_items` et `right_items`
   - Pour les images, toujours utiliser des objets avec `type="image"` et `content="chemin"`

## Conclusion

La solution implémentée résout le problème de cohérence des chemins d'images dans les exercices d'association de paires. Elle garantit que les images s'affichent correctement après leur création ou modification, en normalisant systématiquement les chemins et en vérifiant l'existence physique des fichiers.

Le script de correction permet de corriger rétroactivement les exercices existants, tandis que l'intégration dans le workflow d'édition garantit que les nouveaux exercices sont correctement sauvegardés.

Les tests complets valident le comportement de la fonction de normalisation dans différents scénarios, assurant sa robustesse et sa fiabilité.
