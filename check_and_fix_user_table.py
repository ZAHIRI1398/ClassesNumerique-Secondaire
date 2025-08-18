import os
import sqlite3
from sqlalchemy import create_engine, inspect, text
from config import DevelopmentConfig

def check_and_fix_user_table():
    """
    Vérifie si la colonne school_id existe dans la table user.
    Si elle n'existe pas, l'ajoute à la table.
    """
    # Récupérer l'URI de la base de données depuis la configuration
    db_uri = DevelopmentConfig.SQLALCHEMY_DATABASE_URI
    
    if db_uri.startswith('sqlite:///'):
        # Extraire le chemin du fichier SQLite
        db_path = db_uri.replace('sqlite:///', '')
        print(f"Vérification de la base de données SQLite: {db_path}")
        
        # Vérifier si le fichier existe
        if not os.path.exists(db_path):
            print(f"Erreur: Le fichier de base de données {db_path} n'existe pas.")
            return False
        
        # Se connecter à la base de données SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si la colonne school_id existe dans la table user
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'school_id' not in column_names:
            print("La colonne school_id n'existe pas dans la table user. Ajout en cours...")
            
            # Ajouter la colonne school_id à la table user
            try:
                cursor.execute("ALTER TABLE user ADD COLUMN school_id INTEGER")
                conn.commit()
                print("Colonne school_id ajoutée avec succès à la table user.")
                
                # Vérifier si la table school existe
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='school'")
                if not cursor.fetchone():
                    print("La table school n'existe pas. Création en cours...")
                    cursor.execute("""
                    CREATE TABLE school (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(200) NOT NULL,
                        address VARCHAR(255),
                        postal_code VARCHAR(20),
                        city VARCHAR(100),
                        country VARCHAR(100),
                        created_at DATETIME,
                        created_by INTEGER,
                        FOREIGN KEY(created_by) REFERENCES user(id)
                    )
                    """)
                    conn.commit()
                    print("Table school créée avec succès.")
                
                # Ajouter la contrainte de clé étrangère
                # Note: SQLite ne permet pas d'ajouter des contraintes de clé étrangère après la création de la table
                # Nous devons donc créer une nouvelle table, copier les données, puis renommer
                print("Ajout de la contrainte de clé étrangère...")
                cursor.execute("PRAGMA foreign_keys=OFF")
                
                # Créer une nouvelle table user avec la contrainte
                cursor.execute("""
                CREATE TABLE user_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(64),
                    email VARCHAR(120),
                    name VARCHAR(120),
                    password_hash VARCHAR(128),
                    role VARCHAR(20),
                    school_name VARCHAR(100),
                    school_id INTEGER,
                    created_at DATETIME,
                    subscription_status VARCHAR(20),
                    subscription_type VARCHAR(20),
                    subscription_amount INTEGER,
                    payment_date DATETIME,
                    payment_reference VARCHAR(100),
                    payment_session_id VARCHAR(100),
                    payment_amount INTEGER,
                    approval_date DATETIME,
                    approved_by INTEGER,
                    subscription_expires DATETIME,
                    rejection_reason TEXT,
                    notes TEXT,
                    FOREIGN KEY(school_id) REFERENCES school(id)
                )
                """)
                
                # Copier les données de l'ancienne table vers la nouvelle
                cursor.execute("""
                INSERT INTO user_new (
                    id, username, email, name, password_hash, role, school_name,
                    created_at, subscription_status, subscription_type, subscription_amount,
                    payment_date, payment_reference, payment_session_id, payment_amount,
                    approval_date, approved_by, subscription_expires, rejection_reason, notes
                )
                SELECT
                    id, username, email, name, password_hash, role, school_name,
                    created_at, subscription_status, subscription_type, subscription_amount,
                    payment_date, payment_reference, payment_session_id, payment_amount,
                    approval_date, approved_by, subscription_expires, rejection_reason, notes
                FROM user
                """)
                
                # Supprimer l'ancienne table et renommer la nouvelle
                cursor.execute("DROP TABLE user")
                cursor.execute("ALTER TABLE user_new RENAME TO user")
                
                # Réactiver les clés étrangères
                cursor.execute("PRAGMA foreign_keys=ON")
                
                conn.commit()
                print("Contrainte de clé étrangère ajoutée avec succès.")
                
            except Exception as e:
                conn.rollback()
                print(f"Erreur lors de la modification de la table user: {e}")
                return False
        else:
            print("La colonne school_id existe déjà dans la table user.")
        
        conn.close()
        return True
    else:
        print(f"Base de données non SQLite: {db_uri}")
        # Pour les bases de données non SQLite, utilisez SQLAlchemy
        try:
            engine = create_engine(db_uri)
            inspector = inspect(engine)
            
            if 'user' in inspector.get_table_names():
                columns = [column['name'] for column in inspector.get_columns('user')]
                
                if 'school_id' not in columns:
                    print("La colonne school_id n'existe pas dans la table user. Ajout en cours...")
                    with engine.connect() as connection:
                        connection.execute(text("ALTER TABLE user ADD COLUMN school_id INTEGER"))
                        print("Colonne school_id ajoutée avec succès à la table user.")
                else:
                    print("La colonne school_id existe déjà dans la table user.")
            else:
                print("La table user n'existe pas dans la base de données.")
                return False
            
            return True
        except Exception as e:
            print(f"Erreur lors de la vérification/modification de la table user: {e}")
            return False

if __name__ == "__main__":
    if check_and_fix_user_table():
        print("Vérification et correction de la structure de la table user terminées avec succès.")
    else:
        print("Échec de la vérification et correction de la structure de la table user.")
