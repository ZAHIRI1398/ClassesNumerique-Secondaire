#!/usr/bin/env python3
"""
Script pour redémarrer l'application Flask
"""

import os
import sys
import subprocess
import time
import signal
import psutil

def find_flask_process():
    """Trouve le processus Flask en cours d'exécution"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'python' in cmdline[0].lower() and any('app.py' in cmd for cmd in cmdline):
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None

def kill_flask_process():
    """Tue le processus Flask en cours d'exécution"""
    flask_proc = find_flask_process()
    if flask_proc:
        print(f"[INFO] Arrêt du processus Flask (PID: {flask_proc.pid})...")
        try:
            flask_proc.terminate()
            flask_proc.wait(timeout=5)
            print("[OK] Processus Flask arrêté avec succès")
            return True
        except Exception as e:
            print(f"[ERREUR] Erreur lors de l'arrêt du processus: {e}")
            try:
                flask_proc.kill()
                print("[OK] Processus Flask tué avec force")
                return True
            except Exception as e2:
                print(f"[ERREUR] Impossible de tuer le processus: {e2}")
                return False
    else:
        print("[INFO] Aucun processus Flask en cours d'exécution")
        return True

def start_flask():
    """Démarre l'application Flask"""
    try:
        print("[INFO] Démarrage de l'application Flask...")
        # Démarrer Flask en arrière-plan
        subprocess.Popen(["python", "app.py"], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
        
        # Attendre que le serveur démarre
        time.sleep(2)
        print("[OK] Application Flask démarrée")
        return True
    except Exception as e:
        print(f"[ERREUR] Erreur lors du démarrage de Flask: {e}")
        return False

def main():
    """Fonction principale pour redémarrer Flask"""
    print("[INFO] Redémarrage de l'application Flask...")
    
    # Arrêter l'application Flask en cours
    if not kill_flask_process():
        print("[AVERTISSEMENT] Problème lors de l'arrêt de Flask, tentative de démarrage quand même")
    
    # Démarrer l'application Flask
    if start_flask():
        print("[OK] Redémarrage de l'application Flask réussi")
        print("[INFO] L'application est maintenant accessible à l'adresse http://localhost:5000")
    else:
        print("[ERREUR] Échec du redémarrage de l'application Flask")

if __name__ == "__main__":
    main()
