#!/usr/bin/env python3
# Script pour lister toutes les routes Flask disponibles

import sys
sys.path.append('.')

from app import app

print("=== TOUTES LES ROUTES FLASK DISPONIBLES ===")
print()

for rule in app.url_map.iter_rules():
    methods = ','.join(rule.methods)
    print(f"Route: {rule.rule}")
    print(f"Methods: {methods}")
    print(f"Endpoint: {rule.endpoint}")
    print("---")

print()
print("=== RECHERCHE DE LA ROUTE handle_exercise_answer ===")

# Rechercher spécifiquement notre route
found_answer_route = False
for rule in app.url_map.iter_rules():
    if 'answer' in rule.rule and 'exercise' in rule.rule:
        print(f"TROUVÉ: {rule.rule} -> {rule.endpoint} ({','.join(rule.methods)})")
        found_answer_route = True

if not found_answer_route:
    print("❌ AUCUNE ROUTE /exercise/<id>/answer TROUVÉE !")
else:
    print("✅ Route /exercise/<id>/answer trouvée")

print()
print("=== RECHERCHE DE ROUTES SIMILAIRES ===")

for rule in app.url_map.iter_rules():
    if 'exercise' in rule.rule and 'POST' in rule.methods:
        print(f"Route POST avec 'exercise': {rule.rule} -> {rule.endpoint}")
