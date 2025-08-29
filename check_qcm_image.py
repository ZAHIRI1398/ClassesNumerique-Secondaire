import sqlite3
import json
import os

# Tester différentes bases de données
db_files = ['classe_numerique.db', 'app.db', 'instance/app.db', 'instance/classe_numerique.db']

for db_file in db_files:
    if os.path.exists(db_file):
        print(f'\n=== Testing {db_file} ===')
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Lister les tables
            cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
            tables = cursor.fetchall()
            print(f'Tables: {[t[0] for t in tables]}')
            
            # Si table exercise existe (sans 's')
            if any('exercise' in str(t) for t in tables):
                cursor.execute('SELECT id, title, content FROM exercise WHERE title LIKE "%Test image QCM%" OR title LIKE "%Test%" ORDER BY id DESC LIMIT 3')
                exercises = cursor.fetchall()
                print(f'Exercices trouvés: {len(exercises)}')
                
                for ex_id, ex_title, content_str in exercises:
                    print(f'  ID={ex_id}: {ex_title}')
                    if 'Test image QCM' in ex_title:
                        try:
                            content = json.loads(content_str)
                            if 'image' in content:
                                print(f'    Image: {content["image"]}')
                            else:
                                print('    Pas d\'image dans le contenu')
                        except:
                            print('    Erreur parsing JSON')
            
            conn.close()
        except Exception as e:
            print(f'Erreur: {e}')
    else:
        print(f'{db_file} n\'existe pas')
