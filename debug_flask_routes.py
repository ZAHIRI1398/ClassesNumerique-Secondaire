#!/usr/bin/env python3
"""
Script pour déboguer les routes Flask enregistrées
"""

import os
import sys

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

def debug_flask_routes():
    """Afficher toutes les routes enregistrées dans Flask"""
    
    print("=== DEBUG ROUTES FLASK ===\n")
    
    with app.app_context():
        print("Routes enregistrées dans l'application Flask:")
        print("-" * 50)
        
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': rule.rule
            })
        
        # Trier par endpoint
        routes.sort(key=lambda x: x['rule'])
        
        for route in routes:
            methods = ', '.join([m for m in route['methods'] if m not in ['HEAD', 'OPTIONS']])
            print(f"{route['rule']:<30} [{methods}] -> {route['endpoint']}")
        
        print(f"\nTotal routes: {len(routes)}")
        
        # Chercher spécifiquement test_upload
        test_upload_routes = [r for r in routes if 'test_upload' in r['rule']]
        
        print(f"\nRoutes contenant 'test_upload': {len(test_upload_routes)}")
        for route in test_upload_routes:
            print(f"  {route['rule']} -> {route['endpoint']}")
        
        # Vérifier si la fonction test_upload existe
        print(f"\nVérification de la fonction test_upload:")
        try:
            from app import test_upload
            print(f"  ✓ Fonction test_upload trouvée: {test_upload}")
        except ImportError:
            print(f"  ✗ Fonction test_upload non trouvée dans app.py")
        
        # Vérifier le template
        template_path = "templates/test_upload.html"
        if os.path.exists(template_path):
            print(f"  ✓ Template trouvé: {template_path}")
        else:
            print(f"  ✗ Template manquant: {template_path}")

if __name__ == "__main__":
    debug_flask_routes()
