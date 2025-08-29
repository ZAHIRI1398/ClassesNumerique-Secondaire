"""
Script pour corriger directement le chemin des images dans la route de création d'exercices image_labeling.

Ce script modifie le fichier modified_submit.py pour ajouter un slash au début des chemins
d'images lors de la création d'exercices d'étiquetage d'image, et synchroniser exercise.image_path
avec content['main_image'] pour assurer la cohérence avec la route d'édition.

Problèmes résolus:
1. Lors de la création: chemins sauvegardés comme 'static/uploads/filename' (sans slash initial)
2. Lors de l'édition: chemins attendus comme '/static/uploads/filename' (avec slash initial)
3. Manque de synchronisation entre exercise.image_path et content['main_image']
"""

import os
import re
import shutil
from datetime import datetime

# Chemin du fichier à modifier
file_path = 'modified_submit.py'

# Créer une sauvegarde du fichier original
backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_path = f'{file_path}.bak_{backup_timestamp}'
shutil.copy2(file_path, backup_path)
print(f"Sauvegarde créée: {backup_path}")

# Lire le contenu du fichier
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# 1. Rechercher et remplacer le code problématique pour ajouter le slash initial
pattern1 = r"main_image_path = f'static/uploads/\{unique_filename\}'"
replacement1 = "main_image_path = f'/static/uploads/{unique_filename}'  # Ajout du slash initial pour cohérence"

# Effectuer le premier remplacement
modified_content = re.sub(pattern1, replacement1, content)

# 2. Rechercher le bloc de création d'exercice pour ajouter la synchronisation
# Nous cherchons après la ligne où exercise est créé avec Exercise()
pattern2 = r"(exercise = Exercise\([^)]*\))"
replacement2 = r"\1\n            # Synchroniser exercise.image_path avec content['main_image'] pour les exercices image_labeling\n            if exercise_type == 'image_labeling' and 'main_image' in content:\n                exercise.image_path = content['main_image']  # Assurer la cohérence"

# Effectuer le deuxième remplacement
modified_content = re.sub(pattern2, replacement2, modified_content)

# Vérifier si des remplacements ont été effectués
if modified_content == content:
    print("ATTENTION: Aucun remplacement effectué. Les patterns n'ont pas été trouvés.")
    print("Vérifiez les patterns de recherche ou si le fichier a déjà été corrigé.")
else:
    # Écrire le contenu modifié dans le fichier
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    print("Modifications effectuées avec succès!")
    print("1. Le chemin des images pour les exercices image_labeling est maintenant normalisé avec un slash initial")
    print("2. exercise.image_path est synchronisé avec content['main_image'] pour les exercices image_labeling")

print("\nRésumé des modifications:")
print("1. Ajout d'un slash initial aux chemins d'images lors de la création d'exercices image_labeling")
print("2. Synchronisation entre exercise.image_path et content['main_image']")
print("3. Assure la cohérence entre la création et l'édition d'exercices")
print("4. Évite les problèmes d'affichage des images après création")
