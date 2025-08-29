import sqlite3
import json

# Vérifier le contenu actuel de l'exercice
conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()

cursor.execute('SELECT id, title, content FROM exercise WHERE id = 4')
exercise = cursor.fetchone()

if exercise:
    exercise_id, title, content_str = exercise
    print(f'Exercice ID={exercise_id}: {title}')
    
    content = json.loads(content_str)
    print(f'Contenu JSON complet:')
    print(json.dumps(content, indent=2))
    
    if 'image' in content:
        print(f'\nImage dans le contenu: {content["image"]}')
    else:
        print('\nAUCUNE IMAGE dans le contenu!')

conn.close()
