from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from fastapi import Depends

from typing import Annotated


SQLALCHEMY_DATABASE_URL = 'sqlite:///./todo_app.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       connect_args={'check_same_thread': False})


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    This creates a database session instance, keeps it open until all the
    selected operations are done. Then closes the database.
    :return: None
    """
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# database injection to open the database and close it after complete data
# fetching/modifications.
db_dependency = Annotated[Session, Depends(get_db)]