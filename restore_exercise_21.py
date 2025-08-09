import sqlite3
import json

# Connexion à la base de données
conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()

# Contenu correct pour l'exercice 21
correct_content = {
    'mode': 'classic',
    'instructions': 'Placer les nombres sur la droite',
    'main_image': 'static/uploads/1754559327_clopepe.png',
    'zones': [
        {'x': 301, 'y': 189, 'legend': '1.6', 'id': 1},
        {'x': 452, 'y': 191, 'legend': '3.8', 'id': 2},
        {'x': 548, 'y': 189, 'legend': '5.2', 'id': 3}
    ],
    'elements': [
        {'id': 1, 'text': '1.6', 'type': 'text'},
        {'id': 2, 'text': '3.8', 'type': 'text'},
        {'id': 3, 'text': '5.2', 'type': 'text'}
    ]
}

# Mettre à jour l'exercice 21
content_str = json.dumps(correct_content, ensure_ascii=False)
cursor.execute('UPDATE exercise SET content = ? WHERE id = 21', (content_str,))
conn.commit()

print('Exercice 21 restauré avec 3 zones:')
print('- Zone 1: 1.6 (Position: 301, 189)')
print('- Zone 2: 3.8 (Position: 452, 191)')  
print('- Zone 3: 5.2 (Position: 548, 189)')
print('- 3 éléments générés automatiquement')

conn.close()
