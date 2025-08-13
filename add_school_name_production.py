#!/usr/bin/env python3
"""
Script pour ajouter la colonne school_name en production Railway
SANS perdre les données existantes
"""

import os
import psycopg2
from urllib.parse import urlparse

def add_school_name_column_production():
    """
    Ajoute la colonne school_name à la table user en production
    sans perdre les données existantes
    """
    
    # URL de la base PostgreSQL Railway (à récupérer depuis les variables d'environnement)
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ Variable DATABASE_URL non trouvée")
        print("ℹ️  Vous devez définir DATABASE_URL avec l'URL PostgreSQL de Railway")
        return False
    
    try:
        # Parser l'URL de la base de données
        url = urlparse(database_url)
        
        # Connexion à PostgreSQL
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port,
            user=url.username,
            password=url.password,
            database=url.path[1:]  # Enlever le '/' du début
        )
        
        cursor = conn.cursor()
        
        print("✅ Connexion à PostgreSQL Railway réussie")
        
        # Vérifier si la colonne existe déjà
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='user' AND column_name='school_name';
        """)
        
        existing_column = cursor.fetchone()
        
        if existing_column:
            print("✅ La colonne school_name existe déjà en production")
            return True
        
        # Ajouter la colonne school_name
        print("🔄 Ajout de la colonne school_name...")
        cursor.execute("""
            ALTER TABLE "user" 
            ADD COLUMN school_name VARCHAR(255);
        """)
        
        # Valider les changements
        conn.commit()
        print("✅ Colonne school_name ajoutée avec succès !")
        
        # Vérifier le nombre d'utilisateurs existants
        cursor.execute('SELECT COUNT(*) FROM "user";')
        user_count = cursor.fetchone()[0]
        print(f"ℹ️  Nombre d'utilisateurs existants préservés: {user_count}")
        
        # Vérifier le nombre d'exercices existants
        cursor.execute('SELECT COUNT(*) FROM exercise;')
        exercise_count = cursor.fetchone()[0]
        print(f"ℹ️  Nombre d'exercices existants préservés: {exercise_count}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout de la colonne: {e}")
        return False

def get_railway_database_url():
    """
    Aide pour récupérer l'URL de la base Railway
    """
    print("🔍 Pour récupérer l'URL de la base Railway:")
    print("1. Aller sur railway.app")
    print("2. Ouvrir votre projet")
    print("3. Onglet 'Variables'")
    print("4. Copier la valeur de DATABASE_URL")
    print("5. Exécuter: set DATABASE_URL=postgresql://...")
    print("")
    print("Ou utiliser directement:")
    print("python add_school_name_production.py")

if __name__ == '__main__':
    print("🚄 Migration production Railway - Ajout colonne school_name")
    print("=" * 60)
    
    if add_school_name_column_production():
        print("🎉 Migration réussie ! Aucune donnée perdue.")
        print("✅ Vous pouvez maintenant déployer le code mis à jour")
    else:
        print("❌ Migration échouée")
        print("")
        get_railway_database_url()
