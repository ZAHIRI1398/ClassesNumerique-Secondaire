from app import app, db, Exercise

with app.app_context():
    exercises = Exercise.query.all()
    print(f"Nombre d'exercices: {len(exercises)}")
    
    if exercises:
        ex = exercises[0]
        print(f"Premier exercice: {ex.title}")
        
        # Verifier si le champ image_path existe
        if hasattr(ex, 'image_path'):
            print(f"[OK] Le champ image_path existe: {ex.image_path}")
        else:
            print("[ERREUR] Le champ image_path n'existe pas")
            
        # Lister tous les attributs de l'exercice
        print("\nTous les attributs de l'exercice:")
        for attr in dir(ex):
            if not attr.startswith('_') and not callable(getattr(ex, attr)):
                try:
                    value = getattr(ex, attr)
                    print(f"  {attr}: {value}")
                except:
                    print(f"  {attr}: [erreur d'accès]")
