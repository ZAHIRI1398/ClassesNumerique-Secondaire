import json
from flask import Flask
from app import app, db, Exercise

def debug_submit_route():
    """
    Examine la route de soumission des réponses dans app.py
    pour identifier d'éventuels problèmes dans le traitement des réponses.
    """
    # Chercher la route de soumission dans app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        app_code = f.read()
    
    # Chercher la route de soumission des réponses
    submit_route_start = app_code.find('@app.route(\'/exercise/submit/<int:exercise_id>\'')
    if submit_route_start == -1:
        print("Route de soumission non trouvée dans app.py")
        return
    
    # Extraire le code de la route de soumission
    submit_route_end = app_code.find('@app.route', submit_route_start + 1)
    if submit_route_end == -1:
        submit_route_end = len(app_code)
    
    submit_route_code = app_code[submit_route_start:submit_route_end]
    
    # Afficher le code de la route de soumission
    print("Code de la route de soumission des réponses:")
    print("=" * 80)
    print(submit_route_code)
    print("=" * 80)
    
    # Chercher le traitement spécifique pour fill_in_blanks
    fill_in_blanks_start = submit_route_code.find('elif exercise.exercise_type == \'fill_in_blanks\'')
    if fill_in_blanks_start == -1:
        print("Traitement pour fill_in_blanks non trouvé dans la route de soumission")
        return
    
    # Extraire le code de traitement pour fill_in_blanks
    fill_in_blanks_end = submit_route_code.find('elif', fill_in_blanks_start + 1)
    if fill_in_blanks_end == -1:
        fill_in_blanks_end = submit_route_code.find('else', fill_in_blanks_start + 1)
        if fill_in_blanks_end == -1:
            fill_in_blanks_end = len(submit_route_code)
    
    fill_in_blanks_code = submit_route_code[fill_in_blanks_start:fill_in_blanks_end]
    
    # Afficher le code de traitement pour fill_in_blanks
    print("\nCode de traitement pour fill_in_blanks:")
    print("=" * 80)
    print(fill_in_blanks_code)
    print("=" * 80)
    
    # Chercher le code de récupération des réponses utilisateur
    user_answers_code = fill_in_blanks_code.find('user_answer = request.form.get')
    if user_answers_code != -1:
        # Extraire quelques lignes autour
        user_answers_start = fill_in_blanks_code.rfind('\n', 0, user_answers_code)
        user_answers_end = fill_in_blanks_code.find('\n\n', user_answers_code)
        if user_answers_end == -1:
            user_answers_end = len(fill_in_blanks_code)
        
        user_answers_code = fill_in_blanks_code[user_answers_start:user_answers_end]
        
        print("\nCode de récupération des réponses utilisateur:")
        print("=" * 80)
        print(user_answers_code)
        print("=" * 80)
    
    # Vérifier si le code utilise request.form.getlist pour les réponses multiples
    if 'request.form.getlist' in fill_in_blanks_code:
        print("\nATTENTION: Le code utilise request.form.getlist pour récupérer les réponses.")
        print("Cela pourrait causer des problèmes si les réponses sont récupérées individuellement.")
    
    # Vérifier si le code utilise request.form.get pour chaque réponse
    if 'request.form.get(f\'answer_{i}\'' in fill_in_blanks_code:
        print("\nLe code récupère chaque réponse individuellement avec request.form.get(f'answer_{i}').")
        print("C'est la méthode correcte pour récupérer les réponses de chaque blanc.")
    
    # Vérifier comment le score est calculé
    score_calc_start = fill_in_blanks_code.find('score = ')
    if score_calc_start != -1:
        score_calc_end = fill_in_blanks_code.find('\n', score_calc_start)
        if score_calc_end == -1:
            score_calc_end = len(fill_in_blanks_code)
        
        score_calc_code = fill_in_blanks_code[score_calc_start:score_calc_end]
        
        print("\nCode de calcul du score:")
        print("=" * 80)
        print(score_calc_code)
        print("=" * 80)

if __name__ == "__main__":
    debug_submit_route()
