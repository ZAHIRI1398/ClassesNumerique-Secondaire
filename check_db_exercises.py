import sqlite3
import os

# Vérifier les exercices 10 et 11 dans les bases de données
for db_file in ['instance/app.db', 'instance/classe_numerique.db']:
    if os.path.exists(db_file):
        print(f'=== {db_file} ===')
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Lister les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print('Tables:', [t[0] for t in tables])
        
        # Chercher la table exercise
        if 'exercise' in [t[0] for t in tables]:
            cursor.execute('SELECT id, title, exercise_type, image_path FROM exercise WHERE id IN (10, 11)')
            results = cursor.fetchall()
            for row in results:
                print(f'Exercise {row[0]}: {row[1]} (type: {row[2]}, image: {row[3]})')
        
        conn.close()
        print()
