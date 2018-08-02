from sqlalchemy import Column, ForeignKey, Integer, Float, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from functools import wraps
import os.path
import os

# Import click to have better cli interface.
# (Yes, better for Windows)
import click

# Define our model
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(250), nullable=False)
    password = Column(String(250), nullable=False)

class AppData(Base):
    __tablename__ = 'app_data'
    id = Column(Integer, primary_key=True)
    a = Column(Float, default=0.0)
    b = Column(Float, default=0.0)
    c = Column(Float, default=0.0)
    target = Column(Float, default=0.0)

# DB Name
dbname = 'beasiswa.db'

# Engine to must  be singleton. Python caching its module.
engine = create_engine('sqlite:///{}'.format(dbname))

# Session Maker must be global scope
DBSession = sessionmaker(autoflush=True)

# Function to initialize db
# You can call it from flask-cli
@click.command('init-db')
@with_appcontext
def init_db():
    # Remove db
    db_name = 'beasiswa.db'
    if (os.path.isfile(db_name)):
        os.remove(db_name)
        print('Removing db')

    Base.metadata.create_all(engine)
    dbsession = DBSession(bind=engine)
    phash = generate_password_hash('admin')
    user = User(username='admin', password=phash)
    dbsession.add(user)
    dbsession.commit()

    # Randomize our dataset
    import random
    def random_dset(nrand=50):
        dbsession = DBSession(bind=engine)
        for i in  range(nrand):
            a = random.random() * 4
            b = int(random.random() * 10)
            c = random.randint(1_000_000, 10_000_000)
            target = random.random() * 100
            x = AppData(a=a, b=b, c=c, target=target)
            dbsession.add(x)
            
            print('Add {}/{} data'.format(i + 1, nrand))
        dbsession.commit()
    random_dset()

    print('Database created')

# Create the session and attach it to request context.
def create_session():
    Base.metadata.bind = engine
    session = DBSession(bind=engine)
    return session

# Decorator to inject dbsession into app_context
def dbsession_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        dbsession = g.pop('dbsession', None)
        if dbsession is None:
            g.dbsession = create_session()
        return f(*args, **kwargs)
    return wrap

# Remove the session from request context and close it.
# What the fuck is 'e'
def close_session(e=None):
    session = g.pop('dbsession', None)
    if session is not None:
        session.close()

# Register session lifecycle hook to instance.
# Using function since we use factory.
def init_app(app=None):
    if app is None: raise Exception('App is none!')
    app.teardown_appcontext(close_session)
    app.cli.add_command(init_db)

# Create mapping from attr to its display.
attr_map = {
  'a': 'a',
  'b': 'b',
  'c': 'c'
}
