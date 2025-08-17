#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db
from models import User, Class

def check_user_classes():
    with app.app_context():
        # Récupérer tous les utilisateurs enseignants
        teachers = User.query.filter_by(role='teacher').all()
        
        print("=== ENSEIGNANTS ET LEURS CLASSES ===")
        for teacher in teachers:
            print(f"\nEnseignant: {teacher.email}")
            print(f"Nom: {teacher.name or 'Non renseigné'}")
            print(f"Username: {teacher.username}")
            print(f"Role: {teacher.role}")
            
            # Vérifier les classes créées par cet enseignant
            classes_created = Class.query.filter_by(teacher_id=teacher.id).all()
            print(f"Nombre de classes créées: {len(classes_created)}")
            
            if classes_created:
                print("Classes créées:")
                for cls in classes_created:
                    print(f"  - ID: {cls.id}, Nom: {cls.name}, Code: {cls.access_code}")
            else:
                print("  ❌ AUCUNE CLASSE CRÉÉE - C'est pourquoi le dropdown est vide!")
        
        # Vérifier toutes les classes dans la base
        all_classes = Class.query.all()
        print(f"\n=== TOTAL CLASSES EN BASE ===")
        print(f"Nombre total de classes: {len(all_classes)}")
        
        if all_classes:
            for cls in all_classes:
                teacher = User.query.get(cls.teacher_id)
                print(f"Classe: {cls.name} (ID: {cls.id}) - Enseignant: {teacher.email if teacher else 'INCONNU'}")

if __name__ == '__main__':
    check_user_classes()
