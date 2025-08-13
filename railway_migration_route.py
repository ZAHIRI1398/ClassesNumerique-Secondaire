"""
Route temporaire à ajouter dans app.py pour migrer la base depuis Railway lui-même
"""

# Ajoutez cette route dans votre app.py temporairement :

@app.route('/migrate-school-column')
def migrate_school_column():
    """Route temporaire pour ajouter la colonne school_name depuis Railway"""
    
    try:
        from sqlalchemy import text
        
        # Vérifier si la colonne existe déjà
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user' AND column_name = 'school_name'
        """))
        
        if result.fetchone():
            return "La colonne school_name existe déjà !"
        
        # Ajouter la colonne school_name
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN school_name VARCHAR(255);'))
        db.session.commit()
        
        return "✅ Colonne school_name ajoutée avec succès ! Votre application devrait maintenant fonctionner."
        
    except Exception as e:
        db.session.rollback()
        return f"❌ Erreur : {str(e)}"

# Instructions :
# 1. Ajoutez cette route dans app.py
# 2. Poussez sur GitHub (déploiement automatique Railway)
# 3. Visitez : https://votre-app.railway.app/migrate-school-column
# 4. Supprimez la route après usage
