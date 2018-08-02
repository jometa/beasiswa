# Import what we need
import functools
from flask import (
  Blueprint, flash, g, redirect, render_template,
  request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from .model import User, AppData, dbsession_required
from .auth import login_required
from .fuzz import mamdani

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
    dbsession = g.get('dbsession')
    xs = dbsession.query(AppData).all()
    return render_template('app/data.html', xs=xs)

@bp.route('/data/tambah', methods=['GET', 'POST'])
@dbsession_required
@login_required
def dataTambah():
    if request.method == 'POST':
        dbsession = g.get('dbsession')
        a = request.form['a']
        b = request.form['b']
        c = request.form['c']
        target = request.form['target']

        app_data = AppData(a=a, b=b, c=c, target=target)

        dbsession.add(app_data)
        dbsession.commit()
        return render_template('app/data-tambah-result.html')
    else:
        return render_template('app/data-tambah.html')

@bp.route('/data/edit', methods=['GET', 'POST'])
@dbsession_required
@login_required
def dataEdit():
    # Get id of app_data
    data_id = request.args.get('id')

    dbsession = g.get('dbsession')

    # Get the record
    record = dbsession.query(AppData).filter_by(id=int(data_id)).first()

    if request.method == 'POST':
        a = request.form['a']
        b = request.form['b']
        c = request.form['c']
        target = request.form['target']

        record.a = a
        record.b = b
        record.c = c
        record.target = target

        dbsession.commit()
        return render_template('app/data-edit-result.html', id=data_id)
    else:
        return render_template('app/data-edit.html', x=record)

@bp.route('/mamdani', methods=['GET', 'POST'])
@dbsession_required
@login_required
def mamdaniHandler():
    print(mamdani)
    if request.method == 'GET':
        return render_template('app/mamdani.html')
    else:
        name = request.form['name']
        a = float(request.form['a'])
        b = int(request.form['b'])
        c = float(request.form['c'])

        case = mamdani.Case(ipk=a, tan=b, pot=c)
        prob = mamdani.mamdani(case)

        return render_template('app/mamdani-result.html',
          name=name,
          prob=prob)

@bp.route('/tsukamoto')
@dbsession_required
@login_required
def tsukamoto():
    return render_template('app/tsukamoto.html')

@bp.route('/sugeno')
@dbsession_required
@login_required
def sugeno():
    return render_template('app/sugeno.html')

@bp.route('/perbandingan')
@dbsession_required
@login_required
def perbandingan():
    return render_template('app/perbandingan.html')