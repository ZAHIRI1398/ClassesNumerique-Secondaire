#!/usr/bin/env python3
"""
Script pour redémarrer l'application Flask après les modifications.
Ce script arrête le processus Flask en cours d'exécution et le redémarre.
"""

import os
import sys
import time
import subprocess
import psutil
import signal

def find_flask_process():
    """Trouve le processus Flask en cours d'exécution"""
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

def stop_flask_process():
    """Arrête le processus Flask en cours d'exécution"""
    proc = find_flask_process()
    if proc:
        print(f"Processus Flask trouvé (PID: {proc.pid})")
        try:
            proc.terminate()
            print("Signal d'arrêt envoyé au processus Flask")
            
            # Attendre que le processus se termine
            try:
                proc.wait(timeout=5)
                print("Processus Flask arrêté avec succès")
                return True
            except psutil.TimeoutExpired:
                print("Le processus Flask ne répond pas au signal d'arrêt")
                print("Tentative d'arrêt forcé...")
                proc.kill()
                print("Processus Flask arrêté de force")
                return True
        except Exception as e:
            print(f"Erreur lors de l'arrêt du processus Flask: {str(e)}")
            return False
    else:
        print("Aucun processus Flask en cours d'exécution")
        return True

def start_flask_app():
    """Démarre l'application Flask"""
    try:
        # Démarrer Flask en arrière-plan
        print("Démarrage de l'application Flask...")
        
        # Utiliser subprocess.Popen pour démarrer le processus en arrière-plan
        process = subprocess.Popen(
            ["flask", "run"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE  # Ouvre une nouvelle fenêtre de console
        )
        
        # Attendre un peu pour s'assurer que le processus démarre
        time.sleep(2)
        
        # Vérifier si le processus est en cours d'exécution
        if process.poll() is None:
            print("Application Flask démarrée avec succès")
            print("URL: http://localhost:5000")
            return True
        else:
            stdout, stderr = process.communicate()
            print("Erreur lors du démarrage de l'application Flask:")
            print(f"Sortie standard: {stdout}")
            print(f"Erreur standard: {stderr}")
            return False
    except Exception as e:
        print(f"Erreur lors du démarrage de l'application Flask: {str(e)}")
        return False

def main():
    """Fonction principale"""
    print("Redémarrage de l'application Flask...")
    
    # Arrêter le processus Flask en cours d'exécution
    if stop_flask_process():
        # Attendre un peu avant de redémarrer
        time.sleep(1)
        
        # Démarrer l'application Flask
        if start_flask_app():
            print("\nL'application Flask a été redémarrée avec succès!")
            print("Les modifications apportées au code sont maintenant actives.")
            print("\nVous pouvez maintenant tester l'exercice ID 6 pour vérifier que le score est bien de 100%.")
            print("URL: http://localhost:5000/exercise/6")
        else:
            print("\nÉchec du redémarrage de l'application Flask.")
            print("Veuillez la démarrer manuellement avec la commande 'flask run'")
    else:
        print("\nÉchec de l'arrêt du processus Flask.")
        print("Veuillez arrêter manuellement le processus et redémarrer l'application avec 'flask run'")

if __name__ == "__main__":
    main()
