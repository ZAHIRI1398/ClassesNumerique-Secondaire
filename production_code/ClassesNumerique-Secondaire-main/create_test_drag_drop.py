from app import app, db
from models import Exercise, User
import json

with app.app_context():
    # Récupérer l'enseignant
    teacher = User.query.filter_by(role='teacher').first()
    
    if not teacher:
        print("Aucun enseignant trouvé dans la base de données")
        exit()
    
    # Créer un exercice de test "drag_and_drop"
    test_exercise = Exercise(
        title="Test Exercice Glisser-Déposer - Ordre Alphabétique",
        description="Glissez les mots dans l'ordre alphabétique",
        exercise_type="drag_and_drop",
        content=json.dumps({
            "subject": "Français",
            "draggable_items": ["Zèbre", "Abeille", "Chat", "Éléphant"],
            "drop_zones": ["1er mot", "2ème mot", "3ème mot", "4ème mot"],
            "correct_order": [1, 0, 2, 3]  # Abeille, Chat, Éléphant, Zèbre
        }),
        teacher_id=teacher.id
    )
    
    db.session.add(test_exercise)
    db.session.commit()
    
    print(f"Exercice drag_and_drop créé avec succès ! ID: {test_exercise.id}")
    print(f"Titre: {test_exercise.title}")
    print(f"Type: {test_exercise.exercise_type}")
    print(f"URL de test: http://127.0.0.1:5000/exercise/{test_exercise.id}")
    
    # Vérifier le contenu
    content = test_exercise.get_content()
    print(f"Contenu parsé: {content}")
    print(f"Éléments à glisser: {content.get('draggable_items', [])}")
    print(f"Zones de dépôt: {content.get('drop_zones', [])}")
    print(f"Ordre correct: {content.get('correct_order', [])}")
