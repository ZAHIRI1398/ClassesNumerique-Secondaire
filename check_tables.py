#!/usr/bin/env python3
import sqlite3

def check_tables():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # Lister toutes les tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("=== TABLES DISPONIBLES ===")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Vérifier si Exercise existe (avec majuscule)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%xercise%'")
    exercise_tables = cursor.fetchall()
    
    print("\n=== TABLES EXERCISE ===")
    for table in exercise_tables:
        print(f"  - {table[0]}")
        
        # Afficher la structure de la table
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        print(f"    Colonnes:")
        for col in columns:
            print(f"      {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == '__main__':
    check_tables()
