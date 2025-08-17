from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_teacher:
            flash('Accès réservé aux enseignants.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function
