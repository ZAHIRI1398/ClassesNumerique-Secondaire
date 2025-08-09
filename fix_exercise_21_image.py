import sqlite3
import json

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
    print(f'Image path actuel: {image_path}')
    print(f'Main image actuel: {content.get("main_image")}')
    
    # Corriger le chemin de l'image dans le content
    if image_path:
        correct_main_image = f'static/uploads/{image_path}'
        content['main_image'] = correct_main_image
        
        # Sauvegarder les modifications
        new_content_str = json.dumps(content, ensure_ascii=False)
        cursor.execute('UPDATE exercise SET content = ? WHERE id = ?', (new_content_str, exercise_id))
        conn.commit()
        
        print('Correction appliquee!')
        print(f'Nouveau main_image: {correct_main_image}')
    else:
        print('Aucun image_path trouve')

else:
    print('Exercice 21 non trouve')

conn.close()
