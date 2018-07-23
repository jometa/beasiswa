from sqlalchemy import Column, ForeignKey, Integer, Float, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    password = Column(String(250), nullable=False)

class AppData(Base):
    __tablename__ = 'app_data'
    id = Column(Integer, primary_key=True)
    a = Column(Float), default=0.0)
    b = Column(Float, default=0.0)
    c = Column(Float, default=0.0)
    target = Column(Integer, default=0)

engine = create_engine('sqlite:///sistemik.db')

Base.metadata.create_all(engine)