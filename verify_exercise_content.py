import json
from flask import Flask
from app import app, db, Exercise

def verify_exercise_content():
    """
    Vérifie le contenu de l'exercice à texte à trous ID 7
    pour s'assurer que les séparateurs < ont bien des espaces autour d'eux.
    """
    with app.app_context():
        # Récupérer l'exercice à texte à trous
        exercise_id = 7
        exercise = Exercise.query.get(exercise_id)
        
        if not exercise:
            print(f"Exercice ID {exercise_id} non trouvé")
            return
        
        print(f"Exercice ID {exercise_id}: {exercise.title}")
        print(f"Type: {exercise.exercise_type}")
        
        try:
            content = json.loads(exercise.content)
            print("\nContenu brut:")
            print(json.dumps(content, indent=2, ensure_ascii=False))
            
            # Vérifier le format du contenu
            if 'sentences' in content:
                print("\nFormat 'sentences' détecté")
                for i, sentence in enumerate(content['sentences']):
                    print(f"Phrase {i+1}: {sentence}")
                    # Vérifier les séparateurs
                    if "<" in sentence:
                        if " < " in sentence:
                            print(f"✅ Les séparateurs ont des espaces")
                        else:
                            print(f"❌ Les séparateurs n'ont PAS d'espaces")
                            # Corriger le format
                            corrected = sentence.replace("<", " < ")
                            print(f"Format corrigé: {corrected}")
                            # Mettre à jour le contenu
                            content['sentences'][i] = corrected
            
            # Vérifier les mots disponibles
            if 'words' in content:
                print("\nMots disponibles:")
                print(content['words'])
            elif 'available_words' in content:
                print("\nMots disponibles (format ancien):")
                print(content['available_words'])
            
            # Compter les blancs dans le contenu
            total_blanks_in_content = 0
            if 'sentences' in content:
                sentences_blanks = sum(s.count('___') for s in content['sentences'])
                total_blanks_in_content = sentences_blanks
                print(f"\nNombre de blancs dans 'sentences': {sentences_blanks}")
            elif 'text' in content:
                text_blanks = content['text'].count('___')
                total_blanks_in_content = text_blanks
                print(f"\nNombre de blancs dans 'text': {text_blanks}")
            
            # Récupérer les réponses correctes
            correct_answers = content.get('words', []) or content.get('available_words', [])
            print(f"\nRéponses correctes: {correct_answers}")
            print(f"Nombre de réponses correctes: {len(correct_answers)}")
            
            # Vérifier la cohérence
            if total_blanks_in_content != len(correct_answers):
                print(f"⚠️ ATTENTION: Le nombre de blancs ({total_blanks_in_content}) ne correspond pas au nombre de réponses ({len(correct_answers)})")
            else:
                print(f"✅ Le nombre de blancs ({total_blanks_in_content}) correspond au nombre de réponses ({len(correct_answers)})")
            
            # Si des corrections ont été apportées, mettre à jour l'exercice
            if 'sentences' in content and any("<" in s and " < " not in s for s in content['sentences']):
                print("\nMise à jour du contenu de l'exercice avec les séparateurs corrigés...")
                exercise.content = json.dumps(content, ensure_ascii=False)
                db.session.commit()
                print("✅ Exercice mis à jour avec succès")
            
        except json.JSONDecodeError:
            print(f"Erreur: Le contenu de l'exercice n'est pas un JSON valide")
            print(f"Contenu brut: {exercise.content}")

if __name__ == "__main__":
    verify_exercise_content()
