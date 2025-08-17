#!/usr/bin/env python3
"""
Script d'audit des utilisateurs et abonnements pour l'interface d'administration
"""

import os
import sys
from datetime import datetime

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import User, db

def audit_users_and_subscriptions():
    """Audit complet des utilisateurs et abonnements"""
    
    with app.app_context():
        print("=== AUDIT UTILISATEURS ET ABONNEMENTS ===")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Statistiques générales
        total_users = User.query.count()
        admins = User.query.filter_by(role='admin').count()
        teachers = User.query.filter_by(role='teacher').count()
        students = User.query.filter_by(role='student').count()
        
        print(f"📊 STATISTIQUES GÉNÉRALES")
        print(f"Total utilisateurs: {total_users}")
        print(f"Administrateurs: {admins}")
        print(f"Enseignants: {teachers}")
        print(f"Étudiants: {students}")
        print()
        
        # Statistiques des abonnements
        pending = User.query.filter_by(subscription_status='pending').count()
        paid = User.query.filter_by(subscription_status='paid').count()
        approved = User.query.filter_by(subscription_status='approved').count()
        rejected = User.query.filter_by(subscription_status='rejected').count()
        suspended = User.query.filter_by(subscription_status='suspended').count()
        
        print(f"💳 STATUTS D'ABONNEMENTS")
        print(f"En attente (pending): {pending}")
        print(f"Payé (paid): {paid}")
        print(f"Approuvé (approved): {approved}")
        print(f"Rejeté (rejected): {rejected}")
        print(f"Suspendu (suspended): {suspended}")
        print()
        
        # Types d'abonnements
        teacher_subs = User.query.filter_by(subscription_type='teacher').count()
        school_subs = User.query.filter_by(subscription_type='school').count()
        no_sub_type = User.query.filter(User.subscription_type.is_(None)).count()
        
        print(f"📋 TYPES D'ABONNEMENTS")
        print(f"Enseignant: {teacher_subs}")
        print(f"École: {school_subs}")
        print(f"Non défini: {no_sub_type}")
        print()
        
        # Utilisateurs nécessitant une attention admin
        print(f"⚠️  UTILISATEURS NÉCESSITANT UNE ATTENTION")
        
        # Paiements en attente de validation
        paid_pending_approval = User.query.filter_by(subscription_status='paid').all()
        if paid_pending_approval:
            print(f"Paiements à valider ({len(paid_pending_approval)}):")
            for user in paid_pending_approval:
                print(f"  - {user.email} ({user.name or 'Sans nom'}) - {user.subscription_type} - {user.payment_amount}€")
        else:
            print("Aucun paiement en attente de validation")
        print()
        
        # Administrateurs existants
        admin_users = User.query.filter_by(role='admin').all()
        print(f"👑 ADMINISTRATEURS ({len(admin_users)})")
        if admin_users:
            for admin in admin_users:
                print(f"  - {admin.email} ({admin.name or 'Sans nom'}) - Créé: {admin.created_at.strftime('%Y-%m-%d')}")
        else:
            print("⚠️  AUCUN ADMINISTRATEUR TROUVÉ!")
        print()
        
        # Revenus
        total_revenue = db.session.query(db.func.sum(User.payment_amount)).filter(
            User.payment_amount.isnot(None)
        ).scalar() or 0
        
        print(f"💰 REVENUS")
        print(f"Revenus totaux: {total_revenue}€")
        print()
        
        print("=== FIN DE L'AUDIT ===")

if __name__ == '__main__':
    audit_users_and_subscriptions()
