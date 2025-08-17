import json
import os
from datetime import datetime

# Importer l'application Flask et les modèles
from app import app, db
from models import Exercise, ExerciseAttempt, User

def test_fill_in_blanks_scoring():
    """
    Script de test pour vérifier le scoring des exercices 'fill_in_blanks'
    après l'application des corrections.
    """
    print("=" * 80)
    print("TEST DE SCORING DES EXERCICES TEXTE À TROUS (FILL_IN_BLANKS)")
    print("=" * 80)
    
    # Utiliser le contexte de l'application Flask
    with app.app_context():
        try:
            # Récupérer tous les exercices de type 'fill_in_blanks'
            exercises = Exercise.query.filter_by(exercise_type='fill_in_blanks').all()
            
            print(f"\nNombre d'exercices 'fill_in_blanks' trouvés: {len(exercises)}")
            print("-" * 80)
            
            if not exercises:
                print("Aucun exercice 'fill_in_blanks' trouvé dans la base de données.")
                return
            
            # Tester chaque exercice
            for exercise in exercises:
                exercise_id = exercise.id
                title = exercise.title
                
                try:
                    content = exercise.get_content()
                    
                    print(f"\nExercice #{exercise_id}: {title}")
                    print(f"Structure: {list(content.keys())}")
                    
                    # Vérifier la structure du contenu
                    has_text = 'text' in content
                    has_sentences = 'sentences' in content
                    has_words = 'words' in content
                    has_available_words = 'available_words' in content
                    has_answers = 'answers' in content
                    
                    # Compter les blancs selon la logique correcte
                    total_blanks_in_content = 0
                    
                    if has_sentences:
                        sentences_blanks = sum(s.count('___') for s in content['sentences'])
                        total_blanks_in_content = sentences_blanks
                        print(f"- Format 'sentences': {sentences_blanks} blancs")
                    elif has_text:
                        text_blanks = content['text'].count('___')
                        total_blanks_in_content = text_blanks
                        print(f"- Format 'text': {text_blanks} blancs")
                    else:
                        print("- ERREUR: Ni 'sentences' ni 'text' trouvés dans le contenu!")
                    
                    # Vérifier les réponses disponibles
                    correct_answers = []
                    if has_words:
                        correct_answers = content['words']
                        print(f"- Mots disponibles ('words'): {correct_answers}")
                    elif has_available_words:
                        correct_answers = content['available_words']
                        print(f"- Mots disponibles ('available_words'): {correct_answers}")
                    else:
                        print("- ERREUR: Aucun mot disponible trouvé!")
                    
                    # Vérifier si le champ 'answers' existe et est cohérent
                    if has_answers:
                        answers = content['answers']
                        print(f"- Réponses ('answers'): {answers}")
                        
                        # Vérifier la cohérence entre answers et blanks
                        if len(answers) != total_blanks_in_content:
                            print(f"- INCOHÉRENCE: {len(answers)} réponses pour {total_blanks_in_content} blancs!")
                        else:
                            print(f"- COHÉRENCE VÉRIFIÉE: {len(answers)} réponses pour {total_blanks_in_content} blancs")
                    else:
                        print("- ERREUR: Champ 'answers' non trouvé!")
                    
                    # Calculer le nombre total de blanks selon la logique de scoring
                    total_blanks = max(total_blanks_in_content, len(correct_answers))
                    print(f"- Total blancs pour scoring: {total_blanks}")
                    
                    # Simuler différents scénarios de scoring
                    print("\n  Simulation de scoring:")
                    
                    # Scénario 1: Toutes les réponses correctes
                    correct_blanks = total_blanks
                    score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
                    print(f"  - Toutes réponses correctes: {correct_blanks}/{total_blanks} = {score:.1f}%")
                    
                    # Scénario 2: Aucune réponse correcte
                    correct_blanks = 0
                    score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
                    print(f"  - Aucune réponse correcte: {correct_blanks}/{total_blanks} = {score:.1f}%")
                    
                    # Scénario 3: Moitié des réponses correctes
                    correct_blanks = total_blanks // 2
                    score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
                    print(f"  - Moitié des réponses correctes: {correct_blanks}/{total_blanks} = {score:.1f}%")
                    
                    # Vérifier si l'exercice a des tentatives récentes
                    attempts = ExerciseAttempt.query.filter_by(exercise_id=exercise_id).order_by(ExerciseAttempt.created_at.desc()).limit(1).all()
                    if attempts:
                        attempt = attempts[0]
                        print(f"\n  Dernière tentative (ID: {attempt.id}):")
                        print(f"  - Score: {attempt.score}%")
                        
                        # Analyser le feedback si disponible
                        try:
                            feedback = json.loads(attempt.feedback) if attempt.feedback else {}
                            if isinstance(feedback, dict) and 'correct_blanks' in feedback and 'total_blanks' in feedback:
                                print(f"  - Détails: {feedback['correct_blanks']}/{feedback['total_blanks']} blancs corrects")
                                print(f"  - Calcul vérifié: ({feedback['correct_blanks']}/{feedback['total_blanks']})*100 = {(feedback['correct_blanks']/feedback['total_blanks'])*100:.1f}%")
                        except:
                            print("  - Impossible d'analyser le feedback")
                    
                except json.JSONDecodeError:
                    print(f"Erreur: Contenu JSON invalide pour l'exercice #{exercise_id}")
                except Exception as e:
                    print(f"Erreur lors de l'analyse de l'exercice #{exercise_id}: {str(e)}")
                
                print("-" * 80)
        
        except Exception as e:
            print(f"Erreur lors de l'exécution du test: {str(e)}")
        
        print("\nTest terminé.")

if __name__ == "__main__":
    test_fill_in_blanks_scoring()
