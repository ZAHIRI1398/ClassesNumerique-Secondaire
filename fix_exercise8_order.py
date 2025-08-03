from app import app, db
from models import Exercise
import json

with app.app_context():
    # Récupérer l'exercice 8
    exercise = Exercise.query.get(8)
    if not exercise:
        print("Exercice 8 non trouvé")
        exit()
    
    print(f"=== CORRECTION EXERCICE {exercise.id} ===")
    print(f"Titre: {exercise.title}")
    
    # Récupérer le contenu actuel
    content = exercise.get_content()
    print(f"Éléments: {content.get('draggable_items', [])}")
    print(f"Ordre correct actuel: {content.get('correct_order', [])}")
    
    # Les éléments sont: ['Zèbre', 'Abeille', 'Chat', 'Éléphant']
    # Pour l'ordre alphabétique: Abeille(1), Chat(2), Éléphant(3), Zèbre(0)
    # Donc l'ordre correct devrait être [1, 2, 3, 0]
    
    draggable_items = content.get('draggable_items', [])
    if draggable_items == ['Zèbre', 'Abeille', 'Chat', 'Éléphant']:
        # Corriger l'ordre correct
        content['correct_order'] = [1, 2, 3, 0]  # Abeille, Chat, Éléphant, Zèbre
        
        # Sauvegarder dans la base de données
        exercise.content = json.dumps(content, ensure_ascii=False)
        db.session.commit()
        
        print(f"CORRECTION APPLIQUEE")
        print(f"Nouvel ordre correct: {content['correct_order']}")
        
        # Vérification
        print(f"\n=== VERIFICATION ===")
        for i, correct_idx in enumerate(content['correct_order']):
            item = draggable_items[correct_idx]
            print(f"Zone {i+1} -> Element {correct_idx}: '{item}'")
        
        print(f"\nL'exercice 8 a ete corrige avec succes !")
        print(f"Maintenant, l'ordre alphabetique attendu est:")
        print(f"1. Abeille")
        print(f"2. Chat") 
        print(f"3. Elephant")
        print(f"4. Zebre")
        
    else:
        print(f"Les elements ne correspondent pas a ce qui etait attendu")
        print(f"Éléments trouvés: {draggable_items}")
