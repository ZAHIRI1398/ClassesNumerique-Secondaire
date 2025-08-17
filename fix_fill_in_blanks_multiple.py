"""
Script pour corriger le problème de scoring des exercices fill_in_blanks
avec plusieurs blancs sur la même ligne.

Ce script modifie le fichier app.py pour utiliser la fonction get_blank_location
afin de déterminer correctement l'emplacement des blancs dans les phrases.
"""

import os
import re
import shutil
from datetime import datetime

# Fonction pour créer une sauvegarde du fichier app.py
def backup_app_file():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source = "app.py"
    backup = f"app.py.bak.{timestamp}"
    
    if os.path.exists(source):
        shutil.copy2(source, backup)
        print(f"[OK] Sauvegarde créée: {backup}")
        return True
    else:
        print(f"[ERREUR] Le fichier {source} n'existe pas")
        return False

# Fonction pour remplacer le code de détermination de l'index de phrase
def replace_sentence_index_code(content):
    # Ancien code à remplacer
    old_code = """                # Déterminer l'index de la phrase à laquelle appartient ce blanc
                sentence_index = -1
                if 'sentences' in content:
                    blank_count = 0
                    for idx, sentence in enumerate(content['sentences']):
                        blanks_in_sentence = sentence.count('___')
                        if blank_count <= i < blank_count + blanks_in_sentence:
                            sentence_index = idx
                            break
                        blank_count += blanks_in_sentence"""
    
    # Nouveau code utilisant get_blank_location
    new_code = """                # Déterminer l'index de la phrase à laquelle appartient ce blanc
                sentence_index = -1
                local_blank_index = -1
                if 'sentences' in content:
                    sentence_index, local_blank_index = get_blank_location(i, content['sentences'])
                    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Blank {i} est dans la phrase {sentence_index}, position locale {local_blank_index}")"""
    
    # Remplacer toutes les occurrences
    modified_content = content.replace(old_code, new_code)
    
    # Vérifier si des modifications ont été effectuées
    if modified_content != content:
        print("[OK] Code de détermination d'index de phrase remplacé avec succès")
        return modified_content
    else:
        print("[ERREUR] Impossible de trouver le code à remplacer")
        return content

# Fonction principale
def main():
    print("=== CORRECTION DU PROBLÈME DE SCORING FILL_IN_BLANKS AVEC PLUSIEURS BLANCS PAR LIGNE ===\n")
    
    # Créer une sauvegarde
    if not backup_app_file():
        return
    
    try:
        # Lire le contenu du fichier app.py
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Remplacer le code
        modified_content = replace_sentence_index_code(content)
        
        # Écrire le contenu modifié
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(modified_content)
        
        print("\n[OK] Modifications appliquées avec succès")
        print("\nPour tester la correction, exécutez:")
        print("python test_fill_in_blanks_multiple.py")
        
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la modification du fichier: {str(e)}")

if __name__ == "__main__":
    main()
