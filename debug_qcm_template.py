from flask import Flask, render_template
import sqlite3
import json

app = Flask(__name__)

# Simuler les données de l'exercice
conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()

cursor.execute('SELECT id, title, content FROM exercise WHERE id = 4')
exercise_data = cursor.fetchone()

if exercise_data:
    exercise_id, title, content_str = exercise_data
    content = json.loads(content_str)
    
    print(f"=== DEBUG QCM TEMPLATE ===")
    print(f"Exercise ID: {exercise_id}")
    print(f"Title: {title}")
    print(f"Content: {json.dumps(content, indent=2)}")
    
    # Vérifier la condition du template
    print(f"\n=== TEMPLATE CONDITIONS ===")
    print(f"content exists: {content is not None}")
    print(f"content.image exists: {'image' in content}")
    print(f"content.image value: {content.get('image', 'NOT FOUND')}")
    
    # Vérifier si la condition {% if content and content.image %} est vraie
    template_condition = content and 'image' in content and content['image']
    print(f"Template condition (content and content.image): {template_condition}")
    
    if template_condition:
        print(f"\nL'image DEVRAIT s'afficher")
        print(f"URL generee: {content['image']}?v=123456")
    else:
        print(f"\nL'image ne s'affichera PAS")
        print("Raison: condition template non remplie")

conn.close()
