#!/usr/bin/env python3
"""
Script pour vérifier si l'application Flask a été redémarrée après la correction.
"""

import os
import sys
import time
import subprocess
import psutil

def get_app_process():
    """Recherche le processus Flask en cours d'exécution"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'python' in proc.info['name'].lower():
                cmdline_str = ' '.join(cmdline)
                if 'app.py' in cmdline_str or 'flask run' in cmdline_str:
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None

def get_app_start_time():
    """Obtient l'heure de démarrage du processus Flask"""
    proc = get_app_process()
    if proc:
        return proc.create_time()
    return None

def get_app_py_mod_time():
    """Obtient l'heure de dernière modification du fichier app.py"""
    if os.path.exists('app.py'):
        return os.path.getmtime('app.py')
    return None

def main():
    """Fonction principale"""
    print("Vérification de l'état de l'application Flask...")
    
    # Vérifier si le processus Flask est en cours d'exécution
    flask_proc = get_app_process()
    if flask_proc:
        print(f"Processus Flask trouvé (PID: {flask_proc.pid})")
        
        # Obtenir l'heure de démarrage du processus
        start_time = get_app_start_time()
        if start_time:
            start_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
            print(f"Heure de démarrage du processus: {start_time_str}")
        
        # Obtenir l'heure de dernière modification du fichier app.py
        mod_time = get_app_py_mod_time()
        if mod_time:
            mod_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mod_time))
            print(f"Dernière modification de app.py: {mod_time_str}")
        
        # Comparer les heures
        if start_time and mod_time:
            if start_time < mod_time:
                print("\n[PROBLÈME DÉTECTÉ] L'application Flask n'a PAS été redémarrée après la modification de app.py!")
                print("Les modifications apportées au code ne sont pas prises en compte.")
                print("\nSolution: Redémarrer l'application Flask avec la commande:")
                print("  flask run")
                return False
            else:
                print("\n[OK] L'application Flask a été démarrée après la dernière modification de app.py.")
                print("Les modifications devraient être prises en compte.")
                return True
    else:
        print("Aucun processus Flask en cours d'exécution.")
        print("\nPour démarrer l'application, utilisez la commande:")
        print("  flask run")
        return False

if __name__ == "__main__":
    main()
