# Import what we need
import functools
from flask import (
  Blueprint, flash, g, redirect, render_template,
  request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from .model import User, AppData, dbsession_required
from .auth import login_required
from .fuzz.fuzzmethods import Case, tsukamoto, sugeno, compare_methods, mamdani
# from .fuzz import mamdani
import collections

bp = Blueprint('app', __name__, url_prefix='/app')

PenentuanResult = collections.namedtuple('PenentuanResult', ['metode', 'prob'])

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
        name = request.form['name']
        a = request.form['a']
        b = request.form['b']
        c = request.form['c']
        target = request.form['target']

        app_data = AppData(name=name, a=a, b=b, c=c, target=target)

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

@bp.route('/tsukamoto', methods=['GET', 'POST'])
@dbsession_required
@login_required
def tsukamotoHandler():
    if request.method == 'GET':
        return render_template('app/tsukamoto.html')
    elif request.method == 'POST':
        name = request.form['name']
        a = float(request.form['a'])
        b = int(request.form['b'])
        c = float(request.form['c'])

        case = Case(ipk=a, tan=b, pot=c)
        prob = tsukamoto.run(case)

        return render_template('app/klas-result.html',
          name=name,
          prob=prob,
          metode='Tsukamoto')
    else:
        raise Exception('unknown http method. only accepts GET and POST')

@bp.route('/sugeno', methods=['GET', 'POST'])
@dbsession_required
@login_required
def sugenoHandler():
    if request.method == 'GET':
        return render_template('app/klas-view.html', metode='Sugeno')
    else:
        name = request.form['name']
        a = float(request.form['a'])
        b = int(request.form['b'])
        c = float(request.form['c'])

        case = Case(ipk=a, tan=b, pot=c)
        prob = sugeno.run(case)

        return render_template('app/klas-result.html',
          name=name,
          prob=prob,
          metode='Sugeno')

@bp.route('/perbandingan', methods=['GET', 'POST'])
@dbsession_required
@login_required
def perbandingan():
    if request.method == 'GET':
        return render_template('app/perbandingan.html')
    else:
        n = int(request.form['n'])
        a = float(request.form['a'])
        b = int(request.form['b'])
        c = float(request.form['c'])
        case = Case(ipk=a, tan=b, pot=c)
        result = compare_methods(case)
        return render_template('app/perbandingan-result.html', result=result, n=n)

@bp.route('/penentuan', methods=['GET', 'POST'])
@dbsession_required
@login_required
def penentuan():
    if request.method == 'GET':
        return render_template('app/klas-view.html')
    else:
        a = float(request.form['a'])
        b = int(request.form['b'])
        c = float(request.form['c'])

        case = Case(ipk=a, tan=b, pot=c)
        # mcase = mamdani.Case(ipk=a, tan=b, pot=c)
        mprob = mamdani.run(case)
        result = (
            PenentuanResult( 'sugeno', sugeno.run(case) ),
            PenentuanResult( 'mamdani', mprob ),
            PenentuanResult( 'tsukamoto', tsukamoto.run(case) )
        )

        return render_template('app/penentuan-result.html',
          result=result)
