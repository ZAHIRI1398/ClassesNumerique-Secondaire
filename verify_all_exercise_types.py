from flask import Flask
from models import db, Exercise
import json
import os
import sys
from utils.image_path_handler import normalize_image_path

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def check_image_path(path):
    """Vérifie si le chemin d'image est correctement formaté et si l'image existe"""
    if not path:
        return False, "Chemin d'image manquant"
    
    # Vérifier le format du chemin
    normalized_path = normalize_image_path(path)
    if normalized_path != path:
        return False, f"Format incorrect: '{path}' devrait être '{normalized_path}'"
    
    # Vérifier si le fichier existe
    file_path = os.path.join(app.root_path, path.lstrip('/'))
    if not os.path.exists(file_path):
        return False, f"Fichier non trouvé: {file_path}"
    
    return True, "OK"

def verify_exercise(exercise):
    """Vérifie un exercice et retourne les problèmes détectés"""
    problems = []
    
    # Vérifier le chemin d'image de l'exercice
    image_ok, image_msg = check_image_path(exercise.image_path)
    if not image_ok:
        problems.append(f"Problème avec exercise.image_path: {image_msg}")
    
    # Charger le contenu JSON
    try:
        content = json.loads(exercise.content)
    except json.JSONDecodeError:
        problems.append("Contenu JSON invalide")
        return problems
    
    # Vérifier le chemin d'image dans le contenu
    if 'image' in content:
        content_image_ok, content_image_msg = check_image_path(content['image'])
        if not content_image_ok:
            problems.append(f"Problème avec content.image: {content_image_msg}")
        
        # Vérifier la cohérence entre les deux chemins
        if exercise.image_path != content['image']:
            problems.append(f"Incohérence: exercise.image_path='{exercise.image_path}' != content.image='{content['image']}'")
    
    # Vérifications spécifiques selon le type d'exercice
    if exercise.exercise_type == 'qcm':
        if 'questions' not in content:
            problems.append("QCM: 'questions' manquant dans le contenu")
        elif not isinstance(content['questions'], list):
            problems.append("QCM: 'questions' n'est pas une liste")
        else:
            for i, q in enumerate(content['questions']):
                if not isinstance(q, dict):
                    problems.append(f"QCM: question {i} n'est pas un dictionnaire")
                elif 'text' not in q:
                    problems.append(f"QCM: question {i} n'a pas de 'text'")
                elif 'choices' not in q:
                    problems.append(f"QCM: question {i} n'a pas de 'choices'")
                elif 'correct_answer' not in q:
                    problems.append(f"QCM: question {i} n'a pas de 'correct_answer'")
    
    elif exercise.exercise_type == 'qcm_multichoix':
        if 'questions' not in content:
            problems.append("QCM Multichoix: 'questions' manquant dans le contenu")
        elif not isinstance(content['questions'], list):
            problems.append("QCM Multichoix: 'questions' n'est pas une liste")
        else:
            for i, q in enumerate(content['questions']):
                if not isinstance(q, dict):
                    problems.append(f"QCM Multichoix: question {i} n'est pas un dictionnaire")
                elif 'text' not in q:
                    problems.append(f"QCM Multichoix: question {i} n'a pas de 'text'")
                elif 'choices' not in q:
                    problems.append(f"QCM Multichoix: question {i} n'a pas de 'choices'")
                elif 'correct_answers' not in q:
                    problems.append(f"QCM Multichoix: question {i} n'a pas de 'correct_answers'")
                elif not isinstance(q['correct_answers'], list):
                    problems.append(f"QCM Multichoix: 'correct_answers' de la question {i} n'est pas une liste")
    
    elif exercise.exercise_type == 'fill_in_blanks':
        if 'sentences' not in content:
            problems.append("Texte à trous: 'sentences' manquant dans le contenu")
    
    elif exercise.exercise_type == 'pairs':
        if 'left_items' not in content and 'pairs' not in content:
            problems.append("Association de paires: ni 'left_items' ni 'pairs' trouvés dans le contenu")
        if 'left_items' in content and 'right_items' not in content:
            problems.append("Association de paires: 'right_items' manquant dans le contenu")
        if 'left_items' in content and 'correct_pairs' not in content:
            problems.append("Association de paires: 'correct_pairs' manquant dans le contenu")
    
    elif exercise.exercise_type == 'word_placement':
        if 'sentences' not in content:
            problems.append("Mots à placer: 'sentences' manquant dans le contenu")
        if 'words' not in content:
            problems.append("Mots à placer: 'words' manquant dans le contenu")
        if 'answers' not in content:
            problems.append("Mots à placer: 'answers' manquant dans le contenu")
    
    elif exercise.exercise_type == 'underline_words':
        if 'sentences' not in content:
            problems.append("Souligner les mots: 'sentences' manquant dans le contenu")
        elif not isinstance(content['sentences'], list):
            problems.append("Souligner les mots: 'sentences' n'est pas une liste")
        else:
            for i, s in enumerate(content['sentences']):
                if not isinstance(s, dict):
                    problems.append(f"Souligner les mots: phrase {i} n'est pas un dictionnaire")
                elif 'text' not in s:
                    problems.append(f"Souligner les mots: phrase {i} n'a pas de 'text'")
                elif 'words_to_underline' not in s:
                    problems.append(f"Souligner les mots: phrase {i} n'a pas de 'words_to_underline'")
    
    elif exercise.exercise_type == 'drag_and_drop':
        if 'draggable_items' not in content:
            problems.append("Glisser-déposer: 'draggable_items' manquant dans le contenu")
        if 'drop_zones' not in content:
            problems.append("Glisser-déposer: 'drop_zones' manquant dans le contenu")
        if 'correct_order' not in content:
            problems.append("Glisser-déposer: 'correct_order' manquant dans le contenu")
    
    elif exercise.exercise_type == 'flashcards':
        if 'cards' not in content:
            problems.append("Cartes mémoire: 'cards' manquant dans le contenu")
        elif not isinstance(content['cards'], list):
            problems.append("Cartes mémoire: 'cards' n'est pas une liste")
        else:
            for i, card in enumerate(content['cards']):
                if not isinstance(card, dict):
                    problems.append(f"Cartes mémoire: carte {i} n'est pas un dictionnaire")
                elif 'front' not in card:
                    problems.append(f"Cartes mémoire: carte {i} n'a pas de 'front'")
                elif 'back' not in card:
                    problems.append(f"Cartes mémoire: carte {i} n'a pas de 'back'")
    
    return problems

with app.app_context():
    # Récupérer tous les exercices
    exercises = Exercise.query.all()
    
    if not exercises:
        print("Aucun exercice trouvé dans la base de données.")
        sys.exit(1)
    
    print(f"Vérification de {len(exercises)} exercices...")
    print("-" * 50)
    
    all_ok = True
    exercise_types_found = set()
    
    for exercise in exercises:
        exercise_types_found.add(exercise.exercise_type)
        problems = verify_exercise(exercise)
        
        if problems:
            all_ok = False
            print(f"Exercice #{exercise.id}: {exercise.title} ({exercise.exercise_type})")
            for problem in problems:
                print(f"  - {problem}")
            print("-" * 50)
        else:
            print(f"OK - Exercice #{exercise.id}: {exercise.title} ({exercise.exercise_type})")
    
    print("\nTypes d'exercices trouvés:")
    for ex_type in sorted(exercise_types_found):
        print(f"- {ex_type}")
    
    print("\nTypes d'exercices manquants:")
    all_types = [t[0] for t in Exercise.EXERCISE_TYPES]
    for ex_type in sorted(set(all_types) - exercise_types_found):
        print(f"- {ex_type}")
    
    if all_ok:
        print("\nTous les exercices sont correctement configurés!")
    else:
        print("\nDes problèmes ont été détectés dans certains exercices.")
