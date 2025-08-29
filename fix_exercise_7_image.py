#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour corriger l'exercice 7 avec le bon nom de fichier
"""

import os
import sqlite3
import json

def fix_exercise_7_image():
    """Corriger le chemin d'image de l'exercice 7"""
    
    # Chemin vers la base de données
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"Base de donnees non trouvee: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Le fichier qui existe réellement
        actual_filename = "qcm_20250824_001159_43396886.png"
        actual_path = f"/static/exercises/{actual_filename}"
        
        print("CORRECTION EXERCICE 7")
        print("=" * 30)
        print(f"Nouveau chemin: {actual_path}")
        
        # Mettre à jour l'exercice 7
        cursor.execute("UPDATE exercise SET image_path = ? WHERE id = 7", (actual_path,))
        
        # Récupérer et mettre à jour le contenu JSON
        cursor.execute("SELECT content FROM exercise WHERE id = 7")
        result = cursor.fetchone()
        
        if result and result[0]:
            try:
                content_data = json.loads(result[0])
                content_data['image'] = actual_path
                new_content = json.dumps(content_data)
                cursor.execute("UPDATE exercise SET content = ? WHERE id = 7", (new_content,))
                print("Contenu JSON mis a jour")
            except json.JSONDecodeError:
                print("Erreur decodage JSON")
        
        # Valider les changements
        conn.commit()
        conn.close()
        
        print("Exercice 7 corrige avec succes!")
        return True
        
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    fix_exercise_7_image()
