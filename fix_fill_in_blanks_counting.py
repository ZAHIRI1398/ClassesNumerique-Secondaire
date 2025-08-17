import json
from app import app, db, Exercise

def fix_fill_in_blanks_exercise(exercise_id):
    """
    Corrige un exercice à texte à trous pour résoudre les problèmes de scoring.
    
    Problèmes identifiés:
    1. Double comptage des blancs quand les champs 'text' et 'sentences' existent dans le même exercice
    2. Les blancs adjacents séparés uniquement par '<' sont mal interprétés
    """
    with app.app_context():
        exercise = Exercise.query.filter_by(id=exercise_id).first()
        
        if not exercise:
            print(f"Exercice avec ID {exercise_id} non trouvé.")
            return False
        
        if exercise.exercise_type != 'fill_in_blanks':
            print(f"L'exercice {exercise_id} n'est pas de type 'texte à trous'.")
            return False
        
        print(f"Correction de l'exercice {exercise_id}: {exercise.title}")
        
        # Charger le contenu actuel
        try:
            content = json.loads(exercise.content)
        except json.JSONDecodeError:
            print("Erreur: Impossible de décoder le contenu JSON de l'exercice.")
            return False
        
        # Sauvegarder l'ancien contenu pour référence
        old_content = content.copy()
        print(f"Ancien contenu: {old_content}")
        
        # 1. Corriger le problème des blancs adjacents dans les phrases
        if 'sentences' in content:
            new_sentences = []
            for sentence in content['sentences']:
                # Ajouter des espaces autour des '<' pour éviter la confusion avec les blancs
                corrected_sentence = sentence.replace('___<___', '___ < ___')
                corrected_sentence = corrected_sentence.replace('<___', ' < ___')
                corrected_sentence = corrected_sentence.replace('___<', '___ < ')
                new_sentences.append(corrected_sentence)
            
            content['sentences'] = new_sentences
            print(f"Phrases corrigées: {new_sentences}")
        
        # 2. Vérifier si l'exercice a à la fois 'text' et 'sentences'
        has_text = 'text' in content
        has_sentences = 'sentences' in content
        
        if has_text and has_sentences:
            print("PROBLÈME DÉTECTÉ: L'exercice contient à la fois 'text' et 'sentences'")
            print("Cela peut causer un double comptage des blancs.")
            
            # Compter les blancs dans chaque format
            text_blanks = content['text'].count('___') if has_text else 0
            sentences_blanks = sum(s.count('___') for s in content['sentences']) if has_sentences else 0
            
            print(f"Blancs dans 'text': {text_blanks}")
            print(f"Blancs dans 'sentences': {sentences_blanks}")
            
            # Privilégier le format avec le plus de blancs
            if sentences_blanks >= text_blanks:
                print("Conservation du format 'sentences' et suppression de 'text'")
                if 'text' in content:
                    del content['text']
            else:
                print("Conservation du format 'text' et suppression de 'sentences'")
                if 'sentences' in content:
                    del content['sentences']
        
        # Mettre à jour l'exercice dans la base de données
        exercise.content = json.dumps(content, ensure_ascii=False)
        db.session.commit()
        
        print(f"Exercice {exercise_id} corrigé avec succès.")
        print(f"Nouveau contenu: {content}")
        return True

def fix_app_scoring_logic():
    """
    Modifie le code de scoring dans app.py pour éviter le double comptage des blancs.
    Cette fonction crée un script de modification à exécuter séparément.
    """
    script_content = """
import re

def fix_app_py_scoring():
    # Chemin du fichier app.py
    app_path = 'app.py'
    
    # Lire le contenu du fichier
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Sauvegarder une copie de sauvegarde
    with open(app_path + '.bak.fill_in_blanks_fix', 'w', encoding='utf-8') as file:
        file.write(content)
    
    # Motif à rechercher - code qui fait le double comptage
    pattern = r"(\\s+# Compter le nombre réel de blancs dans le contenu\\s+total_blanks_in_content = 0\\s+)if 'text' in content:\\s+text_blanks = content\\['text'\\].count\\('___'\\)\\s+total_blanks_in_content \\+= text_blanks\\s+.*?\\s+if 'sentences' in content:\\s+sentences_blanks = sum\\(s.count\\('___'\\) for s in content\\['sentences'\\]\\)\\s+total_blanks_in_content \\+= sentences_blanks"
    
    # Nouveau code qui évite le double comptage
    replacement = r"\\1if 'sentences' in content:\\n        sentences_blanks = sum(s.count('___') for s in content['sentences'])\\n        total_blanks_in_content = sentences_blanks\\n        app.logger.info(f\\"[FILL_IN_BLANKS_DEBUG] Format 'sentences' detected: {sentences_blanks} blanks in sentences\\")\\n    elif 'text' in content:\\n        text_blanks = content['text'].count('___')\\n        total_blanks_in_content = text_blanks\\n        app.logger.info(f\\"[FILL_IN_BLANKS_DEBUG] Format 'text' detected: {text_blanks} blanks in text\\")"
    
    # Appliquer la modification
    modified_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Vérifier si des modifications ont été apportées
    if modified_content == content:
        print("Aucune modification n'a été apportée. Le motif n'a pas été trouvé.")
        return False
    
    # Écrire le contenu modifié
    with open(app_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("Le fichier app.py a été modifié avec succès pour corriger le problème de double comptage.")
    return True

if __name__ == "__main__":
    fix_app_py_scoring()
"""
    
    # Écrire le script dans un fichier
    script_path = 'fix_app_scoring_logic.py'
    with open(script_path, 'w', encoding='utf-8') as file:
        file.write(script_content)
    
    print(f"Script de correction de la logique de scoring créé: {script_path}")
    print("Exécutez ce script pour modifier app.py et corriger le problème de double comptage.")
    return script_path

if __name__ == "__main__":
    # ID de l'exercice à corriger
    exercise_id = 7
    success = fix_fill_in_blanks_exercise(exercise_id)
    
    # Créer le script pour corriger la logique de scoring dans app.py
    script_path = fix_app_scoring_logic()
    
    if success:
        print("\nL'exercice a été corrigé. Vous devriez maintenant obtenir un score correct.")
        print("Instructions pour tester:")
        print("1. Exécutez le script de correction de la logique de scoring:")
        print(f"   python {script_path}")
        print("2. Connectez-vous à l'application")
        print("3. Accédez à l'exercice corrigé")
        print("4. Placez les mots dans l'ordre correct: 0 < 1 < 2 < 3 < 4")
        print("5. Soumettez vos réponses et vérifiez que le score est de 100%")
    else:
        print("\nLa correction a échoué. Veuillez vérifier les messages d'erreur ci-dessus.")
