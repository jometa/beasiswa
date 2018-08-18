# Import what we need
import functools
from flask import (
  Blueprint, flash, g, redirect, render_template,
  request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from .model import User, dbsession_required

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Decorator to check if user is logged in.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('/auth/login'), next=request.url)
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login',  methods=['POST', 'GET'])
@dbsession_required
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        dbsession = g.get('dbsession')
        user = dbsession.query(User)\
            .filter(User.username == username)\
            .first()

        if user is None:
            error = 'Incorrect username'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password'
        
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('app.index'))
        
        flash(error)
        return redirect(url_for('auth.login'))
    else:
        if session.get('user_id', None) is not None:
            return redirect('/app/data')
        else:
            return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')