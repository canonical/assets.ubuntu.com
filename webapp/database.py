from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from webapp.config import config


db_engine = create_engine(config.database_url.get_secret_value())
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
)
