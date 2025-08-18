"""
Script pour ajouter un bouton École dans l'interface de connexion
"""
import os
import re
from flask import Flask, render_template, url_for

def add_school_button_to_login():
    """
    Ajoute un bouton École dans l'interface de connexion
    """
    # Chemin vers le template de connexion
    template_path = os.path.join('templates', 'login.html')
    
    # Vérifier si le fichier existe
    if not os.path.exists(template_path):
        print(f"Le fichier {template_path} n'existe pas.")
        return False
    
    # Lire le contenu du fichier
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Première modification: ajouter le bouton École dans le modal de connexion
    login_modal_pattern = r'(<div class="text-center">\s*<p class="mb-2">Pas encore inscrit \?</p>\s*<div class="d-grid gap-2">\s*<a href="\{\{ url_for\(\'register_teacher\'\) \}\}" class="btn-custom btn-outline-custom w-100">\s*<i class="fas fa-chalkboard-teacher me-2"></i> Enseignant\s*</a>\s*<a href="\{\{ url_for\(\'register_student\'\) \}\}" class="btn-custom btn-outline-custom w-100">\s*<i class="fas fa-user-graduate me-2"></i> Élève\s*</a>)'
    
    login_modal_replacement = r'\1\n                    <a href="{{ url_for(\'register_school\') }}" class="btn-custom btn-outline-custom w-100">\n                        <i class="fas fa-school me-2"></i> École\n                    </a>'
    
    content = re.sub(login_modal_pattern, login_modal_replacement, content)
    
    # Deuxième modification: ajouter le bouton École dans le modal de choix d'inscription
    register_choice_pattern = r'(<div class="d-grid gap-3">\s*<a href="\{\{ url_for\(\'register_teacher\'\) \}\}" class="btn-custom btn-primary-custom w-100">\s*<i class="fas fa-chalkboard-teacher me-2"></i> Enseignant\s*</a>\s*<a href="\{\{ url_for\(\'register_student\'\) \}\}" class="btn-custom btn-outline-custom w-100">\s*<i class="fas fa-user-graduate me-2"></i> Élève\s*</a>)'
    
    register_choice_replacement = r'\1\n                <a href="{{ url_for(\'register_school\') }}" class="btn-custom btn-outline-custom w-100">\n                    <i class="fas fa-school me-2"></i> École\n                </a>'
    
    content = re.sub(register_choice_pattern, register_choice_replacement, content)
    
    # Écrire le contenu modifié dans le fichier
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Le bouton École a été ajouté avec succès au template {template_path}.")
    return True

if __name__ == "__main__":
    add_school_button_to_login()
