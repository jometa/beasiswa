from sqlalchemy import Column, ForeignKey, Integer, Float, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from flask import current_app, g
from flask.cli import with_appcontext

# Import click to have better cli interface.
# (Yes, better for Windows)
import click

# Define our model
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    password = Column(String(250), nullable=False)

class AppData(Base):
    __tablename__ = 'app_data'
    id = Column(Integer, primary_key=True)
    a = Column(Float, default=0.0)
    b = Column(Float, default=0.0)
    c = Column(Float, default=0.0)
    target = Column(Integer, default=0)

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
    Base.metadata.create_all(engine)
    print('Database created')

# Create the session and attach it to request context.
def create_session():
    if 'dbsession' not in g:
        Base.metadata.bind = engine
        session = DBSession(bind=engine)
        g.session = session

# Remove the session from request context and close it.
# What the fuck is 'e'
def close_session(e=None):
    session = g.pop('session', None)
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