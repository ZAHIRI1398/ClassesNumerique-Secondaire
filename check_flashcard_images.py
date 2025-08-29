import sqlite3
import json

conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()
cursor.execute("SELECT id, title, content FROM exercise WHERE exercise_type = 'flashcards'")
results = cursor.fetchall()

print("Détails des exercices flashcards :")
for row in results:
    exercise_id = row[0]
    title = row[1]
    content_str = row[2]
    
    print(f"\nID: {exercise_id}, Titre: {title}")
    
    try:
        content = json.loads(content_str)
        cards = content.get('cards', [])
        print(f"Nombre de cartes: {len(cards)}")
        
        for i, card in enumerate(cards):
            question = card.get('question', '')
            answer = card.get('answer', '')
            image = card.get('image', 'Pas d\'image')
            
            print(f"  Carte {i+1}:")
            print(f"    Question: {question}")
            print(f"    Réponse: {answer}")
            print(f"    Image: {image}")
    except json.JSONDecodeError:
        print(f"  Erreur: Contenu JSON invalide")
    except Exception as e:
        print(f"  Erreur: {str(e)}")

conn.close()
