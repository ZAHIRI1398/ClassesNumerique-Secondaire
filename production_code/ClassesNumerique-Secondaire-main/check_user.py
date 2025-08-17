from app import app, db
from models import User

with app.app_context():
    # Try to find the user
    user = User.query.filter_by(email='mr.zahiri@gmail.com').first()
    if user:
        print(f"User found:")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
    else:
        print("User not found with email: mr.zahiri@gmail.com")
        
    # List all users for verification
    print("\nAll users in database:")
    all_users = User.query.all()
    for user in all_users:
        print(f"- {user.email} (Role: {user.role})")
