from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Class
from decorators import teacher_required

def register_teacher_classes_route(app):
    @app.route('/teacher/classes')
    @login_required
    @teacher_required
    def teacher_classes():
        """Affiche toutes les classes de l'enseignant connecté"""
        classes = Class.query.filter_by(teacher_id=current_user.id).all()
        return render_template('teacher/classes.html', classes=classes)
