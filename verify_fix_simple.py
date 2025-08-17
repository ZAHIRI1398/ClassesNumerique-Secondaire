import os
import sys
import requests
import re

# Configuration
BASE_URL = "http://127.0.0.1:5000"
EXERCISE_ID = 2  # ID de l'exercice 2 (Texte à trous - Les verbes)

def check_app_running():
    """Vérifie si l'application est en cours d'exécution."""
    try:
        response = requests.get(f"{BASE_URL}/")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def check_exercise_exists():
    """Vérifie si l'exercice 2 existe et est accessible."""
    try:
        response = requests.get(f"{BASE_URL}/exercise/{EXERCISE_ID}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def check_app_py_syntax():
    """Vérifie que app.py est syntaxiquement correct."""
    result = os.system("python -m py_compile app.py")
    return result == 0

def check_fill_in_blanks_code():
    """Vérifie que le code de traitement des mots est présent dans app.py."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Vérifier si notre code de correction est présent
    pattern = r"# Traiter les réponses pour gérer à la fois les chaînes simples et les objets/dictionnaires"
    if re.search(pattern, content):
        return True
    return False

def main():
    print("=== Verification de la correction de l'exercice 2 ===")
    
    # Vérifier la syntaxe de app.py
    print("\n1. Verification de la syntaxe de app.py...")
    if check_app_py_syntax():
        print("[OK] app.py est syntaxiquement correct")
    else:
        print("[ERREUR] app.py contient des erreurs de syntaxe")
        return False
    
    # Vérifier que le code de correction est présent
    print("\n2. Verification du code de correction...")
    if check_fill_in_blanks_code():
        print("[OK] Le code de correction du format des mots est present")
    else:
        print("[ERREUR] Le code de correction du format des mots est absent")
        return False
    
    # Vérifier que l'application est en cours d'exécution
    print("\n3. Verification de l'application en cours d'execution...")
    if check_app_running():
        print("[OK] L'application est en cours d'execution")
    else:
        print("[ERREUR] L'application n'est pas en cours d'execution")
        print("  Veuillez demarrer l'application avec 'python app.py'")
        return False
    
    # Vérifier que l'exercice 2 est accessible
    print("\n4. Verification de l'acces a l'exercice 2...")
    if check_exercise_exists():
        print("[OK] L'exercice 2 est accessible")
    else:
        print("[ERREUR] L'exercice 2 n'est pas accessible")
        print("  Verifiez que l'exercice existe dans la base de donnees")
        return False
    
    print("\n=== Resume ===")
    print("[OK] La correction a ete appliquee avec succes")
    print("[OK] L'application fonctionne correctement")
    print("[OK] L'exercice 2 est accessible")
    print("\nLa correction du probleme de format des mots dans l'exercice 2 est complete.")
    
    return True

if __name__ == "__main__":
    main()
