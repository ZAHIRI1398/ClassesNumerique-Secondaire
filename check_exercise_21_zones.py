import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()

cursor.execute('SELECT id, title, content FROM exercise WHERE id = 21')
result = cursor.fetchone()

if result:
    exercise_id, title, content_str = result
    content = json.loads(content_str)
    
    print(f'Exercice {exercise_id}: {title}')
    print(f'Nombre de zones: {len(content.get("zones", []))}')
    print(f'Nombre d\'elements: {len(content.get("elements", []))}')
    
    print('\nZones:')
    for i, zone in enumerate(content.get('zones', [])):
        print(f'  Zone {i+1}: {zone}')
        
    print('\nElements:')
    for i, element in enumerate(content.get('elements', [])):
        print(f'  Element {i+1}: {element}')
else:
    print('Exercice non trouve')

conn.close()
