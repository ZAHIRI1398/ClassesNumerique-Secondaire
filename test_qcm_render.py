import os
import sys
import sqlite3
import json
from flask import Flask, render_template

# Ajouter le répertoire courant au path
sys.path.insert(0, os.getcwd())

# Créer une application Flask minimale
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'

# Simuler les données de l'exercice QCM
class MockExercise:
    def __init__(self):
        self.id = 4
        self.title = "Test image QCM"
        self.exercise_type = "qcm"
        self.description = "TEST"
        
    def get_content(self):
        # Récupérer le contenu réel de la base
        conn = sqlite3.connect('instance/app.db')
        cursor = conn.cursor()
        cursor.execute('SELECT content FROM exercise WHERE id = 4')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return {}

with app.app_context():
    try:
        # Créer l'exercice mock
        exercise = MockExercise()
        content = exercise.get_content()
        
        print("=== TEST RENDU TEMPLATE QCM ===")
        print(f"Exercise ID: {exercise.id}")
        print(f"Title: {exercise.title}")
        print(f"Content: {json.dumps(content, indent=2)}")
        
        # Vérifier que le template existe
        template_path = os.path.join(app.template_folder, 'exercise_types/qcm.html')
        print(f"\nTemplate path: {template_path}")
        print(f"Template exists: {os.path.exists(template_path)}")
        
        # Tenter de rendre le template
        print("\n=== TENTATIVE DE RENDU ===")
        rendered = render_template('exercise_types/qcm.html',
                                 exercise=exercise,
                                 content=content,
                                 attempt=None,
                                 progress=None,
                                 course=None,
                                 user_answers={},
                                 show_answers=False)
        
        # Vérifier si l'image est dans le HTML rendu
        if '/static/uploads/qcm_test_image.png' in rendered:
            print("✅ IMAGE TROUVEE dans le HTML rendu!")
        else:
            print("❌ Image NOT FOUND dans le HTML rendu")
            
        # Chercher la section image dans le HTML
        if 'class="image-display-card"' in rendered:
            print("✅ Section image-display-card trouvée")
        else:
            print("❌ Section image-display-card NOT FOUND")
            
        print(f"\nTaille du HTML rendu: {len(rendered)} caractères")
        
        # Extraire la partie image du HTML
        start_img = rendered.find('<!-- Affichage de l\'image optionnelle -->')
        if start_img != -1:
            end_img = rendered.find('{% endif %}', start_img)
            if end_img != -1:
                img_section = rendered[start_img:end_img+200]
                print(f"\nSection image extraite:\n{img_section}")
        
    except Exception as e:
        print(f"ERREUR lors du rendu: {e}")
        import traceback
        traceback.print_exc()
