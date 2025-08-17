import sqlite3
import json

# Connexion à la base de données
conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()

# Récupérer l'exercice 21
cursor.execute('SELECT id, title, content FROM exercise WHERE id = 21')
result = cursor.fetchone()

if result:
    exercise_id, title, content_str = result
    content = json.loads(content_str)
    
    print(f'Exercice {exercise_id}: {title}')
    print(f'Structure actuelle: {list(content.keys())}')
    print(f'Nombre de zones: {len(content.get("zones", []))}')
    print(f'Nombre d\'éléments: {len(content.get("elements", []))}')
    
    # Générer les éléments à partir des zones si manquants
    if 'elements' not in content or not content['elements']:
        elements = []
        for zone in content.get('zones', []):
            elements.append({
                'id': zone['id'],
                'text': zone['legend'],
                'type': 'text'
            })
        
        content['elements'] = elements
        content['mode'] = 'classic'  # S'assurer que le mode est défini
        
        # Sauvegarder les modifications
        new_content_str = json.dumps(content, ensure_ascii=False)
        cursor.execute('UPDATE exercise SET content = ? WHERE id = ?', (new_content_str, exercise_id))
        conn.commit()
        
        print('Exercice corrige!')
        print(f'Nouveaux elements generes: {len(elements)}')
        for element in elements:
            print(f'  - Element {element["id"]}: "{element["text"]}"')
    else:
        print('L\'exercice a deja des elements')

else:
    print('Exercice 21 non trouve')

conn.close()
