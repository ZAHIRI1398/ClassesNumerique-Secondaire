"""
Script pour corriger l'erreur de syntaxe dans app.py
(bloc try sans except à la ligne 2812)
"""
import re

# Lire le fichier app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Ajouter un bloc except à la fin du fichier
if content.endswith('\n'):
    fixed_content = content + "    except Exception as e:\n        app.logger.error(f\"[ERROR] Une erreur s'est produite: {str(e)}\")\n        flash('Une erreur s\\'est produite lors du traitement de votre réponse.', 'error')\n        return redirect(url_for('view_exercise', exercise_id=exercise_id))\n"
else:
    fixed_content = content + "\n    except Exception as e:\n        app.logger.error(f\"[ERROR] Une erreur s'est produite: {str(e)}\")\n        flash('Une erreur s\\'est produite lors du traitement de votre réponse.', 'error')\n        return redirect(url_for('view_exercise', exercise_id=exercise_id))\n"

# Écrire le contenu corrigé dans app.py
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("Correction appliquée avec succès !")
