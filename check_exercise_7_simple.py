#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple pour vérifier l'exercice 7
"""

import os
import sqlite3

def check_exercise_7():
    """Vérifie l'exercice 7"""
    
    # Chemins possibles pour la base de données
    db_paths = [
        "instance/app.db",
        "instance/classe_numerique.db",
        "app.db",
        "classe_numerique.db"
    ]
    
    print("=== VERIFICATION EXERCICE 7 ===")
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"Base trouvee: {db_path}")
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Lister tous les exercices
                cursor.execute("SELECT id, title, image_path FROM exercise ORDER BY id")
                exercises = cursor.fetchall()
                
                print(f"Nombre d'exercices: {len(exercises)}")
                
                for ex_id, title, image_path in exercises:
                    print(f"  ID {ex_id}: {title}")
                    if image_path:
                        print(f"    Image: {image_path}")
                        
                        # Vérifier si le fichier existe
                        if image_path.startswith('/static/'):
                            file_path = image_path[1:]  # Enlever le /
                        else:
                            file_path = image_path
                            
                        if os.path.exists(file_path):
                            size = os.path.getsize(file_path)
                            if size > 0:
                                print(f"    Fichier OK ({size} bytes)")
                            else:
                                print(f"    Fichier VIDE (0 bytes)")
                        else:
                            print(f"    Fichier MANQUANT")
                    else:
                        print(f"    Pas d'image")
                
                conn.close()
                print()
                
            except Exception as e:
                print(f"Erreur avec {db_path}: {e}")
        else:
            print(f"Base non trouvee: {db_path}")
    
    print("=== FIN VERIFICATION ===")

if __name__ == "__main__":
    check_exercise_7()
