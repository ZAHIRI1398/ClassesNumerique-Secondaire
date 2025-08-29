"""
Script d'initialisation d'une base de données propre pour tester le système d'images
"""

import os
import sqlite3
import shutil
from datetime import datetime
from werkzeug.security import generate_password_hash

def backup_current_database():
    """Sauvegarde la base de données actuelle"""
    db_files = ['instance/app.db', 'instance/classe_numerique.db']
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    for db_file in db_files:
        if os.path.exists(db_file):
            backup_name = f"{db_file}.backup_{timestamp}"
            shutil.copy2(db_file, backup_name)
            print(f"✅ Sauvegarde créée: {backup_name}")

def create_clean_database():
    """Crée une base de données propre avec les tables nécessaires"""
    
    # Supprimer l'ancienne base si elle existe
    if os.path.exists('instance/app.db'):
        os.remove('instance/app.db')
    
    # Créer le dossier instance s'il n'existe pas
    os.makedirs('instance', exist_ok=True)
    
    # Connexion à la nouvelle base
    conn = sqlite3.connect('instance/app.db')
    cursor = conn.cursor()
    
    # Créer les tables principales
    cursor.execute('''
        CREATE TABLE user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            name VARCHAR(120) NOT NULL,
            password_hash VARCHAR(128) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'student',
            school_name VARCHAR(200),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            subscription_status VARCHAR(20) DEFAULT 'active',
            subscription_type VARCHAR(20) DEFAULT 'free',
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
            school_id INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE class (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            teacher_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            access_code VARCHAR(6) UNIQUE NOT NULL,
            FOREIGN KEY (teacher_id) REFERENCES user (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE exercise (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            exercise_type VARCHAR(50) NOT NULL,
            content TEXT,
            subject VARCHAR(50),
            teacher_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            max_attempts INTEGER DEFAULT 1,
            image_path VARCHAR(255),
            FOREIGN KEY (teacher_id) REFERENCES user (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE course (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            content TEXT,
            class_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (class_id) REFERENCES class (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE student_class (
            student_id INTEGER,
            class_id INTEGER,
            PRIMARY KEY (student_id, class_id),
            FOREIGN KEY (student_id) REFERENCES user (id),
            FOREIGN KEY (class_id) REFERENCES class (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE course_exercise (
            course_id INTEGER,
            exercise_id INTEGER,
            PRIMARY KEY (course_id, exercise_id),
            FOREIGN KEY (course_id) REFERENCES course (id),
            FOREIGN KEY (exercise_id) REFERENCES exercise (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE exercise_attempt (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            exercise_id INTEGER NOT NULL,
            course_id INTEGER,
            score FLOAT,
            answers TEXT,
            feedback TEXT,
            completed BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES user (id),
            FOREIGN KEY (exercise_id) REFERENCES exercise (id),
            FOREIGN KEY (course_id) REFERENCES course (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE course_file (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename VARCHAR(255) NOT NULL,
            original_filename VARCHAR(255) NOT NULL,
            file_type VARCHAR(50),
            file_size INTEGER,
            course_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES course (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE school (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            address VARCHAR(255),
            postal_code VARCHAR(20),
            city VARCHAR(100),
            country VARCHAR(100) DEFAULT 'France',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES user (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE alembic_version (
            version_num VARCHAR(32) NOT NULL,
            CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
        )
    ''')
    
    # Insérer la version Alembic
    cursor.execute("INSERT INTO alembic_version (version_num) VALUES ('f7755682b0ec')")
    
    conn.commit()
    print("✅ Tables créées avec succès")
    
    return conn, cursor

def create_test_users(cursor):
    """Crée des utilisateurs de test"""
    
    # Enseignant de test
    teacher_password = generate_password_hash('teacher123')
    cursor.execute('''
        INSERT INTO user (username, email, name, password_hash, role, school_name)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('teacher', 'teacher@test.com', 'Professeur Test', teacher_password, 'teacher', 'École Test'))
    
    # Élève de test
    student_password = generate_password_hash('student123')
    cursor.execute('''
        INSERT INTO user (username, email, name, password_hash, role, school_name)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('student', 'student@test.com', 'Élève Test', student_password, 'student', 'École Test'))
    
    print("✅ Utilisateurs de test créés:")
    print("   - Enseignant: teacher@test.com / teacher123")
    print("   - Élève: student@test.com / student123")

def create_test_class(cursor):
    """Crée une classe de test"""
    cursor.execute('''
        INSERT INTO class (name, description, teacher_id, access_code)
        VALUES (?, ?, ?, ?)
    ''', ('Classe Test', 'Classe pour tester le système d\'images', 1, 'TEST01'))
    
    # Associer l'élève à la classe
    cursor.execute('''
        INSERT INTO student_class (student_id, class_id)
        VALUES (?, ?)
    ''', (2, 1))
    
    print("✅ Classe de test créée: Classe Test (code: TEST01)")

def clean_upload_directories():
    """Nettoie et recrée la structure des dossiers d'upload"""
    upload_base = 'static/uploads'
    
    # Dossiers par type d'exercice
    exercise_folders = [
        'qcm', 'fill_in_blanks', 'flashcards', 'pairs', 
        'image_labeling', 'legend', 'word_placement', 
        'drag_and_drop', 'general'
    ]
    
    # Créer la structure propre
    for folder in exercise_folders:
        folder_path = os.path.join(upload_base, folder)
        os.makedirs(folder_path, exist_ok=True)
        
        # Créer un fichier .gitkeep pour préserver la structure
        gitkeep_path = os.path.join(folder_path, '.gitkeep')
        with open(gitkeep_path, 'w') as f:
            f.write('')
    
    print("✅ Structure des dossiers d'upload créée:")
    for folder in exercise_folders:
        print(f"   - static/uploads/{folder}/")

def main():
    """Fonction principale d'initialisation"""
    print("=== Initialisation d'une base de données propre ===\n")
    
    # 1. Sauvegarder l'ancienne base
    print("1. Sauvegarde de la base actuelle...")
    backup_current_database()
    print()
    
    # 2. Créer une nouvelle base propre
    print("2. Création d'une nouvelle base de données...")
    conn, cursor = create_clean_database()
    print()
    
    # 3. Créer des utilisateurs de test
    print("3. Création des utilisateurs de test...")
    create_test_users(cursor)
    print()
    
    # 4. Créer une classe de test
    print("4. Création d'une classe de test...")
    create_test_class(cursor)
    print()
    
    # 5. Nettoyer les dossiers d'upload
    print("5. Nettoyage des dossiers d'upload...")
    clean_upload_directories()
    print()
    
    # Finaliser
    conn.commit()
    conn.close()
    
    print("🎉 Initialisation terminée avec succès !")
    print("\nVous pouvez maintenant:")
    print("1. Démarrer l'application: python app.py")
    print("2. Vous connecter avec: teacher@test.com / teacher123")
    print("3. Créer des exercices avec images pour tester le système")
    print("\nLe nouveau système d'images organisera automatiquement")
    print("vos fichiers dans les bons dossiers par type d'exercice.")

if __name__ == "__main__":
    main()
