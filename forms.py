from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, validators
from models import Exercise

class ExerciseForm(FlaskForm):
    title = StringField('Titre', validators=[validators.DataRequired()])
    description = TextAreaField('Description', validators=[validators.DataRequired()])
    exercise_type = SelectField('Type d\'exercice', choices=Exercise.EXERCISE_TYPES, validators=[validators.DataRequired()])

