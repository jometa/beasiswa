# Import what we need
import functools
from flask import (
  Blueprint, flash, g, redirect, render_template,
  request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from .model import User, dbsession_required
from .auth import login_required

bp = Blueprint('app', __name__, url_prefix='/app')

@bp.route('/')
@dbsession_required
@login_required
def index():
    return render_template('app/index.html')

@bp.route('/data')
@dbsession_required
@login_required
def data():
    return render_template('app/data.html')

@bp.route('/mamdani')
@dbsession_required
@login_required
def mamdani():
    return render_template('app/mamdani.html')

@bp.route('/tsukamoto')
@dbsession_required
@login_required
def mamdani():
    return render_template('app/tsukamoto.html')

@bp.route('/sugeno')
@dbsession_required
@login_required
def mamdani():
    return render_template('app/sugeno.html')

@bp.route('/perbandingan')
@dbsession_required
@login_required
def mamdani():
    return render_template('app/perbandingan.html')