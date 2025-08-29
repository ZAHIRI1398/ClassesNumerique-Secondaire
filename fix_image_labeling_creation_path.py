"""
Script pour corriger le chemin des images dans la route de création d'exercices image_labeling.

Ce script modifie le fichier modified_submit.py pour ajouter un slash au début des chemins
d'images lors de la création d'exercices d'étiquetage d'image, afin d'assurer la cohérence
avec la route d'édition qui utilise des chemins commençant par '/static/'.

Problème résolu:
- Lors de la création: chemins sauvegardés comme 'static/uploads/filename'
- Lors de l'édition: chemins attendus comme '/static/uploads/filename'
- Cette incohérence cause des problèmes d'affichage des images après création
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

# Rechercher et remplacer le code problématique
# Pattern à rechercher: main_image_path = f'static/uploads/{unique_filename}'
pattern = r"main_image_path = f'static/uploads/\{unique_filename\}'"
replacement = "main_image_path = f'/static/uploads/{unique_filename}'  # Ajout du slash initial pour cohérence"

# Effectuer le remplacement
new_content = re.sub(pattern, replacement, content)

# Vérifier si un remplacement a été effectué
if new_content == content:
    print("ATTENTION: Aucun remplacement effectué. Le pattern n'a pas été trouvé.")
    print("Vérifiez le pattern de recherche ou si le fichier a déjà été corrigé.")
else:
    # Écrire le contenu modifié dans le fichier
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    print("Modification effectuée avec succès!")
    print("Le chemin des images pour les exercices image_labeling est maintenant normalisé avec un slash initial.")

# Vérifier si le fichier exercise.image_path est également synchronisé avec content['main_image']
# dans la section de création d'exercice image_labeling

# Pattern pour vérifier si exercise.image_path est défini lors de la création
exercise_image_path_pattern = r"exercise = Exercise\([^)]*image_path=([^,\)]+)"
exercise_image_path_match = re.search(exercise_image_path_pattern, content)

if exercise_image_path_match:
    image_path_value = exercise_image_path_match.group(1).strip()
    print(f"Valeur actuelle de exercise.image_path: {image_path_value}")
    
    if image_path_value == "exercise_image_path":
        print("REMARQUE: exercise.image_path utilise exercise_image_path, qui peut ne pas être synchronisé avec content['main_image']")
        print("Vérifiez si une synchronisation supplémentaire est nécessaire.")
else:
    print("Impossible de déterminer la valeur de exercise.image_path dans la création d'exercice.")

print("\nRésumé des modifications:")
print("1. Ajout d'un slash initial aux chemins d'images lors de la création d'exercices image_labeling")
print("2. Assure la cohérence entre la création et l'édition d'exercices")
print("3. Évite les problèmes d'affichage des images après création")
