import os
import json
import sqlite3
import shutil
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Fonction pour créer une image placeholder si nécessaire
def create_placeholder_image(filename, text="Image placeholder", size=(300, 200)):
    try:
        img = Image.new('RGB', size, color=(240, 240, 240))
        draw = ImageDraw.Draw(img)
        
        # Dessiner un cadre
        draw.rectangle([(0, 0), (size[0]-1, size[1]-1)], outline=(200, 200, 200), width=2)
        
        # Ajouter du texte
        try:
            # Essayer de charger une police standard
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            # Fallback sur la police par défaut
            font = ImageFont.load_default()
            
        text_width = draw.textlength(text, font=font)
        text_position = ((size[0] - text_width) / 2, size[1] / 2 - 10)
        draw.text(text_position, text, fill=(100, 100, 100), font=font)
        
        # Créer le dossier si nécessaire
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Sauvegarder l'image
        img.save(filename)
        print(f"Image placeholder créée: {filename}")
        return True
    except Exception as e:
        print(f"Erreur lors de la création de l'image placeholder: {e}")
        return False

# Fonction pour corriger un exercice spécifique
def fix_exercise(exercise_id):
    conn = sqlite3.connect('instance/app.db')
    cursor = conn.cursor()
    
    # Récupérer l'exercice
    cursor.execute('SELECT id, title, content FROM exercise WHERE id = ?', (exercise_id,))
    result = cursor.fetchone()
    
    if not result:
        print(f"Exercice {exercise_id} non trouvé")
        conn.close()
        return False
    
    exercise_id, title, content_str = result
    print(f"Correction de l'exercice #{exercise_id}: {title}")
    
    # Charger le contenu JSON
    content = json.loads(content_str)
    modified = False
    
    # Vérifier si l'exercice a des paires
    if 'pairs' in content:
        for pair in content['pairs']:
            if 'left' in pair and 'content' in pair['left'] and pair['left']['type'] == 'image':
                old_path = pair['left']['content']
                
                # Normaliser le chemin d'image
                if '/static/exercises/' in old_path:
                    new_path = old_path.replace('/static/exercises/', '/static/uploads/')
                    pair['left']['content'] = new_path
                    print(f"  - Chemin image gauche normalisé: {old_path} -> {new_path}")
                    modified = True
                
                # Vérifier si l'image existe physiquement
                image_path = pair['left']['content'].lstrip('/')
                full_path = os.path.join(os.getcwd(), image_path)
                
                if not os.path.exists(full_path):
                    print(f"  - Image manquante: {full_path}")
                    
                    # Créer le dossier si nécessaire
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    # Créer une image placeholder
                    create_placeholder_image(full_path, f"Image {pair.get('id', 'placeholder')}")
            
            if 'right' in pair and 'content' in pair['right'] and pair['right']['type'] == 'image':
                old_path = pair['right']['content']
                
                # Normaliser le chemin d'image
                if '/static/exercises/' in old_path:
                    new_path = old_path.replace('/static/exercises/', '/static/uploads/')
                    pair['right']['content'] = new_path
                    print(f"  - Chemin image droite normalisé: {old_path} -> {new_path}")
                    modified = True
                
                # Vérifier si l'image existe physiquement
                image_path = pair['right']['content'].lstrip('/')
                full_path = os.path.join(os.getcwd(), image_path)
                
                if not os.path.exists(full_path):
                    print(f"  - Image manquante: {full_path}")
                    
                    # Créer le dossier si nécessaire
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    # Créer une image placeholder
                    create_placeholder_image(full_path, f"Image {pair.get('id', 'placeholder')}")
    
    # Sauvegarder les modifications si nécessaire
    if modified:
        cursor.execute('UPDATE exercise SET content = ? WHERE id = ?', (json.dumps(content), exercise_id))
        conn.commit()
        print(f"Exercice #{exercise_id} mis à jour avec succès")
    else:
        print(f"Aucune modification nécessaire pour l'exercice #{exercise_id}")
    
    conn.close()
    return True

# Exécution principale
if __name__ == "__main__":
    # Corriger l'exercice problématique (ID 45)
    fix_exercise(45)
    
    print("\nCorrection terminée. Veuillez redémarrer l'application Flask pour voir les changements.")
