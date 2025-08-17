#!/usr/bin/env python3
"""
Script pour ajouter une route de débogage spécifique pour les données POST
des exercices fill_in_blanks
"""

import sys
import os
import json
from flask import request, jsonify

def add_debug_route():
    """Ajoute une route de débogage pour les données POST"""
    
    # Chemin du fichier app.py
    app_path = 'app.py'
    
    # Vérifier si le fichier existe
    if not os.path.exists(app_path):
        print(f"Erreur: Le fichier {app_path} n'existe pas.")
        return False
    
    # Lire le contenu du fichier
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Vérifier si la route existe déjà
    if '@app.route(\'debug-form-data\', methods=[\'GET\', \'POST\'])' in content:
        print("La route de débogage existe déjà.")
        return True
    
    # Code de la nouvelle route à ajouter
    new_route = '''
@app.route('/debug-form-data', methods=['GET', 'POST'])
@login_required
def debug_form_data():
    # Route de débogage pour analyser les données POST des formulaires
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        app.logger.info(f"[DEBUG_FORM_DATA] Données POST reçues: {dict(request.form)}")
        
        # Analyser les données du formulaire
        form_data = dict(request.form)
        
        # Extraire les champs answer_X
        answer_fields = {k: v for k, v in form_data.items() if k.startswith('answer_')}
        
        # Analyser les indices des champs answer_X
        answer_indices = []
        for key in answer_fields.keys():
            try:
                index = int(key.split('_')[1])
                answer_indices.append(index)
            except (ValueError, IndexError):
                pass
        
        # Trier les indices
        answer_indices.sort()
        
        # Créer un rapport détaillé
        report = {
            'total_fields': len(form_data),
            'answer_fields': len(answer_fields),
            'answer_indices': answer_indices,
            'answer_values': {f"answer_{i}": form_data.get(f"answer_{i}", "") for i in answer_indices},
            'all_form_data': form_data
        }
        
        return jsonify({
            'success': True,
            'message': 'Données du formulaire analysées avec succès',
            'report': report
        })
    
    # Afficher un formulaire de test pour les requêtes GET
    return render_template('debug/form_data.html')
'''
    
    # Ajouter la route avant la dernière ligne (if __name__ == '__main__':)
    if 'if __name__ == \'__main__\':\'' in content:
        # Trouver la position de la dernière occurrence de if __name__ == '__main__':
        position = content.rfind('if __name__ == \'__main__\':\'')
        
        # Insérer la nouvelle route avant cette ligne
        new_content = content[:position] + new_route + '\n\n' + content[position:]
    else:
        # Si la ligne n'est pas trouvée, ajouter à la fin du fichier
        new_content = content + '\n\n' + new_route
    
    # Écrire le contenu modifié dans le fichier
    with open(app_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print("Route de débogage ajoutée avec succès.")
    
    # Créer le template nécessaire
    template_dir = os.path.join('templates', 'debug')
    os.makedirs(template_dir, exist_ok=True)
    
    template_path = os.path.join(template_dir, 'form_data.html')
    
    # Contenu du template
    template_content = '''{% extends "base.html" %}

{% block title %}Débogage des données de formulaire{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header bg-primary text-white">
            <h2>Débogage des données de formulaire</h2>
        </div>
        <div class="card-body">
            <h3>Formulaire de test pour fill_in_blanks</h3>
            <form method="POST" action="{{ url_for('debug_form_data') }}">
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
                
                <div class="mb-3">
                    <label for="answer_0" class="form-label">Réponse 1 (answer_0)</label>
                    <input type="text" class="form-control" id="answer_0" name="answer_0" value="test1">
                </div>
                
                <div class="mb-3">
                    <label for="answer_1" class="form-label">Réponse 2 (answer_1)</label>
                    <input type="text" class="form-control" id="answer_1" name="answer_1" value="test2">
                </div>
                
                <div class="mb-3">
                    <label for="answer_2" class="form-label">Réponse 3 (answer_2)</label>
                    <input type="text" class="form-control" id="answer_2" name="answer_2" value="test3">
                </div>
                
                <div class="mb-3">
                    <label for="answer_3" class="form-label">Réponse 4 (answer_3)</label>
                    <input type="text" class="form-control" id="answer_3" name="answer_3" value="test4">
                </div>
                
                <div class="mb-3">
                    <label for="answer_4" class="form-label">Réponse 5 (answer_4)</label>
                    <input type="text" class="form-control" id="answer_4" name="answer_4" value="test5">
                </div>
                
                <button type="submit" class="btn btn-primary">Soumettre</button>
            </form>
            
            <hr>
            
            <h3>Instructions</h3>
            <p>Cette page permet de tester la soumission de formulaire et d'analyser les données POST reçues par le serveur.</p>
            <p>Utilisez ce formulaire pour simuler une soumission d'exercice fill_in_blanks et vérifier que tous les champs sont correctement transmis.</p>
            <p>Les résultats seront affichés en format JSON après la soumission.</p>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # Écrire le template
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(template_content)
    
    print(f"Template créé: {template_path}")
    return True

if __name__ == '__main__':
    add_debug_route()
    print("Pour utiliser cette route, redémarrez l'application Flask et accédez à /debug-form-data")
