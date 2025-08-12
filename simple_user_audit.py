#!/usr/bin/env python3
"""
Audit simple des utilisateurs sans emojis pour éviter les problèmes d'encodage
"""

import sqlite3
import os
from datetime import datetime

def simple_audit():
    """Audit simple de la base de données"""
    
    db_path = os.path.join('instance', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"[ERROR] Base de donnees non trouvee: {db_path}")
        return
    
    print("=== AUDIT SIMPLE UTILISATEURS ===")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Statistiques générales
        cursor.execute("SELECT COUNT(*) FROM user")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user WHERE role = 'admin'")
        admins = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user WHERE role = 'teacher'")
        teachers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user WHERE role = 'student'")
        students = cursor.fetchone()[0]
        
        print("STATISTIQUES GENERALES:")
        print(f"  Total utilisateurs: {total_users}")
        print(f"  Administrateurs: {admins}")
        print(f"  Enseignants: {teachers}")
        print(f"  Etudiants: {students}")
        print()
        
        # Abonnements
        cursor.execute("SELECT COUNT(*) FROM user WHERE subscription_status = 'pending'")
        pending = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user WHERE subscription_status = 'paid'")
        paid = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user WHERE subscription_status = 'approved'")
        approved = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user WHERE subscription_status = 'rejected'")
        rejected = cursor.fetchone()[0]
        
        print("STATUTS ABONNEMENTS:")
        print(f"  En attente: {pending}")
        print(f"  Paye: {paid}")
        print(f"  Approuve: {approved}")
        print(f"  Rejete: {rejected}")
        print()
        
        # Administrateurs
        cursor.execute("SELECT email, name, created_at FROM user WHERE role = 'admin'")
        admin_users = cursor.fetchall()
        
        print("ADMINISTRATEURS:")
        if admin_users:
            for email, name, created_at in admin_users:
                print(f"  - {email} ({name or 'Sans nom'}) - Cree: {created_at[:10]}")
        else:
            print("  Aucun administrateur trouve!")
        print()
        
        # Paiements en attente
        cursor.execute("SELECT email, name, subscription_type, payment_amount FROM user WHERE subscription_status = 'paid'")
        paid_users = cursor.fetchall()
        
        print("PAIEMENTS A VALIDER:")
        if paid_users:
            for email, name, sub_type, amount in paid_users:
                print(f"  - {email} ({name or 'Sans nom'}) - {sub_type} - {amount}€")
        else:
            print("  Aucun paiement en attente")
        print()
        
        # Revenus
        cursor.execute("SELECT SUM(payment_amount) FROM user WHERE payment_amount IS NOT NULL")
        total_revenue = cursor.fetchone()[0] or 0
        
        print(f"REVENUS TOTAUX: {total_revenue}€")
        print()
        
        print("=== FIN AUDIT ===")
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'audit: {e}")
    
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    simple_audit()
