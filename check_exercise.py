#!/usr/bin/env python3
from flask import Flask
from models import db, Exercise
import json
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def list_exercises():
    with app.app_context():
        exercises = Exercise.query.all()
        print("\n=== Liste des exercices ===")
        for ex in exercises:
            print(f"ID: {ex.id}, Type: {ex.exercise_type}, Titre: {ex.title}")

if __name__ == "__main__":
    list_exercises()
