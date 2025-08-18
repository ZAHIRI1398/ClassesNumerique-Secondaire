import os 
import sys 
from flask import url_for 
from flask_login import current_user 
 
def test_route():
    """Teste si la route modifiée est correctement enregistrée"""
    try:
        # Vérifier si le fichier school_registration_mod.py existe
        if os.path.exists("production_code/ClassesNumerique-Secondaire-main/blueprints/school_registration_mod.py"):
            print("[SUCCÈS] Le fichier school_registration_mod.py existe")
            return True
        else:
            print("[ERREUR] Le fichier school_registration_mod.py n\'existe pas")
            return False
    except Exception as e:
        print(f"[ERREUR] Une erreur est survenue: {str(e)}")
        return False
 
if __name__ == "__main__": 
    test_route() 
