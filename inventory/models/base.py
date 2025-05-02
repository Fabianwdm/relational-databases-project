
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

def get_engine(db_url):
    """Create and return a database engine"""
    return create_engine(db_url)

def get_session(engine):
    """Create and return a database session"""
    Session = sessionmaker(bind=engine)
    return Session()