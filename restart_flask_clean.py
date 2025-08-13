#!/usr/bin/env python3
"""
Script pour redémarrer Flask avec une base de données propre
"""

import os
import sys
import subprocess
import time

def restart_flask_clean():
    """Redémarrer Flask avec une base de données propre"""
    
    print("=== NETTOYAGE ET REDEMARRAGE FLASK ===")
    
    # 1. Arrêter tous les processus Python
    print("1. Arret des processus Python...")
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                      capture_output=True, text=True)
        print("   Processus arretes")
    except:
        print("   Aucun processus a arreter")
    
    # 2. Supprimer les fichiers de cache Python
    print("2. Nettoyage cache Python...")
    cache_dirs = ['__pycache__', '.pytest_cache']
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                import shutil
                shutil.rmtree(cache_dir)
                print(f"   Cache {cache_dir} supprime")
            except:
                print(f"   Impossible de supprimer {cache_dir}")
    
    # 3. Vérifier la base de données
    print("3. Verification base de donnees...")
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
    if os.path.exists(db_path):
        print(f"   Base trouvee: {db_path}")
        
        # Test rapide de la structure
        import sqlite3
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(user)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'school_name' in columns:
                print("   Colonne school_name OK")
            else:
                print("   ERREUR: school_name manquante!")
            conn.close()
        except Exception as e:
            print(f"   ERREUR test DB: {e}")
    else:
        print("   ERREUR: Base non trouvee!")
    
    # 4. Attendre un peu
    print("4. Attente nettoyage...")
    time.sleep(2)
    
    # 5. Redémarrer Flask
    print("5. Redemarrage Flask...")
    print("   Commande: python app.py")
    print("   Veuillez executer manuellement: python app.py")
    
    return True

if __name__ == "__main__":
    restart_flask_clean()
