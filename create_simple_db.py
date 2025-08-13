#!/usr/bin/env python3
"""
Script simple pour créer la base de données avec SQLite pur
"""

import sqlite3
import os

def create_simple_database():
    """Créer la base de données avec SQLite pur"""
    
    # Créer le dossier instance dans le répertoire courant
    instance_dir = 'instance'
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
        print(f"Dossier {instance_dir} cree")
    
    db_path = os.path.join(instance_dir, 'database.db')
    
    # Supprimer l'ancienne base si elle existe
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Ancienne base supprimee")
    
    try:
        # Créer la nouvelle base
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Creation table User avec school_name...")
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
        
        print("Creation autres tables...")
        
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
        
        # Vérifier la structure
        cursor.execute("PRAGMA table_info(user)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print(f"Colonnes User: {columns}")
        
        if 'school_name' in columns:
            print("OK: Colonne school_name presente!")
        else:
            print("ERREUR: Colonne school_name manquante!")
            return False
        
        # Test simple
        cursor.execute("INSERT INTO user (username, email, name, role, school_name) VALUES (?, ?, ?, ?, ?)",
                      ('test', 'test@example.com', 'Test', 'teacher', 'Ecole Test'))
        conn.commit()
        
        cursor.execute("SELECT school_name FROM user WHERE email = ?", ('test@example.com',))
        result = cursor.fetchone()
        
        if result and result[0] == 'Ecole Test':
            print("OK: Test lecture/ecriture reussi!")
            
            # Nettoyer le test
            cursor.execute("DELETE FROM user WHERE email = ?", ('test@example.com',))
            conn.commit()
        else:
            print("ERREUR: Test lecture/ecriture echoue!")
            return False
        
        conn.close()
        
        print(f"Base creee: {os.path.abspath(db_path)}")
        return True
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    print("=== CREATION BASE SIMPLE ===")
    success = create_simple_database()
    
    if success:
        print("=== BASE CREEE AVEC SUCCES ===")
    else:
        print("=== ECHEC CREATION ===")
