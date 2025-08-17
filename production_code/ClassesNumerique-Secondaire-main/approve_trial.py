#!/usr/bin/env python3
"""
Script pour approuver Mr Nicolas pour un essai gratuit
"""

import sqlite3
import os
from datetime import datetime, timedelta

def approve_nicolas_trial():
    """Approuver Mr Nicolas pour un essai gratuit de 30 jours"""
    
    db_path = os.path.join('instance', 'app.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Trouver Mr Nicolas
        cursor.execute("SELECT id, name, email, subscription_status FROM user WHERE email = 'nicolas@ste.be'")
        user = cursor.fetchone()
        
        if not user:
            print("[ERROR] Mr Nicolas non trouve")
            return False
        
        user_id, name, email, current_status = user
        print(f"=== APPROBATION ESSAI GRATUIT ===")
        print(f"Utilisateur: {name} ({email})")
        print(f"Statut actuel: {current_status}")
        print()
        
        # Calculer dates
        approval_date = datetime.now()
        expiration_date = approval_date + timedelta(days=30)
        
        # Mettre à jour le statut
        sql = """
        UPDATE user SET 
            subscription_status = 'approved',
            subscription_type = 'trial',
            subscription_amount = 0.0,
            approval_date = ?,
            approved_by = 13,
            subscription_expires = ?,
            notes = 'Essai gratuit de 30 jours approuve par admin'
        WHERE id = ?
        """
        
        cursor.execute(sql, (
            approval_date.isoformat(),
            expiration_date.isoformat(),
            user_id
        ))
        
        conn.commit()
        
        print("[SUCCESS] MR NICOLAS APPROUVE POUR ESSAI!")
        print(f"Type: Essai gratuit")
        print(f"Duree: 30 jours")
        print(f"Expire le: {expiration_date.strftime('%d/%m/%Y')}")
        print(f"Statut: {current_status} -> approved")
        print()
        print("Mr Nicolas peut maintenant:")
        print("- Se connecter a la plateforme")
        print("- Creer des exercices")
        print("- Gerer des classes")
        print("- Utiliser toutes les fonctionnalites")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    success = approve_nicolas_trial()
    if success:
        print("\n[INFO] Actualisez la page admin pour voir les changements!")
    else:
        print("\n[ERROR] Approbation echouee")
