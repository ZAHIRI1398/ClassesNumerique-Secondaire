
import re

def fix_app_py_scoring():
    # Chemin du fichier app.py
    app_path = 'app.py'
    
    # Lire le contenu du fichier
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Sauvegarder une copie de sauvegarde
    with open(app_path + '.bak.fill_in_blanks_fix', 'w', encoding='utf-8') as file:
        file.write(content)
    
    # Motif à rechercher - code qui fait le double comptage
    pattern = r"(\s+# Compter le nombre réel de blancs dans le contenu\s+total_blanks_in_content = 0\s+)if 'text' in content:\s+text_blanks = content\['text'\].count\('___'\)\s+total_blanks_in_content \+= text_blanks\s+.*?\s+if 'sentences' in content:\s+sentences_blanks = sum\(s.count\('___'\) for s in content\['sentences'\]\)\s+total_blanks_in_content \+= sentences_blanks"
    
    # Nouveau code qui évite le double comptage
    replacement = r"\1if 'sentences' in content:\n        sentences_blanks = sum(s.count('___') for s in content['sentences'])\n        total_blanks_in_content = sentences_blanks\n        app.logger.info(f\"[FILL_IN_BLANKS_DEBUG] Format 'sentences' detected: {sentences_blanks} blanks in sentences\")\n    elif 'text' in content:\n        text_blanks = content['text'].count('___')\n        total_blanks_in_content = text_blanks\n        app.logger.info(f\"[FILL_IN_BLANKS_DEBUG] Format 'text' detected: {text_blanks} blanks in text\")"
    
    # Appliquer la modification
    modified_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Vérifier si des modifications ont été apportées
    if modified_content == content:
        print("Aucune modification n'a été apportée. Le motif n'a pas été trouvé.")
        return False
    
    # Écrire le contenu modifié
    with open(app_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("Le fichier app.py a été modifié avec succès pour corriger le problème de double comptage.")
    return True

if __name__ == "__main__":
    fix_app_py_scoring()
