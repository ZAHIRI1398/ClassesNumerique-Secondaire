import sqlite3
import json

# Connexion à la base de données active
conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()

# Récupérer l'exercice "Test image QCM"
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
        print('Contenu mis a jour avec succes!')
        
    except json.JSONDecodeError as e:
        print(f'Erreur de parsing JSON: {e}')
else:
    print('Exercice "Test image QCM" non trouvé')

conn.close()
