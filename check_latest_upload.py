import os
import time

# Vérifier le dernier fichier uploadé
uploads_dir = "static/uploads"

print("=== VÉRIFICATION DERNIER UPLOAD ===")

if os.path.exists(uploads_dir):
    # Trouver le fichier le plus récent
    files = []
    for filename in os.listdir(uploads_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            filepath = os.path.join(uploads_dir, filename)
            mtime = os.path.getmtime(filepath)
            size = os.path.getsize(filepath)
            files.append((filename, mtime, size))
    
    # Trier par date (plus récent en premier)
    files.sort(key=lambda x: x[1], reverse=True)
    
    print("5 derniers fichiers uploadés:")
    for i, (filename, mtime, size) in enumerate(files[:5]):
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
        status = "OK" if size > 0 else "CORROMPU"
        print(f"{i+1}. {status} {filename}")
        print(f"   Taille: {size} octets | Date: {time_str}")
        
        # Vérifier si c'est un upload très récent (moins de 5 minutes)
        if time.time() - mtime < 300:  # 5 minutes
            print(f"   >>> UPLOAD RÉCENT <<<")
            if size == 0:
                print(f"   PROBLEME: Le fichier est encore vide!")
            else:
                print(f"   SUCCES: Le fichier a une taille valide!")
        print()

else:
    print("Dossier uploads non trouvé")

print("Si vous venez d'uploader une image et qu'elle est encore vide,")
print("cela signifie que la correction n'a pas fonctionné comme prévu.")
