import sqlite3
import json

# Utiliser la BONNE base de données selon la configuration Flask
conn = sqlite3.connect('classe_numerique.db')  # Pas instance/app.db !
cursor = conn.cursor()

print("=== CORRECTION BASE DE DONNEES CORRECTE ===")

# Vérifier si l'exercice "Test image QCM" existe
cursor.execute('SELECT id, title, content FROM exercise WHERE title = "Test image QCM"')
exercise = cursor.fetchone()

if exercise:
    exercise_id, title, content_str = exercise
    print(f'Exercice trouvé: ID={exercise_id}, Titre={title}')
    
    try:
        content = json.loads(content_str)
        print(f'Contenu actuel: {json.dumps(content, indent=2)}')
        
        # Ajouter une image de test au contenu
        content['image'] = '/static/uploads/qcm_test_image.png'
        
        # Sauvegarder le contenu modifié
        new_content_str = json.dumps(content)
        cursor.execute('UPDATE exercise SET content = ? WHERE id = ?', (new_content_str, exercise_id))
        conn.commit()
        
        print(f'Image ajoutee au contenu: {content["image"]}')
        print('Contenu mis a jour avec succes dans classe_numerique.db!')
        
    except json.JSONDecodeError as e:
        print(f'Erreur de parsing JSON: {e}')
else:
    print('Exercice "Test image QCM" non trouvé dans classe_numerique.db')
    
    # Créer un nouvel exercice QCM avec image
    print('Creation d\'un nouvel exercice QCM avec image...')
    
    content = {
        "questions": [
            {
                "question": "l appareil digestif est :",
                "options": ["1", "2", "3", "4"],
                "correct": 0
            }
        ],
        "image": "/static/uploads/qcm_test_image.png"
    }
    
    cursor.execute('''
        INSERT INTO exercise (title, description, exercise_type, content, created_by)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        'Test image QCM',
        'TEST',
        'qcm',
        json.dumps(content),
        1  # ID utilisateur par défaut
    ))
    
    conn.commit()
    print('Nouvel exercice QCM créé avec image!')

conn.close()
