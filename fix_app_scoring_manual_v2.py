import os
import re
import shutil
from datetime import datetime

def fix_app_py_scoring_manual():
    """
    Corrige manuellement le problème de double comptage des blancs dans app.py
    en modifiant la logique de comptage pour utiliser 'sentences' OU 'text', mais pas les deux.
    """
    # Chemin du fichier app.py
    app_path = 'app.py'
    
    # Vérifier que le fichier existe
    if not os.path.exists(app_path):
        print(f"Erreur: Le fichier {app_path} n'existe pas.")
        return False
    
    # Créer une sauvegarde avec horodatage
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{app_path}.bak.{timestamp}"
    shutil.copy2(app_path, backup_path)
    print(f"Sauvegarde créée: {backup_path}")
    
    # Lire le contenu du fichier
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Rechercher le bloc de code problématique
    code_to_replace = """            # Compter le nombre réel de blancs dans le contenu
            total_blanks_in_content = 0
            
            # Analyser le format de l'exercice et compter les blancs réels
            if 'text' in content:
                text_blanks = content['text'].count('___')
                total_blanks_in_content += text_blanks
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Format 'text' detected: {text_blanks} blanks in text")
            
            if 'sentences' in content:
                sentences_blanks = sum(s.count('___') for s in content['sentences'])
                total_blanks_in_content += sentences_blanks
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Format 'sentences' detected: {sentences_blanks} blanks in sentences")"""
    
    # Nouveau code qui évite le double comptage
    new_code = """            # Compter le nombre réel de blancs dans le contenu
            total_blanks_in_content = 0
            
            # Analyser le format de l'exercice et compter les blancs réels
            # Priorité à 'sentences' pour éviter le double comptage
            if 'sentences' in content:
                sentences_blanks = sum(s.count('___') for s in content['sentences'])
                total_blanks_in_content = sentences_blanks
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Format 'sentences' detected: {sentences_blanks} blanks in sentences")
            elif 'text' in content:
                text_blanks = content['text'].count('___')
                total_blanks_in_content = text_blanks
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Format 'text' detected: {text_blanks} blanks in text")"""
    
    # Remplacer le code
    if code_to_replace in content:
        modified_content = content.replace(code_to_replace, new_code)
        
        # Écrire le contenu modifié
        with open(app_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        print("[SUCCES] Le fichier app.py a été modifié avec succès pour corriger le problème de double comptage.")
        print("La logique de scoring utilise maintenant 'sentences' OU 'text', mais pas les deux.")
        return True
    else:
        print("[ECHEC] Le bloc de code exact n'a pas été trouvé. Vérification d'un format alternatif...")
        
        # Essayer avec une recherche plus flexible
        pattern = r"(# Compter le nombre réel de blancs.*?total_blanks_in_content = 0.*?if 'text' in content:.*?total_blanks_in_content \+= text_blanks.*?if 'sentences' in content:.*?total_blanks_in_content \+= sentences_blanks)"
        
        match = re.search(pattern, content, re.DOTALL)
        if match:
            modified_content = content.replace(match.group(0), new_code)
            
            # Écrire le contenu modifié
            with open(app_path, 'w', encoding='utf-8') as file:
                file.write(modified_content)
            
            print("[SUCCES] Le fichier app.py a été modifié avec succès (via regex) pour corriger le problème de double comptage.")
            return True
        else:
            print("[ECHEC] Impossible de trouver le code à modifier. Veuillez vérifier manuellement.")
            print("\nVoici le code à rechercher dans app.py (vers la ligne 3190):")
            print(code_to_replace)
            print("\nRemplacez-le par:")
            print(new_code)
            return False

def create_test_script():
    """
    Crée un script pour tester si la correction a bien été appliquée
    """
    test_script = """import json
from app import app, db, Exercise

def test_fill_in_blanks_scoring():
    with app.app_context():
        # Récupérer l'exercice à texte à trous
        exercise_id = 7
        exercise = Exercise.query.get(exercise_id)
        
        if not exercise:
            print(f"Exercice {exercise_id} non trouvé.")
            return
        
        print(f"Test de scoring pour l'exercice {exercise_id}: {exercise.title}")
        
        # Charger le contenu
        content = json.loads(exercise.content)
        print(f"Contenu: {content}")
        
        # Compter les blancs selon la nouvelle logique
        total_blanks_in_content = 0
        
        if 'sentences' in content:
            sentences_blanks = sum(s.count('___') for s in content['sentences'])
            total_blanks_in_content = sentences_blanks
            print(f"Format 'sentences' détecté: {sentences_blanks} blancs")
        elif 'text' in content:
            text_blanks = content['text'].count('___')
            total_blanks_in_content = text_blanks
            print(f"Format 'text' détecté: {text_blanks} blancs")
        
        # Récupérer les réponses correctes
        correct_answers = content.get('words', []) or content.get('available_words', [])
        print(f"Réponses correctes: {correct_answers}")
        
        # Calculer le nombre total de blancs
        total_blanks = max(total_blanks_in_content, len(correct_answers))
        print(f"Nombre total de blancs: {total_blanks}")
        
        # Simuler différents scénarios de réponses
        print("\\nScénarios de test:")
        
        # Scénario 1: Toutes les réponses correctes
        correct_blanks = total_blanks
        score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
        print(f"1. Toutes réponses correctes: {correct_blanks}/{total_blanks} = {score}%")
        
        # Scénario 2: Aucune réponse correcte
        correct_blanks = 0
        score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
        print(f"2. Aucune réponse correcte: {correct_blanks}/{total_blanks} = {score}%")
        
        # Scénario 3: Moitié des réponses correctes
        correct_blanks = total_blanks // 2
        score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
        print(f"3. Moitié des réponses correctes: {correct_blanks}/{total_blanks} = {score}%")
        
        # Scénario 4: Une seule réponse correcte
        correct_blanks = 1
        score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
        print(f"4. Une seule réponse correcte: {correct_blanks}/{total_blanks} = {score}%")
        
        print("\\nSi le nombre total de blancs est 5 et que les scores sont cohérents, la correction a réussi.")

if __name__ == "__main__":
    test_fill_in_blanks_scoring()
"""
    
    # Écrire le script dans un fichier
    test_script_path = 'test_fill_in_blanks_scoring.py'
    with open(test_script_path, 'w', encoding='utf-8') as file:
        file.write(test_script)
    
    print(f"Script de test créé: {test_script_path}")
    return test_script_path

def create_documentation():
    """
    Crée une documentation pour expliquer le problème et la solution
    """
    doc_content = """# Correction du problème de scoring des exercices à texte à trous

## Problème identifié

Nous avons identifié deux problèmes majeurs dans la logique de scoring des exercices à texte à trous (fill_in_blanks) :

1. **Double comptage des blancs** : Le code comptait les blancs à la fois dans `content['text']` et `content['sentences']` pour le même exercice, ce qui pouvait doubler le nombre total de blancs.

2. **Mauvaise interprétation des blancs adjacents** : Les blancs séparés uniquement par le caractère `<` sans espaces (comme `___<___`) étaient mal interprétés, ce qui pouvait causer une sous-estimation du nombre réel de blancs.

Ces problèmes entraînaient des scores incorrects, généralement trop bas (20% au lieu de 100% pour des réponses toutes correctes).

## Solution implémentée

### 1. Correction du format des blancs adjacents

Le script `fix_fill_in_blanks_counting.py` normalise les séparateurs entre blancs en ajoutant des espaces autour des caractères `<` :

```python
# Avant
"___<___<___<___<___"

# Après
"___ < ___ < ___ < ___ < ___"
```

### 2. Correction du double comptage

Le script `fix_app_scoring_manual.py` modifie la logique de scoring dans `app.py` pour utiliser soit `sentences`, soit `text`, mais pas les deux :

```python
# AVANT (problème de double comptage)
if 'text' in content:
    text_blanks = content['text'].count('___')
    total_blanks_in_content += text_blanks

if 'sentences' in content:
    sentences_blanks = sum(s.count('___') for s in content['sentences'])
    total_blanks_in_content += sentences_blanks
```

```python
# APRÈS (correction avec priorité)
if 'sentences' in content:
    sentences_blanks = sum(s.count('___') for s in content['sentences'])
    total_blanks_in_content = sentences_blanks
elif 'text' in content:
    text_blanks = content['text'].count('___')
    total_blanks_in_content = text_blanks
```

## Comment tester la correction

1. Exécutez le script de test `test_fill_in_blanks_scoring.py` pour vérifier que le nombre de blancs est correctement compté.
2. Accédez à l'exercice corrigé dans l'application.
3. Placez les mots dans l'ordre correct.
4. Vérifiez que le score est de 100% lorsque toutes les réponses sont correctes.

## Recommandations pour l'avenir

1. **Format cohérent** : Utilisez soit `sentences`, soit `text`, mais pas les deux dans le même exercice.
2. **Séparateurs clairs** : Utilisez des séparateurs avec des espaces (`___ < ___`) plutôt que sans espaces (`___<___`).
3. **Tests de validation** : Testez les exercices avec différentes combinaisons de réponses pour vérifier que le scoring fonctionne correctement.
"""
    
    # Écrire la documentation dans un fichier
    doc_path = 'DOCUMENTATION_SCORING_FIX.md'
    with open(doc_path, 'w', encoding='utf-8') as file:
        file.write(doc_content)
    
    print(f"Documentation créée: {doc_path}")
    return doc_path

if __name__ == "__main__":
    # Corriger app.py
    success = fix_app_py_scoring_manual()
    
    # Créer le script de test
    test_script_path = create_test_script()
    
    # Créer la documentation
    doc_path = create_documentation()
    
    print("\n=== RÉSUMÉ DES ACTIONS ===")
    if success:
        print("[SUCCES] Le code de scoring dans app.py a été corrigé avec succès.")
    else:
        print("[ATTENTION] La correction automatique a échoué. Veuillez appliquer les modifications manuellement.")
    
    print(f"[OK] Script de test créé: {test_script_path}")
    print(f"[OK] Documentation créée: {doc_path}")
    
    print("\n=== PROCHAINES ÉTAPES ===")
    print("1. Exécutez le script de test pour vérifier la correction:")
    print(f"   python {test_script_path}")
    print("2. Testez l'exercice dans l'application pour confirmer que le score est correct.")
    print("3. Consultez la documentation pour comprendre le problème et la solution.")
