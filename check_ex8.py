#!/usr/bin/env python3
from flask import Flask
from models import db, Exercise
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    ex8 = Exercise.query.get(8)
    if ex8:
        print(f'Exercice 8: {ex8.title}')
        print(f'Type: {ex8.exercise_type}')
        content = json.loads(ex8.content)
        if 'draggable_items' in content:
            print(f'Elements: {content["draggable_items"]}')
            print(f'Ordre correct: {content.get("correct_order", "MANQUANT")}')
        else:
            print('Pas un exercice drag_and_drop!')
    else:
        print('Exercice 8 non trouve')
