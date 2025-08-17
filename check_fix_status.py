#!/usr/bin/env python3
"""
Script pour vérifier si la correction du scoring fill_in_blanks est bien appliquée dans app.py
Version simplifiée sans caractères spéciaux
"""

import re
import os
import sys

def check_app_py():
    """Vérifie si la correction est bien appliquée dans app.py"""
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
            
        # Vérifier si la première implémentation est bien désactivée
        pattern_first_impl = r"elif exercise\.exercise_type == 'fill_in_blanks':\s+# Cette implémentation a été désactivée.*?\s+pass\s+"
        match_first_impl = re.search(pattern_first_impl, content, re.DOTALL)
        
        if match_first_impl:
            print("[OK] La première implémentation est bien désactivée avec un 'pass'")
            
            # Vérifier qu'il n'y a pas de code actif après le pass
            disabled_section = match_first_impl.group(0)
            if "user_answers" in disabled_section or "correct_answers" in disabled_section:
                print("[PROBLEME] Il y a encore du code actif après le 'pass'")
                print("Extrait du code problématique:")
                print(disabled_section[:200] + "..." if len(disabled_section) > 200 else disabled_section)
            else:
                print("[OK] Pas de code actif après le 'pass'")
        else:
            print("[PROBLEME] La première implémentation n'est pas correctement désactivée")
            
        # Vérifier si la deuxième implémentation est présente et active
        pattern_second_impl = r"# Logique de scoring pour fill_in_blanks.*?total_blanks_in_content = 0"
        match_second_impl = re.search(pattern_second_impl, content, re.DOTALL)
        
        if match_second_impl:
            print("[OK] La deuxième implémentation est présente")
            
            # Vérifier le calcul du score
            pattern_score_calc = r"score = \(correct_blanks / total_blanks\) \* 100 if total_blanks > 0 else 0"
            if re.search(pattern_score_calc, content):
                print("[OK] Le calcul du score est correct")
            else:
                print("[PROBLEME] Le calcul du score n'est pas trouvé ou incorrect")
        else:
            print("[PROBLEME] La deuxième implémentation n'est pas trouvée")
            
        # Vérifier la redirection après soumission
        pattern_redirect = r"return redirect\(url_for\('view_exercise', exercise_id=exercise_id.*?\)\)"
        match_redirect = re.search(pattern_redirect, content)
        
        if match_redirect:
            print("[INFO] La soumission redirige vers view_exercise")
            print("[ATTENTION] Cela pourrait expliquer pourquoi le score n'est pas mis à jour dans l'UI")
            print("   La page est rechargée sans afficher le template feedback.html")
        
        # Vérifier si l'application a été modifiée récemment
        app_py_stat = os.stat("app.py")
        print(f"\nDernière modification de app.py: {app_py_stat.st_mtime}")
        
        # Vérifier s'il existe des backups récents
        backups = [f for f in os.listdir(".") if f.startswith("app.py.bak")]
        if backups:
            print(f"Backups trouvés: {backups}")
            
        return True
    except Exception as e:
        print(f"Erreur lors de la vérification: {e}")
        return False

def check_process_running():
    """Vérifie si le processus Flask est en cours d'exécution"""
    try:
        import psutil
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and 'python' in proc.info['name'].lower():
                    cmdline_str = ' '.join(cmdline)
                    if 'app.py' in cmdline_str or 'flask run' in cmdline_str:
                        print(f"\n[OK] Processus Flask trouvé (PID: {proc.pid})")
                        print(f"Ligne de commande: {cmdline_str}")
                        
                        # Vérifier quand le processus a été démarré
                        proc_info = proc.as_dict(attrs=['create_time'])
                        import datetime
                        create_time = datetime.datetime.fromtimestamp(proc_info['create_time']).strftime('%Y-%m-%d %H:%M:%S')
                        print(f"Démarré le: {create_time}")
                        
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
                
        print("\n[PROBLEME] Aucun processus Flask trouvé en cours d'exécution")
        print("[ATTENTION] L'application doit être redémarrée pour appliquer les modifications")
        return False
    except ImportError:
        print("\n[PROBLEME] Module psutil non disponible, impossible de vérifier les processus")
        print("Installez-le avec: pip install psutil")
        return False

def main():
    """Fonction principale"""
    print("=== Vérification de la correction du scoring fill_in_blanks ===\n")
    
    # Vérifier app.py
    check_app_py()
    
    # Vérifier si le processus est en cours d'exécution
    check_process_running()
    
    print("\n=== Recommandations ===")
    print("1. Si l'application n'est pas en cours d'exécution, démarrez-la avec 'flask run'")
    print("2. Si l'application est en cours d'exécution mais que les modifications ne sont pas appliquées:")
    print("   - Arrêtez l'application (Ctrl+C dans le terminal où elle s'exécute)")
    print("   - Redémarrez-la avec 'flask run'")
    print("3. Testez l'exercice ID 6 pour vérifier si le score est maintenant correct")

if __name__ == "__main__":
    main()
