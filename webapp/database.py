import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


DB_URL = os.getenv("DB_URL")


engine = create_engine(DB_URL)
db = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
