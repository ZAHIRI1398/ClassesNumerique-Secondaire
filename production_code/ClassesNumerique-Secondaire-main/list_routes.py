#!/usr/bin/env python3
"""
Script pour lister toutes les routes Flask enregistrées
"""

from app import app

def list_routes():
    """Liste toutes les routes enregistrées dans l'application Flask"""
    print("=== ROUTES FLASK ENREGISTRÉES ===")
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        print(f"{rule.rule:<50} {methods:<20} {rule.endpoint}")
    print("=" * 80)

if __name__ == '__main__':
    with app.app_context():
        list_routes()
