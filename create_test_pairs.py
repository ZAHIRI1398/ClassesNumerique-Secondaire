from app import app, db
from models import Exercise, User
import json

with app.app_context():
    # Récupérer l'enseignant
    teacher = User.query.filter_by(role='teacher').first()
    
    if not teacher:
        print("Aucun enseignant trouvé dans la base de données")
        exit()
    
    # Créer un exercice de test avec la nouvelle structure "pairs"
    test_exercise = Exercise(
        title="Test Exercice Pairs - Drapeaux et Pays",
        description="Associez chaque drapeau à son pays correspondant",
        exercise_type="pairs",
        content=json.dumps({
            "subject": "Géographie",
            "pairs": [
                {
                    "id": "1",
                    "left": {
                        "content": "/static/uploads/france_flag.png",
                        "type": "image"
                    },
                    "right": {
                        "content": "France",
                        "type": "text"
                    }
                },
                {
                    "id": "2", 
                    "left": {
                        "content": "/static/uploads/germany_flag.png",
                        "type": "image"
                    },
                    "right": {
                        "content": "Allemagne",
                        "type": "text"
                    }
                },
                {
                    "id": "3",
                    "left": {
                        "content": "/static/uploads/italy_flag.png", 
                        "type": "image"
                    },
                    "right": {
                        "content": "Italie",
                        "type": "text"
                    }
                }
            ]
        }),
        teacher_id=teacher.id
    )
    
    db.session.add(test_exercise)
    db.session.commit()
    
    print(f"Exercice de test créé avec succès ! ID: {test_exercise.id}")
    print(f"Titre: {test_exercise.title}")
    print(f"Type: {test_exercise.exercise_type}")
    print(f"URL de test: http://127.0.0.1:5000/exercise/{test_exercise.id}")
    
    # Vérifier le contenu
    content = test_exercise.get_content()
    print(f"Contenu parsé: {content}")
