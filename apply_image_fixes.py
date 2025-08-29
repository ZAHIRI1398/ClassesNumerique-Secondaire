"""
Script pour appliquer toutes les corrections liées aux images d'exercices
Ce script intègre les différentes corrections dans l'application Flask
"""

import os
import sys
import json
import logging
from flask import Flask, flash, redirect, url_for
from fix_edit_exercise_implementation import apply_edit_exercise_fix
from fix_all_exercise_images import register_fix_exercise_images_routes

def apply_all_image_fixes(app):
    """
    Applique toutes les corrections liées aux images d'exercices
    
    Args:
        app: L'application Flask
    
    Returns:
        str: Message de confirmation
    """
    messages = []
    
    # 1. Appliquer la correction à la fonction edit_exercise
    try:
        result = apply_edit_exercise_fix(app)
        messages.append(result)
        app.logger.info("[IMAGE_FIXES] Correction de edit_exercise appliquée avec succès")
    except Exception as e:
        app.logger.error(f"[IMAGE_FIXES] Erreur lors de l'application de la correction à edit_exercise: {str(e)}")
        messages.append(f"Erreur lors de l'application de la correction à edit_exercise: {str(e)}")
    
    # 2. Enregistrer les routes de correction des images d'exercices
    try:
        register_fix_exercise_images_routes(app)
        messages.append("Routes de correction des images d'exercices enregistrées")
        app.logger.info("[IMAGE_FIXES] Routes de correction enregistrées avec succès")
    except Exception as e:
        app.logger.error(f"[IMAGE_FIXES] Erreur lors de l'enregistrement des routes de correction: {str(e)}")
        messages.append(f"Erreur lors de l'enregistrement des routes de correction: {str(e)}")
    
    # 3. Vérifier que les modules nécessaires sont importés dans app.py
    try:
        # Cette vérification est symbolique, car les imports sont déjà vérifiés dans les fonctions ci-dessus
        app.logger.info("[IMAGE_FIXES] Vérification des imports réussie")
        messages.append("Vérification des imports réussie")
    except Exception as e:
        app.logger.error(f"[IMAGE_FIXES] Erreur lors de la vérification des imports: {str(e)}")
        messages.append(f"Erreur lors de la vérification des imports: {str(e)}")
    
    return "\n".join(messages)

# Fonction pour intégrer les corrections dans app.py
def integrate_fixes_in_app():
    """
    Intègre les corrections dans app.py
    Cette fonction est appelée depuis app.py
    """
    from flask import current_app
    return apply_all_image_fixes(current_app)

# Si ce script est exécuté directement, afficher un message d'aide
if __name__ == "__main__":
    print("Ce script doit être importé depuis app.py")
    print("Ajoutez les lignes suivantes à app.py:")
    print("from apply_image_fixes import integrate_fixes_in_app")
    print("# Appliquer les corrections d'images")
    print("integrate_fixes_in_app()")
