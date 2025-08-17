#!/usr/bin/env python3
"""
Script pour vérifier les tables disponibles dans la base de données.
"""
import os
import sqlite3
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def connect_to_db():
    """Connexion à la base de données."""
    try:
        # Utiliser le chemin absolu vers la base de données
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'site.db')
        logger.info(f"Tentative de connexion à la base de données: {db_path}")
        
        # Vérifier si le fichier existe
        if not os.path.exists(db_path):
            logger.error(f"❌ Fichier de base de données non trouvé: {db_path}")
            return None
            
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Erreur de connexion à la base de données: {str(e)}")
        return None

def list_tables():
    """Liste toutes les tables dans la base de données."""
    conn = connect_to_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        logger.info(f"Tables trouvées dans la base de données ({len(tables)}):")
        for i, table in enumerate(tables, 1):
            logger.info(f"{i}. {table['name']}")
        
        conn.close()
    except Exception as e:
        logger.error(f"Erreur lors de la liste des tables: {str(e)}")
        if conn:
            conn.close()

def check_exercise_table():
    """Vérifie si la table 'exercise' existe et affiche sa structure."""
    conn = connect_to_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        # Vérifier si la table existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exercise';")
        table = cursor.fetchone()
        
        if table:
            logger.info("✅ La table 'exercise' existe.")
            
            # Afficher la structure de la table
            cursor.execute("PRAGMA table_info(exercise);")
            columns = cursor.fetchall()
            
            logger.info("Structure de la table 'exercise':")
            for col in columns:
                logger.info(f"- {col['name']} ({col['type']})")
            
            # Compter les enregistrements
            cursor.execute("SELECT COUNT(*) as count FROM exercise;")
            count = cursor.fetchone()['count']
            logger.info(f"Nombre d'exercices dans la table: {count}")
            
            # Afficher les premiers exercices
            cursor.execute("SELECT id, title, exercise_type FROM exercise LIMIT 5;")
            exercises = cursor.fetchall()
            
            logger.info("Premiers exercices:")
            for ex in exercises:
                logger.info(f"- ID: {ex['id']}, Titre: {ex['title']}, Type: {ex['exercise_type']}")
        else:
            logger.error("❌ La table 'exercise' n'existe pas.")
        
        conn.close()
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la table 'exercise': {str(e)}")
        if conn:
            conn.close()

def check_exercises_table():
    """Vérifie si la table 'exercises' existe (au pluriel) et affiche sa structure."""
    conn = connect_to_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        # Vérifier si la table existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exercises';")
        table = cursor.fetchone()
        
        if table:
            logger.info("✅ La table 'exercises' existe.")
            
            # Afficher la structure de la table
            cursor.execute("PRAGMA table_info(exercises);")
            columns = cursor.fetchall()
            
            logger.info("Structure de la table 'exercises':")
            for col in columns:
                logger.info(f"- {col['name']} ({col['type']})")
            
            # Compter les enregistrements
            cursor.execute("SELECT COUNT(*) as count FROM exercises;")
            count = cursor.fetchone()['count']
            logger.info(f"Nombre d'exercices dans la table: {count}")
            
            # Afficher les premiers exercices
            cursor.execute("SELECT id, title, exercise_type FROM exercises LIMIT 5;")
            exercises = cursor.fetchall()
            
            logger.info("Premiers exercices:")
            for ex in exercises:
                logger.info(f"- ID: {ex['id']}, Titre: {ex['title']}, Type: {ex['exercise_type']}")
        else:
            logger.error("❌ La table 'exercises' n'existe pas.")
        
        conn.close()
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la table 'exercises': {str(e)}")
        if conn:
            conn.close()

def main():
    """Fonction principale."""
    logger.info("=== VÉRIFICATION DE LA BASE DE DONNÉES ===")
    
    # Lister toutes les tables
    logger.info("\n=== LISTE DES TABLES ===")
    list_tables()
    
    # Vérifier la table 'exercise'
    logger.info("\n=== VÉRIFICATION DE LA TABLE 'exercise' ===")
    check_exercise_table()
    
    # Vérifier la table 'exercises' (au pluriel)
    logger.info("\n=== VÉRIFICATION DE LA TABLE 'exercises' ===")
    check_exercises_table()

if __name__ == "__main__":
    main()
