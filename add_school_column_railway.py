#!/usr/bin/env python3
"""
Script pour ajouter la colonne school_name à la base PostgreSQL Railway
"""

import os
import psycopg2
from urllib.parse import urlparse

def add_school_column():
    """Ajoute la colonne school_name à la table user en production Railway"""
    
    # URL de connexion Railway PostgreSQL
    DATABASE_URL = "postgresql://postgres:SJqjLlGjIzLYjOuaKRcTmDqrgkMpcGJO@postgres.railway.internal:5432/railway"
    
    # IMPORTANT: Remplacez DATABASE_URL par l'URL réelle de votre base Railway
    # Vous pouvez la trouver dans Railway > PostgreSQL > Variables > DATABASE_URL
    
    print("Connexion a la base PostgreSQL Railway...")
    
    try:
        # Connexion à la base
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("Connexion reussie !")
        
        # Vérifier si la colonne existe déjà
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user' AND column_name = 'school_name'
        """)
        
        if cursor.fetchone():
            print("La colonne school_name existe deja !")
            return
        
        # Ajouter la colonne school_name
        print("Ajout de la colonne school_name...")
        cursor.execute('ALTER TABLE "user" ADD COLUMN school_name VARCHAR(255);')
        
        # Confirmer les changements
        conn.commit()
        
        print("Colonne school_name ajoutee avec succes !")
        print("Votre application Railway devrait maintenant fonctionner !")
        
    except Exception as e:
        print(f"Erreur : {e}")
        print("\nSolutions :")
        print("1. Verifiez l'URL de connexion DATABASE_URL")
        print("2. Verifiez que psycopg2 est installe : pip install psycopg2-binary")
        print("3. Verifiez les droits d'acces a la base Railway")
        
    finally:
        if 'conn' in locals():
            conn.close()
            print("Connexion fermee")

if __name__ == "__main__":
    print("Script d'ajout de colonne school_name pour Railway")
    print("=" * 50)
    
    # Vérifier si psycopg2 est installé
    try:
        import psycopg2
    except ImportError:
        print("psycopg2 n'est pas installe")
        print("Installez-le avec : pip install psycopg2-binary")
        exit(1)
    
    add_school_column()
