import os
import sqlite3

# Tester l'accès direct à la base
db_path = 'instance/app.db'
print(f'Chemin: {os.path.abspath(db_path)}')
print(f'Existe: {os.path.exists(db_path)}')
print(f'Taille: {os.path.getsize(db_path)} bytes')
print(f'Permissions lecture: {os.access(db_path, os.R_OK)}')
print(f'Permissions ecriture: {os.access(db_path, os.W_OK)}')

# Test de connexion SQLite
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = cursor.fetchall()
    print(f'Tables: {[t[0] for t in tables]}')
    conn.close()
    print('Connexion SQLite: OK')
except Exception as e:
    print(f'Erreur SQLite: {e}')

# Test avec chemin absolu
abs_path = os.path.abspath(db_path)
print(f'\nTest avec chemin absolu: {abs_path}')
try:
    conn = sqlite3.connect(abs_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM exercise')
    count = cursor.fetchone()[0]
    print(f'Nombre d\'exercices: {count}')
    conn.close()
    print('Connexion avec chemin absolu: OK')
except Exception as e:
    print(f'Erreur avec chemin absolu: {e}')
