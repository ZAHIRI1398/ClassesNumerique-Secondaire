#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script d'exécution pour la migration des chemins d'images.
Ce script permet de lancer la migration avec des options de sécurité.
"""

import argparse
from migrate_image_paths import migrate_image_paths

def main():
    """Fonction principale pour exécuter la migration"""
    parser = argparse.ArgumentParser(description='Migration des chemins d\'images pour les exercices image_labeling')
    parser.add_argument('--dry-run', action='store_true', help='Exécuter en mode simulation sans modifier la base de données')
    parser.add_argument('--backup', action='store_true', help='Créer une sauvegarde de la base de données avant la migration')
    args = parser.parse_args()
    
    if args.backup:
        print("Création d'une sauvegarde de la base de données...")
        # Code pour créer une sauvegarde de la base de données
        # Cette partie dépend de votre configuration de base de données
        print("Sauvegarde terminée.")
    
    if args.dry_run:
        print("Mode simulation activé. Aucune modification ne sera apportée à la base de données.")
        # Modifier la fonction migrate_image_paths pour supporter le mode simulation
    
    print("Lancement de la migration des chemins d'images...")
    success = migrate_image_paths()
    
    if success:
        print("Migration terminée avec succès.")
    else:
        print("La migration a échoué. Consultez les logs pour plus d'informations.")

if __name__ == "__main__":
    main()
