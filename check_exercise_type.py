import sqlite3
import json

def check_exercise():
    try:
        # Connexion à la base de données
        conn = sqlite3.connect('instance/app.db')
        cursor = conn.cursor()
        
        # Recherche des exercices avec "Test mots" dans le titre
        cursor.execute("SELECT id, title, exercise_type, content FROM exercise WHERE title LIKE '%Test mots%'")
        exercises = cursor.fetchall()
        
        print(f"Nombre d'exercices trouvés: {len(exercises)}")
        
        for exercise in exercises:
            exercise_id, title, exercise_type, content_json = exercise
            print(f"\nID: {exercise_id}")
            print(f"Titre: {title}")
            print(f"Type: {exercise_type}")
            
            try:
                content = json.loads(content_json)
                print(f"Structure du contenu: {list(content.keys())}")
                
                # Vérifier si c'est un exercice word_placement
                if exercise_type == 'word_placement':
                    print("Détails word_placement:")
                    print(f"Phrases: {content.get('sentences', [])}")
                    print(f"Mots: {content.get('words', [])}")
                    print(f"Réponses: {content.get('answers', [])}")
                
                # Vérifier si c'est un exercice legend
                elif exercise_type == 'legend':
                    print("Détails legend:")
                    print(f"Mode: {content.get('mode', 'non spécifié')}")
                    print(f"Instructions: {content.get('instructions', 'non spécifiées')}")
                    print(f"Éléments: {len(content.get('elements', []))} éléments")
            except json.JSONDecodeError:
                print(f"Contenu JSON invalide: {content_json[:100]}...")
            except Exception as e:
                print(f"Erreur lors de l'analyse du contenu: {str(e)}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erreur: {str(e)}")

if __name__ == "__main__":
    check_exercise()
