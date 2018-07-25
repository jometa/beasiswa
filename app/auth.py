# Import what we need
import functools
from flask import (
  Blueprint, flash, g, redirect, render_template,
  request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from .model import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login')
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        dbsession = g.get('dbsession')
        user = dbsession.query(User)\
            .filter(User.name == username)\
            .first()
        if user is None:
            error = 'Incorrect username'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password'
        
        if error is None:
            session.clear()
            session.['user_id'] = user.id
            return redirect(url_for('app'))
        
        flash(error)
    return render_template('auth/login.html')

@bp.route('/logut')
    pass