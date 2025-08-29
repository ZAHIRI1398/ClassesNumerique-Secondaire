import sqlite3
import json
import os

# Vérifier l'état de l'exercice QCM après modification
conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()

# Récupérer l'exercice QCM modifié
cursor.execute('SELECT id, title, content, image_path FROM exercise WHERE id = 4')
result = cursor.fetchone()

if result:
    exercise_id, title, content_json, image_path = result
    print(f"=== EXERCICE QCM ID {exercise_id} ===")
    print(f"Titre: {title}")
    print(f"Image_path (colonne): {image_path}")
    
    # Parser le contenu JSON
    try:
        content = json.loads(content_json)
        print(f"Contenu JSON:")
        print(f"  - Clés disponibles: {list(content.keys())}")
        
        if 'image' in content:
            print(f"  - Image dans contenu: {content['image']}")
            # Vérifier si le fichier existe
            image_file = content['image']
            if image_file.startswith('/'):
                full_path = f"static{image_file}"
            else:
                full_path = image_file
            
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                print(f"  - Fichier existe: OUI ({size} octets)")
            else:
                print(f"  - Fichier existe: NON")
                print(f"  - Chemin testé: {full_path}")
        else:
            print("  - Pas d'image dans le contenu JSON")
            
        if 'questions' in content:
            print(f"  - Nombre de questions: {len(content['questions'])}")
            for i, q in enumerate(content['questions']):
                print(f"    Question {i+1}: {q.get('text', q.get('question', 'N/A'))[:50]}...")
    except json.JSONDecodeError as e:
        print(f"Erreur parsing JSON: {e}")
        print(f"Contenu brut: {content_json}")
else:
    print("Exercice QCM non trouvé")

conn.close()

# Lister les fichiers récents dans uploads
print("\n=== FICHIERS RÉCENTS DANS UPLOADS ===")
uploads_dir = "static/uploads"
if os.path.exists(uploads_dir):
    files = []
    for f in os.listdir(uploads_dir):
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            path = os.path.join(uploads_dir, f)
            size = os.path.getsize(path)
            mtime = os.path.getmtime(path)
            files.append((f, size, mtime))
    
    # Trier par date de modification (plus récent en premier)
    files.sort(key=lambda x: x[2], reverse=True)
    
    print("5 fichiers les plus récents:")
    for f, size, mtime in files[:5]:
        import datetime
        date_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"  - {f} ({size} octets, {date_str})")
