import json
import os
from datetime import datetime

# Importer l'application Flask et les modèles
from app import app, db
from models import Exercise, ExerciseAttempt, User

def diagnose_fill_in_blanks():
    """
    Script de diagnostic pour analyser tous les exercices 'fill_in_blanks' dans la base de données
    et vérifier leur structure et cohérence pour le scoring.
    """
    print("=" * 80)
    print("DIAGNOSTIC DES EXERCICES TEXTE À TROUS (FILL_IN_BLANKS)")
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
            
            # Analyser chaque exercice
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
                        
                        # Détail des blancs par phrase
                        for i, sentence in enumerate(content['sentences']):
                            blanks_in_sentence = sentence.count('___')
                            print(f"  - Phrase {i+1}: '{sentence}' contient {blanks_in_sentence} blancs")
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
                        print("- MANQUANT: Champ 'answers' non trouvé!")
                    
                    # Calculer le nombre total de blanks selon la logique de scoring
                    total_blanks = max(total_blanks_in_content, len(correct_answers))
                    print(f"- Total blancs pour scoring: {total_blanks}")
                    
                    # Récupérer les tentatives récentes
                    attempts = ExerciseAttempt.query.filter_by(exercise_id=exercise_id).order_by(ExerciseAttempt.created_at.desc()).limit(3).all()
                    if attempts:
                        print("\n  Tentatives récentes:")
                        for attempt in attempts:
                            created_at = attempt.created_at
                            print(f"  - ID: {attempt.id}, User: {attempt.student_id}, Score: {attempt.score}%, Date: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                            
                            # Analyser le feedback si disponible
                            try:
                                feedback = json.loads(attempt.feedback)
                                if isinstance(feedback, dict) and 'correct_blanks' in feedback and 'total_blanks' in feedback:
                                    print(f"    Détails: {feedback['correct_blanks']}/{feedback['total_blanks']} blancs corrects")
                            except:
                                pass
                    else:
                        print("\n  Aucune tentative récente trouvée.")
                    
                    # Simulation de scoring
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
                    
                    # Recommandations
                    print("\n  Recommandations:")
                    if not has_answers:
                        print("  - AJOUTER le champ 'answers' basé sur les mots disponibles")
                    if has_text and has_sentences:
                        print("  - ATTENTION: Les deux champs 'text' et 'sentences' sont présents, risque de double comptage")
                    if total_blanks_in_content == 0:
                        print("  - ERREUR CRITIQUE: Aucun blanc trouvé dans le contenu!")
                    if len(correct_answers) == 0:
                        print("  - ERREUR CRITIQUE: Aucune réponse disponible!")
                    if total_blanks_in_content > 0 and len(correct_answers) > 0 and total_blanks_in_content != len(correct_answers):
                        print(f"  - INCOHÉRENCE: {total_blanks_in_content} blancs pour {len(correct_answers)} réponses")
                
                except json.JSONDecodeError:
                    print(f"Erreur: Contenu JSON invalide pour l'exercice #{exercise_id}")
                except Exception as e:
                    print(f"Erreur lors de l'analyse de l'exercice #{exercise_id}: {str(e)}")
                
                print("-" * 80)
        
        except Exception as e:
            print(f"Erreur lors de l'exécution du diagnostic: {str(e)}")
        
        print("\nDiagnostic terminé.")

def fix_fill_in_blanks_structure():
    """
    Corrige la structure des exercices 'fill_in_blanks' en ajoutant le champ 'answers'
    basé sur les mots disponibles et le nombre de blancs.
    """
    print("=" * 80)
    print("CORRECTION DE LA STRUCTURE DES EXERCICES TEXTE À TROUS")
    print("=" * 80)
    
    # Créer une sauvegarde de la base de données
    backup_path = f"instance/site.db.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        import shutil
        if os.path.exists('instance/site.db'):
            shutil.copy2('instance/site.db', backup_path)
            print(f"Sauvegarde de la base de données créée: {backup_path}")
        else:
            print("Avertissement: Fichier de base de données non trouvé pour la sauvegarde")
    except Exception as e:
        print(f"Erreur lors de la création de la sauvegarde: {str(e)}")
        return
    
    # Utiliser le contexte de l'application Flask
    with app.app_context():
        try:
            # Récupérer tous les exercices de type 'fill_in_blanks'
            exercises = Exercise.query.filter_by(exercise_type='fill_in_blanks').all()
            
            print(f"\nNombre d'exercices 'fill_in_blanks' trouvés: {len(exercises)}")
            
            if not exercises:
                print("Aucun exercice 'fill_in_blanks' trouvé dans la base de données.")
                return
            
            fixed_count = 0
            
            # Analyser et corriger chaque exercice
            for exercise in exercises:
                exercise_id = exercise.id
                title = exercise.title
                
                try:
                    content = exercise.get_content()
                    
                    print(f"\nExercice #{exercise_id}: {title}")
                    
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
                    elif has_text:
                        text_blanks = content['text'].count('___')
                        total_blanks_in_content = text_blanks
                    
                    # Récupérer les mots disponibles
                    available_words = []
                    if has_words:
                        available_words = content['words']
                    elif has_available_words:
                        available_words = content['available_words']
                    
                    # Vérifier si une correction est nécessaire
                    needs_correction = False
                    
                    # Cas 1: Pas de champ 'answers'
                    if not has_answers:
                        print(f"- Ajout du champ 'answers' manquant")
                        needs_correction = True
                        
                        # Utiliser les mots disponibles comme réponses
                        if available_words:
                            # Ajuster le nombre de réponses au nombre de blancs
                            if total_blanks_in_content > 0:
                                # Si plus de mots que de blancs, prendre les premiers mots
                                if len(available_words) >= total_blanks_in_content:
                                    answers = available_words[:total_blanks_in_content]
                                # Si moins de mots que de blancs, répéter les mots
                                else:
                                    answers = []
                                    for i in range(total_blanks_in_content):
                                        answers.append(available_words[i % len(available_words)])
                                
                                content['answers'] = answers
                                print(f"  - Ajouté {len(answers)} réponses: {answers}")
                            else:
                                print("  - ERREUR: Aucun blanc trouvé dans le contenu!")
                        else:
                            print("  - ERREUR: Aucun mot disponible trouvé!")
                    
                    # Cas 2: Incohérence entre 'answers' et nombre de blancs
                    elif has_answers and total_blanks_in_content > 0 and len(content['answers']) != total_blanks_in_content:
                        print(f"- Correction de l'incohérence: {len(content['answers'])} réponses pour {total_blanks_in_content} blancs")
                        needs_correction = True
                        
                        current_answers = content['answers']
                        
                        # Ajuster le nombre de réponses au nombre de blancs
                        if total_blanks_in_content > len(current_answers):
                            # Ajouter des réponses supplémentaires
                            additional_needed = total_blanks_in_content - len(current_answers)
                            for i in range(additional_needed):
                                if available_words:
                                    current_answers.append(available_words[i % len(available_words)])
                                else:
                                    current_answers.append("réponse" + str(len(current_answers) + 1))
                        else:
                            # Tronquer les réponses excédentaires
                            current_answers = current_answers[:total_blanks_in_content]
                        
                        content['answers'] = current_answers
                        print(f"  - Ajusté à {len(current_answers)} réponses: {current_answers}")
                    
                    # Appliquer les corrections si nécessaire
                    if needs_correction:
                        # Mettre à jour l'exercice dans la base de données
                        exercise.content = json.dumps(content, ensure_ascii=False)
                        db.session.commit()
                        fixed_count += 1
                        print("  - Exercice mis à jour avec succès")
                    else:
                        print("  - Aucune correction nécessaire")
                
                except json.JSONDecodeError:
                    print(f"Erreur: Contenu JSON invalide pour l'exercice #{exercise_id}")
                except Exception as e:
                    print(f"Erreur lors de la correction de l'exercice #{exercise_id}: {str(e)}")
            
            print(f"\n{fixed_count} exercices corrigés sur {len(exercises)} au total.")
            
        except Exception as e:
            print(f"Erreur lors de l'exécution de la correction: {str(e)}")
            db.session.rollback()
        
        print("\nCorrection terminée.")

if __name__ == "__main__":
    print("Diagnostic des exercices 'fill_in_blanks'")
    diagnose_fill_in_blanks()
    
    print("\nVoulez-vous appliquer les corrections? (o/n): ", end="")
    try:
        choice = input()
        if choice.lower() == "o":
            fix_fill_in_blanks_structure()
    except:
        # En cas d'erreur d'entrée (comme dans un environnement non interactif)
        print("\nPour appliquer les corrections, exécutez ce script avec l'argument 'fix':")
        print("python test_fill_in_blanks_diagnostic.py fix")
        
        # Vérifier si l'argument 'fix' est passé
        import sys
        if len(sys.argv) > 1 and sys.argv[1] == 'fix':
            print("\nApplication des corrections...")
            fix_fill_in_blanks_structure()
