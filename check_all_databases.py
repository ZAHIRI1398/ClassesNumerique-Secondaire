import sqlite3
import os

# Tester toutes les bases de données disponibles
db_files = ['classe_numerique.db', 'instance/classe_numerique.db', 'instance/app.db']

for db_file in db_files:
    if os.path.exists(db_file):
        print(f'\n=== {db_file} ===')
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Lister les tables
            cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
            tables = cursor.fetchall()
            print(f'Tables: {[t[0] for t in tables]}')
            
            # Si table exercise existe
            if any('exercise' in str(t) for t in tables):
                cursor.execute('SELECT COUNT(*) FROM exercise')
                count = cursor.fetchone()[0]
                print(f'Nombre d\'exercices: {count}')
                
                # Chercher exercices QCM
                cursor.execute('SELECT id, title FROM exercise WHERE title LIKE "%QCM%" OR title LIKE "%Test%" ORDER BY id DESC LIMIT 3')
                exercises = cursor.fetchall()
                for ex_id, ex_title in exercises:
                    print(f'  ID={ex_id}: {ex_title}')
            
            conn.close()
        except Exception as e:
            print(f'Erreur: {e}')
    else:
        print(f'{db_file} n\'existe pas')
