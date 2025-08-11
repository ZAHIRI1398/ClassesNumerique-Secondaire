web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
release: python -c "from app import app, db; db.create_all()"
