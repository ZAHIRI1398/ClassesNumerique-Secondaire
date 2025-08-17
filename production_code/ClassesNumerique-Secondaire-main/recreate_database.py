#!/usr/bin/env python3
"""
Script pour recréer complètement la base de données avec toutes les tables
"""

import os
import sys
import sqlite3
from datetime import datetime

def recreate_database():
    """Recréer la base de données avec toutes les tables"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
    
    # Créer le dossier instance s'il n'existe pas
    instance_dir = os.path.dirname(db_path)
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
        print(f"Dossier cree: {instance_dir}")
    
    # Supprimer l'ancienne base si elle existe
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Ancienne base supprimee")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Creation de la table User...")
        cursor.execute('''
            CREATE TABLE user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                name VARCHAR(120),
                password_hash VARCHAR(128),
                role VARCHAR(20) NOT NULL DEFAULT 'student',
                school_name VARCHAR(200),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                subscription_status VARCHAR(20) DEFAULT 'pending',
                subscription_type VARCHAR(20),
                subscription_amount FLOAT,
                payment_date DATETIME,
                payment_reference VARCHAR(100),
                payment_session_id VARCHAR(200),
                payment_amount FLOAT,
                approval_date DATETIME,
                approved_by INTEGER,
                subscription_expires DATETIME,
                rejection_reason TEXT,
                notes TEXT,
                FOREIGN KEY (approved_by) REFERENCES user(id)
            )
        ''')
        
        print("Creation de la table Class...")
        cursor.execute('''
            CREATE TABLE class (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                teacher_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES user(id)
            )
        ''')
        
        print("Creation de la table Exercise...")
        cursor.execute('''
            CREATE TABLE exercise (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                exercise_type VARCHAR(50) NOT NULL,
                content TEXT,
                image_path VARCHAR(200),
                teacher_id INTEGER NOT NULL,
                subject VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES user(id)
            )
        ''')
        
        print("Creation de la table ExerciseAttempt...")
        cursor.execute('''
            CREATE TABLE exercise_attempt (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                exercise_id INTEGER NOT NULL,
                score FLOAT,
                completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                answers TEXT,
                FOREIGN KEY (student_id) REFERENCES user(id),
                FOREIGN KEY (exercise_id) REFERENCES exercise(id)
            )
        ''')
        
        print("Creation de la table student_class_association...")
        cursor.execute('''
            CREATE TABLE student_class_association (
                student_id INTEGER NOT NULL,
                class_id INTEGER NOT NULL,
                PRIMARY KEY (student_id, class_id),
                FOREIGN KEY (student_id) REFERENCES user(id),
                FOREIGN KEY (class_id) REFERENCES class(id)
            )
        ''')
        
        conn.commit()
        
        # Vérifier les tables créées
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables creees: {tables}")
        
        # Vérifier la structure de la table User
        cursor.execute("PRAGMA table_info(user)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Colonnes User: {columns}")
        
        if 'school_name' in columns:
            print("✅ Colonne school_name presente!")
        else:
            print("❌ Colonne school_name manquante!")
        
        conn.close()
        print(f"Base de donnees creee: {db_path}")
        return True
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    print("=== RECREATION BASE DE DONNEES ===")
    success = recreate_database()
    
    if success:
        print("=== BASE RECREEE AVEC SUCCES ===")
    else:
        print("=== ECHEC RECREATION BASE ===")
