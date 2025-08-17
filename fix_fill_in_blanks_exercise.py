import json
from app import app, db, Exercise

def fix_fill_in_blanks_exercise(exercise_id):
    """
    Corrige un exercice à texte à trous pour résoudre les problèmes de scoring.
    
    Problèmes identifiés:
    1. Les blancs adjacents séparés uniquement par '<' sont mal interprétés
    2. Le système ne reconnaît pas correctement les séparateurs entre les blancs
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
        
        # Corriger le problème des blancs adjacents dans les phrases
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
        
        # Mettre à jour l'exercice dans la base de données
        exercise.content = json.dumps(content, ensure_ascii=False)
        db.session.commit()
        
        print(f"Exercice {exercise_id} corrigé avec succès.")
        print(f"Nouveau contenu: {content}")
        return True

if __name__ == "__main__":
    # ID de l'exercice à corriger
    exercise_id = 7
    success = fix_fill_in_blanks_exercise(exercise_id)
    
    if success:
        print("\nL'exercice a été corrigé. Vous devriez maintenant obtenir un score correct.")
        print("Instructions pour tester:")
        print("1. Connectez-vous à l'application")
        print("2. Accédez à l'exercice corrigé")
        print("3. Placez les mots dans l'ordre correct: 0 < 1 < 2 < 3 < 4")
        print("4. Soumettez vos réponses et vérifiez que le score est de 100%")
    else:
        print("\nLa correction a échoué. Veuillez vérifier les messages d'erreur ci-dessus.")
