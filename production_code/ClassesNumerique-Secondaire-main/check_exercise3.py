import sqlite3
import json

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# Vérifier l'exercice 3
cursor.execute('SELECT id, title, exercise_type, content FROM exercise WHERE id = 3')
result = cursor.fetchone()

if result:
    print('Exercise 3 data:')
    print(f'ID: {result[0]}')
    print(f'Title: {result[1]}')
    print(f'Type: {result[2]}')
    print(f'Content: {result[3]}')
    
    try:
        content = json.loads(result[3])
        print(f'Content keys: {list(content.keys())}')
        print(f'Left items: {content.get("left_items", [])}')
        print(f'Right items: {content.get("right_items", [])}')
    except Exception as e:
        print(f'Error parsing JSON: {e}')
else:
    print('Exercise 3 not found')

# Vérifier tous les exercices
cursor.execute('SELECT id, title, exercise_type FROM exercise')
all_exercises = cursor.fetchall()
print(f'\nAll exercises in database:')
for ex in all_exercises:
    print(f'- ID {ex[0]}: {ex[1]} ({ex[2]})')

conn.close()
