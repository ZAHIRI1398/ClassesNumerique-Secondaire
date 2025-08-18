import os
import sys
import sqlite3
from datetime import datetime

def test_school_database():
    """
    Vérifie la structure de la base de données et teste l'insertion d'une école.
    """
    # Chemin vers la base de données SQLite
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'classe_numerique.db')
    
    # Chemin alternatif si le premier n'existe pas
    alt_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"[INFO] Base de données non trouvée à l'emplacement: {db_path}")
        if os.path.exists(alt_db_path):
            print(f"[INFO] Utilisation de la base de données alternative: {alt_db_path}")
            db_path = alt_db_path
        else:
            print(f"[ERREUR] Aucune base de données trouvée")
            return
    
    print(f"[INFO] Base de données trouvée: {db_path}")
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si la table school existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='school';")
        if cursor.fetchone():
            print("[OK] Table 'school' trouvée dans la base de données.")
        else:
            print("[ERREUR] Table 'school' non trouvée dans la base de données.")
            return
        
        # Vérifier la structure de la table school
        cursor.execute("PRAGMA table_info(school);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print("\nStructure de la table 'school':")
        print("-" * 50)
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
        print("-" * 50)
        
        # Vérifier si la colonne school_id existe dans la table user
        cursor.execute("PRAGMA table_info(user);")
        user_columns = cursor.fetchall()
        user_column_names = [col[1] for col in user_columns]
        
        if 'school_id' in user_column_names:
            print("[OK] Colonne 'school_id' trouvée dans la table 'user'.")
        else:
            print("[ERREUR] Colonne 'school_id' non trouvée dans la table 'user'.")
        
        # Afficher les écoles existantes
        cursor.execute("SELECT * FROM school;")
        schools = cursor.fetchall()
        
        print("\nÉcoles existantes:")
        print("-" * 50)
        if schools:
            for school in schools:
                print(f"ID: {school[0]}, Nom: {school[1]}, Adresse: {school[2]}, Code postal: {school[3]}, Ville: {school[4]}")
        else:
            print("Aucune école n'est enregistrée dans la base de données.")
        print("-" * 50)
        
        # Tester l'insertion d'une école (optionnel, décommenter pour tester)
        """
        test_school_name = f"École de Test {datetime.now().strftime('%Y%m%d%H%M%S')}"
        cursor.execute(
            "INSERT INTO school (name, address, postal_code, city, country, created_at, created_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (test_school_name, "123 Rue de Test", "75000", "Paris", "France", datetime.now(), 1)
        )
        conn.commit()
        print(f"[INFO] École de test '{test_school_name}' insérée avec succès.")
        """
        
        # Afficher les utilisateurs avec leur école associée
        cursor.execute("""
            SELECT u.id, u.name, u.email, u.role, s.name as school_name
            FROM user u
            LEFT JOIN school s ON u.school_id = s.id
            LIMIT 10;
        """)
        users = cursor.fetchall()
        
        print("\nUtilisateurs avec école associée (10 premiers):")
        print("-" * 50)
        if users:
            for user in users:
                print(f"ID: {user[0]}, Nom: {user[1]}, Email: {user[2]}, Rôle: {user[3]}, École: {user[4] or 'Non associé'}")
        else:
            print("Aucun utilisateur trouvé dans la base de données.")
        print("-" * 50)
        
    except sqlite3.Error as e:
        print(f"[ERREUR] Erreur SQLite: {str(e)}")
    except Exception as e:
        print(f"[ERREUR] Erreur générale: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    test_school_database()
