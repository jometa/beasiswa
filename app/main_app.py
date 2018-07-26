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
