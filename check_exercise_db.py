import sqlite3
import json

# Connexion à la base de données
conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()

# Récupérer l'exercice T56
cursor.execute('SELECT id, title, image_path, content FROM exercise WHERE title = ?', ('T56',))
exercise = cursor.fetchone()

if exercise:
    print(f'Exercice ID: {exercise[0]}')
    print(f'Titre: {exercise[1]}')
    print(f'Image path: {exercise[2]}')
    if exercise[3]:
        print(f'Content: {exercise[3][:200]}...')
    else:
        print('Content: None')
else:
    print('Exercice T56 non trouvé')

conn.close()
