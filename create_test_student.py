"""
Script pour créer un utilisateur étudiant de test dans la base de données.
"""

import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, Class

def create_test_student():
    """Crée un utilisateur étudiant de test"""
    print("=== CRÉATION D'UN UTILISATEUR ÉTUDIANT DE TEST ===\n")
    
    # Vérifier si l'utilisateur existe déjà
    test_student = User.query.filter_by(username="test_student").first()
    
    if test_student:
        print(f"[INFO] L'utilisateur étudiant de test existe déjà avec l'ID {test_student.id}")
        return test_student
    
    # Créer un nouvel utilisateur étudiant
    new_student = User(
        username="test_student",
        email="test_student@example.com",
        name="Étudiant Test",
        role="student",
        created_at=datetime.utcnow()
    )
    
    # Définir un mot de passe
    new_student.set_password("password123")
    
    try:
        db.session.add(new_student)
        db.session.commit()
        print(f"[OK] Utilisateur étudiant de test créé avec l'ID {new_student.id}")
        return new_student
    except Exception as e:
        db.session.rollback()
        print(f"[ERREUR] Impossible de créer l'utilisateur étudiant de test: {str(e)}")
        return None

def create_test_teacher():
    """Crée un utilisateur enseignant de test si nécessaire"""
    print("\n=== VÉRIFICATION DE L'EXISTENCE D'UN ENSEIGNANT DE TEST ===\n")
    
    # Vérifier si un enseignant existe déjà
    test_teacher = User.query.filter_by(role="teacher").first()
    
    if test_teacher:
        print(f"[INFO] Un enseignant existe déjà avec l'ID {test_teacher.id}")
        return test_teacher
    
    # Créer un nouvel enseignant
    new_teacher = User(
        username="test_teacher",
        email="test_teacher@example.com",
        name="Enseignant Test",
        role="teacher",
        created_at=datetime.utcnow()
    )
    
    # Définir un mot de passe
    new_teacher.set_password("password123")
    
    try:
        db.session.add(new_teacher)
        db.session.commit()
        print(f"[OK] Utilisateur enseignant de test créé avec l'ID {new_teacher.id}")
        return new_teacher
    except Exception as e:
        db.session.rollback()
        print(f"[ERREUR] Impossible de créer l'utilisateur enseignant de test: {str(e)}")
        return None

def create_test_class(teacher_id):
    """Crée une classe de test et y inscrit l'étudiant"""
    print("\n=== CRÉATION D'UNE CLASSE DE TEST ===\n")
    
    # Vérifier si la classe existe déjà
    test_class = Class.query.filter_by(name="Classe de Test").first()
    
    if test_class:
        print(f"[INFO] La classe de test existe déjà avec l'ID {test_class.id}")
        return test_class
    
    # Générer un code d'accès aléatoire
    import random
    import string
    access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Créer une nouvelle classe
    new_class = Class(
        name="Classe de Test",
        description="Classe pour les tests automatisés",
        teacher_id=teacher_id,
        created_at=datetime.utcnow(),
        access_code=access_code
    )
    
    try:
        db.session.add(new_class)
        db.session.commit()
        print(f"[OK] Classe de test créée avec l'ID {new_class.id}")
        return new_class
    except Exception as e:
        db.session.rollback()
        print(f"[ERREUR] Impossible de créer la classe de test: {str(e)}")
        return None

def enroll_student_in_class(student_id, class_id):
    """Inscrit l'étudiant dans la classe de test"""
    print(f"\n=== INSCRIPTION DE L'ÉTUDIANT {student_id} DANS LA CLASSE {class_id} ===\n")
    
    try:
        # Récupérer l'étudiant et la classe
        student = User.query.get(student_id)
        class_obj = Class.query.get(class_id)
        
        if not student or not class_obj:
            print("[ERREUR] Étudiant ou classe non trouvé")
            return False
        
        # Vérifier si l'étudiant est déjà inscrit
        if student.is_enrolled(class_id):
            print(f"[INFO] L'étudiant est déjà inscrit dans cette classe")
            return True
        
        # Inscrire l'étudiant
        student.classes_enrolled.append(class_obj)
        db.session.commit()
        print(f"[OK] Étudiant inscrit avec succès dans la classe")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"[ERREUR] Impossible d'inscrire l'étudiant: {str(e)}")
        return False

def main():
    """Fonction principale"""
    with app.app_context():
        # Créer un enseignant de test si nécessaire
        teacher = create_test_teacher()
        if not teacher:
            print("[ERREUR] Impossible de continuer sans enseignant")
            return
        
        # Créer un étudiant de test
        student = create_test_student()
        if not student:
            print("[ERREUR] Impossible de continuer sans étudiant")
            return
        
        # Créer une classe de test
        class_obj = create_test_class(teacher.id)
        if not class_obj:
            print("[ERREUR] Impossible de continuer sans classe")
            return
        
        # Inscrire l'étudiant dans la classe
        enroll_student_in_class(student.id, class_obj.id)
        
        print("\n=== RÉSUMÉ ===\n")
        print(f"Enseignant: ID {teacher.id}, Nom d'utilisateur: {teacher.username}")
        print(f"Étudiant: ID {student.id}, Nom d'utilisateur: {student.username}")
        print(f"Classe: ID {class_obj.id}, Nom: {class_obj.name}, Code d'accès: {class_obj.access_code}")
        print("\nConfiguration terminée!")

if __name__ == "__main__":
    main()
