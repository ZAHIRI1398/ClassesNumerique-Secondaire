import sqlite3
import json
import os

# Connexion à la base de données
conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()

# Récupérer l'exercice 21
cursor.execute('SELECT id, title, content, image_path FROM exercise WHERE id = 21')
result = cursor.fetchone()

if result:
    exercise_id, title, content_str, image_path = result
    content = json.loads(content_str)
    
    print(f'Exercice {exercise_id}: {title}')
    print(f'Image path (champ image_path): {image_path}')
    print(f'Main image (dans content): {content.get("main_image")}')
    
    # Vérifier si les fichiers existent
    if image_path:
        full_path = f'static/uploads/{image_path}'
        exists = os.path.exists(full_path)
        print(f'Fichier {full_path} existe: {exists}')
    
    main_image = content.get('main_image')
    if main_image:
        exists = os.path.exists(main_image)
        print(f'Fichier {main_image} existe: {exists}')
    
    # Lister les fichiers dans static/uploads
    uploads_dir = 'static/uploads'
    if os.path.exists(uploads_dir):
        print(f'\nFichiers dans {uploads_dir}:')
        for file in os.listdir(uploads_dir):
            if 'clopepe' in file.lower() or 'droite' in file.lower():
                print(f'  - {file}')
    
else:
    print('Exercice 21 non trouve')

conn.close()
