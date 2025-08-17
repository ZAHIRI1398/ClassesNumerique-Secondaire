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
    submit_route_start = app_code.find('@app.route(\'/exercise/<int:exercise_id>/submit/')
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
    print(submit_route_code[:500] + "..." if len(submit_route_code) > 500 else submit_route_code)
    print("=" * 80)
    
    # Chercher le traitement spécifique pour fill_in_blanks
    fill_in_blanks_start = submit_route_code.find('elif exercise.exercise_type == \'fill_in_blanks\'')
    if fill_in_blanks_start == -1:
        print("Traitement pour fill_in_blanks non trouvé dans la route de soumission")
        # Chercher une autre façon de traiter fill_in_blanks
        fill_in_blanks_start = submit_route_code.find('fill_in_blanks')
        if fill_in_blanks_start == -1:
            print("Aucune mention de fill_in_blanks dans la route de soumission")
            return
        else:
            print(f"Mention de fill_in_blanks trouvée à la position {fill_in_blanks_start}")
            # Extraire quelques lignes autour
            context_start = max(0, submit_route_code.rfind('\n', 0, fill_in_blanks_start - 100))
            context_end = min(len(submit_route_code), submit_route_code.find('\n\n\n', fill_in_blanks_start + 100))
            context = submit_route_code[context_start:context_end]
            print("\nContexte autour de fill_in_blanks:")
            print("=" * 80)
            print(context)
            print("=" * 80)
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

if __name__ == "__main__":
    debug_submit_route()
