#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db
from models import User, Class

def test_teacher_classes_relations():
    with app.app_context():
        # Récupérer l'enseignant
        teacher = User.query.filter_by(email='mr.zahiri@gmail.com').first()
        
        if not teacher:
            print("ENSEIGNANT NON TROUVE!")
            return
            
        print(f"Enseignant trouve: {teacher.email}")
        print(f"Role: {teacher.role}")
        print(f"Is teacher: {teacher.is_teacher}")
        
        # Tester les différentes relations pour les classes
        print(f"\n=== TEST DES RELATIONS CLASSES ===")
        
        # 1. Relation classes_teaching (utilisée dans le template)
        classes_teaching = teacher.classes_teaching
        print(f"classes_teaching: {len(classes_teaching)} classes")
        for cls in classes_teaching:
            print(f"  - {cls.name} (ID: {cls.id})")
        
        # 2. Vérifier si l'attribut classes_created existe
        try:
            classes_created = teacher.classes_created
            print(f"classes_created: {len(classes_created)} classes")
            for cls in classes_created:
                print(f"  - {cls.name} (ID: {cls.id})")
        except AttributeError:
            print("classes_created n'existe pas - C'est le probleme!")
            print("Le template utilise 'classes_created' mais la relation s'appelle 'classes_teaching'")
        
        # 3. Requête directe pour vérifier
        direct_classes = Class.query.filter_by(teacher_id=teacher.id).all()
        print(f"Requête directe: {len(direct_classes)} classes")
        for cls in direct_classes:
            print(f"  - {cls.name} (ID: {cls.id})")
        
        # 4. Vérifier la structure du modèle User
        print(f"\n=== ATTRIBUTS DU MODÈLE USER ===")
        user_attrs = [attr for attr in dir(teacher) if not attr.startswith('_')]
        class_related_attrs = [attr for attr in user_attrs if 'class' in attr.lower()]
        print(f"Attributs liés aux classes: {class_related_attrs}")

if __name__ == '__main__':
    test_teacher_classes_relations()
