#!/usr/bin/env python3
"""
Script pour corriger la route de diagnostic sur Railway
"""

import os
import re
import sys

def fix_railway_diagnostic():
    """Corrige la route de diagnostic pour qu'elle fonctionne sur Railway"""
    app_path = 'app.py'
    
    # Vérifier que le fichier existe
    if not os.path.exists(app_path):
        print(f"Erreur: {app_path} n'existe pas!")
        return False
    
    # Lire le contenu du fichier
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si la route existe
    if '@app.route(\'/diagnostic-fill-in-blanks\')' not in content:
        print("La route de diagnostic n'existe pas dans le fichier!")
        return False
    
    # Extraire la route actuelle pour la remplacer
    route_pattern = r'# Route de diagnostic pour fill_in_blanks\s*@app\.route\(\'/diagnostic-fill-in-blanks\'\)(.*?)# Configuration du logging'
    route_match = re.search(route_pattern, content, re.DOTALL)
    
    if not route_match:
        print("Impossible de trouver la route de diagnostic complète!")
        return False
    
    # Préparer la nouvelle route simplifiée et sécurisée
    new_route_code = """# Route de diagnostic pour fill_in_blanks
@app.route('/diagnostic-fill-in-blanks')
def diagnostic_fill_in_blanks():
    \"\"\"Route de diagnostic simplifiée pour vérifier les problèmes fill_in_blanks\"\"\"
    # Sécurité: vérifier si l'utilisateur est admin
    if not current_user.is_authenticated:
        return "Accès non autorisé - Connexion requise", 403
        
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        return "Accès non autorisé - Droits administrateur requis", 403
        
    results = []
    
    # 1. Vérifier l'environnement
    results.append("<h1>DIAGNOSTIC FILL_IN_BLANKS SIMPLIFIÉ</h1>")
    results.append("<h2>1. ENVIRONNEMENT</h2>")
    
    # Vérifier les variables d'environnement
    env_vars = {
        'FLASK_ENV': os.environ.get('FLASK_ENV', 'non défini'),
        'RAILWAY_ENVIRONMENT': os.environ.get('RAILWAY_ENVIRONMENT', 'non défini'),
        'PORT': os.environ.get('PORT', 'non défini')
    }
    
    results.append("<h3>Variables d'environnement:</h3>")
    for key, value in env_vars.items():
        results.append(f"<p>{key}: {value}</p>")
    
    # 2. Vérifier les dossiers d'uploads
    results.append("<h2>2. DOSSIERS UPLOADS</h2>")
    
    static_dir = os.path.join(os.getcwd(), 'static')
    uploads_dir = os.path.join(static_dir, 'uploads')
    
    results.append(f"<p>Dossier static: {static_dir} - Existe: {os.path.exists(static_dir)}</p>")
    results.append(f"<p>Dossier uploads: {uploads_dir} - Existe: {os.path.exists(uploads_dir)}</p>")
    
    # Créer uploads si nécessaire
    if not os.path.exists(uploads_dir):
        try:
            os.makedirs(uploads_dir, exist_ok=True)
            results.append("<p style='color: green;'>✓ Dossier uploads créé</p>")
        except Exception as e:
            results.append(f"<p style='color: red;'>✗ Erreur création uploads: {str(e)}</p>")
    else:
        results.append("<p style='color: green;'>✓ Dossier uploads existe</p>")
    
    # 3. Vérifier les exercices fill_in_blanks (sans analyse JSON)
    results.append("<h2>3. EXERCICES FILL_IN_BLANKS</h2>")
    
    try:
        exercises = Exercise.query.filter_by(exercise_type='fill_in_blanks').all()
        results.append(f"<p>Nombre d'exercices: {len(exercises)}</p>")
        
        if exercises:
            # Prendre le premier exercice pour analyse basique
            ex = exercises[0]
            results.append(f"<h3>Exercice {ex.id}: {ex.title}</h3>")
            
            # Image
            if ex.image_path:
                results.append(f"<p>Image path: {ex.image_path}</p>")
    except Exception as e:
        results.append(f"<p style='color: red;'>✗ Erreur analyse exercices: {str(e)}</p>")
    
    # 4. Conclusion
    results.append("<h2>4. CONCLUSION</h2>")
    results.append("<p>Diagnostic de base terminé.</p>")
    
    return "<br>".join(results)

"""
    
    # Remplacer l'ancienne route par la nouvelle
    modified_content = re.sub(route_pattern, new_route_code, content, flags=re.DOTALL)
    
    # Écrire le contenu modifié
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"Route de diagnostic simplifiée et sécurisée ajoutée avec succès dans {app_path}!")
    return True

if __name__ == '__main__':
    fix_railway_diagnostic()
