import sqlite3
import json
import os

def test_flashcard_data():
    """
    Vérifie le contenu des exercices de type flashcard dans la base de données
    pour identifier les problèmes potentiels avec les images
    """
    # Chemin de la base de données
    db_path = "instance/app.db"
    
    if not os.path.exists(db_path):
        print(f"Base de données non trouvée: {db_path}")
        return
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer la structure de la table exercise
        cursor.execute("PRAGMA table_info(exercise)")
        columns = cursor.fetchall()
        print("Structure de la table exercise:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Récupérer les exercices de type flashcard
        cursor.execute("""
            SELECT id, title, content, exercise_type 
            FROM exercise 
            WHERE exercise_type = 'flashcards'
        """)
        
        exercises = cursor.fetchall()
        print(f"Nombre d'exercices flashcard trouvés: {len(exercises)}")
        
        for exercise_id, title, content_json, exercise_type in exercises:
            print(f"\n--- Exercice ID: {exercise_id}, Titre: {title} ---")
            
            try:
                # Parser le contenu JSON
                content = json.loads(content_json)
                
                # Vérifier si le contenu a la structure attendue
                if 'cards' not in content:
                    print(f"  ERREUR: Structure JSON invalide - 'cards' manquant")
                    continue
                
                cards = content['cards']
                print(f"  Nombre de cartes: {len(cards)}")
                
                # Analyser chaque carte
                for i, card in enumerate(cards):
                    print(f"  Carte {i+1}:")
                    
                    # Vérifier la présence de question et réponse
                    if 'question' not in card:
                        print(f"    ERREUR: 'question' manquante")
                    else:
                        print(f"    Question: {card['question']}")
                    
                    if 'answer' not in card:
                        print(f"    ERREUR: 'answer' manquante")
                    else:
                        print(f"    Réponse: {card['answer']}")
                    
                    # Vérifier l'image
                    if 'image' not in card:
                        print(f"    ERREUR: Champ 'image' manquant")
                    elif card['image'] is None:
                        print(f"    Image: Aucune (None)")
                    elif card['image'] == "":
                        print(f"    Image: Chaîne vide")
                    else:
                        print(f"    Image: {card['image']}")
                        
                        # Vérifier si le fichier existe localement
                        if card['image'].startswith('static/'):
                            if os.path.exists(card['image']):
                                print(f"    ✓ Le fichier image existe localement")
                            else:
                                print(f"    ✗ Le fichier image n'existe PAS localement")
            
            except json.JSONDecodeError:
                print(f"  ERREUR: Contenu JSON invalide: {content_json[:100]}...")
            except Exception as e:
                print(f"  ERREUR: {str(e)}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erreur lors de l'accès à la base de données: {str(e)}")

if __name__ == "__main__":
    test_flashcard_data()
