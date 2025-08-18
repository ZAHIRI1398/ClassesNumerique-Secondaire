"""
Script pour corriger les problèmes d'encodage Unicode dans les scripts d'intégration
"""

import os
import sys
import re

def fix_unicode_errors():
    """Remplace les caractères Unicode problématiques par des alternatives ASCII"""
    try:
        # Chemin vers le répertoire de production
        production_dir = os.path.join('production_code', 'ClassesNumerique-Secondaire-main')
        
        # Liste des fichiers à corriger
        files_to_fix = [
            os.path.join(production_dir, 'integrate_select_school_fix.py'),
            os.path.join(production_dir, 'app.py'),
            os.path.join(production_dir, 'test_school_registration_mod.py')
        ]
        
        # Dictionnaire de remplacement des caractères Unicode
        replacements = {
            '\u2705': '[OK]',     # Symbole check
            '\u274c': '[ERREUR]', # Symbole X
            '\u2717': '[ECHEC]'   # Symbole X
        }
        
        for file_path in files_to_fix:
            if os.path.exists(file_path):
                # Lire le contenu du fichier
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                # Remplacer les caractères Unicode problématiques
                for unicode_char, replacement in replacements.items():
                    content = content.replace(unicode_char, replacement)
                
                # Écrire le contenu modifié
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"[INFO] Caractères Unicode remplacés dans {file_path}")
        
        print("[SUCCÈS] Problèmes d'encodage Unicode corrigés")
        return True
    except Exception as e:
        print(f"[ERREUR] Échec de la correction des problèmes d'encodage: {str(e)}")
        return False

if __name__ == "__main__":
    fix_unicode_errors()
