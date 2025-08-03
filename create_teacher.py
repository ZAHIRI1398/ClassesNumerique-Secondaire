from app import app, db
from models import User

with app.app_context():
    # Check if user already exists
    if User.query.filter_by(email='mr.zahiri@gmail.com').first():
        print("User already exists!")
    else:
        # Create new teacher account
        teacher = User(
            username='mr.zahiri',
            email='mr.zahiri@gmail.com',
            name='M. Zahiri',
            role='teacher'
        )
        teacher.set_password('zahiri123')  # temporary password
        
        try:
            db.session.add(teacher)
            db.session.commit()
            print("Teacher account created successfully!")
            print("Email: mr.zahiri@gmail.com")
            print("Password: zahiri123")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating account: {e}")
