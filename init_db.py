from app import app, db
# Import all models to ensure tables are created
from models import User, Class, Course, Exercise, ExerciseAttempt, CourseFile

with app.app_context():
    db.create_all()
    print("Base de données créée avec succès")
    
    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Tables créées: {tables}")
