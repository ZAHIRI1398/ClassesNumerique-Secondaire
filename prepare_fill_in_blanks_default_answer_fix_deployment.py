"""
Script de préparation pour le déploiement de la correction de l'affichage des réponses par défaut
dans les exercices de type "Texte à trous" (fill_in_blanks).

Ce script:
1. Sauvegarde les fichiers modifiés
2. Vérifie que les modifications nécessaires sont présentes
3. Génère un message de commit et des instructions de déploiement
"""

import os
import re
import shutil
import datetime
import sys

# Configuration
APP_FILE = 'app.py'
TEMPLATE_FILE = 'templates/exercise_types/fill_in_blanks.html'
BACKUP_DIR = f'backup_fill_in_blanks_default_answer_fix_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'

# Motifs à rechercher pour vérifier que les modifications sont présentes
APP_PATTERN = r'show_answers\s*=\s*False'
TEMPLATE_PATTERN = r'{%\s*if\s+show_answers\s*%}'

def create_backup():
    """Crée une sauvegarde des fichiers modifiés"""
    print(f"Création du répertoire de sauvegarde '{BACKUP_DIR}'...")
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Sauvegarde de app.py
    if os.path.exists(APP_FILE):
        shutil.copy2(APP_FILE, os.path.join(BACKUP_DIR, APP_FILE))
        print(f"[OK] Sauvegarde de '{APP_FILE}' effectuee")
    else:
        print(f"[ATTENTION] Fichier '{APP_FILE}' non trouve")
    
    # Sauvegarde du template
    if os.path.exists(TEMPLATE_FILE):
        # Creer le repertoire de destination si necessaire
        template_dest = os.path.join(BACKUP_DIR, os.path.basename(TEMPLATE_FILE))
        shutil.copy2(TEMPLATE_FILE, template_dest)
        print(f"[OK] Sauvegarde de '{TEMPLATE_FILE}' effectuee")
    else:
        print(f"[ATTENTION] Fichier '{TEMPLATE_FILE}' non trouve")

def check_modifications():
    """Verifie que les modifications necessaires sont presentes"""
    all_good = True
    
    # Verifier app.py
    if os.path.exists(APP_FILE):
        with open(APP_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            if re.search(APP_PATTERN, content):
                print(f"[OK] Modification 'show_answers' trouvee dans '{APP_FILE}'")
            else:
                print(f"[ATTENTION] Modification 'show_answers' NON trouvee dans '{APP_FILE}'")
                all_good = False
    else:
        print(f"[ATTENTION] Fichier '{APP_FILE}' non trouve")
        all_good = False
    
    # Verifier le template
    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            if re.search(TEMPLATE_PATTERN, content):
                print(f"[OK] Condition 'show_answers' trouvee dans '{TEMPLATE_FILE}'")
            else:
                print(f"[ATTENTION] Condition 'show_answers' NON trouvee dans '{TEMPLATE_FILE}'")
                all_good = False
    else:
        print(f"[ATTENTION] Fichier '{TEMPLATE_FILE}' non trouve")
        all_good = False
    
    return all_good

def generate_commit_message():
    """Genere un message de commit pour le deploiement"""
    return """Fix: Affichage des reponses par defaut dans les exercices "Texte a trous"

Cette correction empeche l'affichage automatique des reponses utilisateur
dans les exercices de type "Texte a trous" (fill_in_blanks) avant soumission.

Modifications:
- Ajout d'une variable 'show_answers' dans la fonction view_exercise
- Modification du template pour n'afficher les reponses que si show_answers est vrai
- Verification de la presence de feedback pour determiner si l'exercice a ete soumis

Documentation: voir DOCUMENTATION_FILL_IN_BLANKS_DEFAULT_ANSWER_FIX.md"""

def main():
    print("=== Preparation du deploiement de la correction d'affichage des reponses par defaut ===\n")
    
    # Creer les sauvegardes
    create_backup()
    print("\n=== Verification des modifications ===")
    
    # Verifier les modifications
    if check_modifications():
        print("[OK] Toutes les modifications necessaires sont presentes")
        
        # Generer le message de commit
        commit_message = generate_commit_message()
        print("\n=== Message de commit suggere ===\n")
        print(commit_message)
        
        # Instructions de deploiement
        print("\n=== Instructions de deploiement ===\n")
        print("1. Verifiez que les tests passent:")
        print("   python test_fill_in_blanks_display_fix.py")
        print("\n2. Commitez les modifications:")
        print("   git add app.py templates/exercise_types/fill_in_blanks.html DOCUMENTATION_FILL_IN_BLANKS_DEFAULT_ANSWER_FIX.md")
        print("   git commit -m \"Fix: Affichage des reponses par defaut dans les exercices Texte a trous\"")
        print("\n3. Poussez les modifications vers le depot distant:")
        print("   git push origin main")
        print("\n4. Deployez sur Railway:")
        print("   Attendez que le deploiement automatique se termine ou declenchez un deploiement manuel")
    else:
        print("\n[ATTENTION] Certaines modifications necessaires sont manquantes. Veuillez verifier les fichiers.")
        sys.exit(1)

if __name__ == "__main__":
    main()
