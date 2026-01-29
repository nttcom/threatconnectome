import os
from unittest.mock import patch

import alembic.config
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.database import get_db
from app.main import app

db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASSWORD")
testdb_host = os.getenv("TESTDB_HOST")
db_port = os.getenv("DB_PORT")
db_schema = os.getenv("DB_SCHEMA")

TEST_SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://{db_user}:{db_pass}@{testdb_host}:{db_port}/{db_schema}"
)


engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL)


@pytest.fixture(scope="session", autouse=True)
def handle_db_once():
    cwd = os.getcwd()
    os.chdir("./app")  # switch dir to where alembic.ini placed.
    alembic.config.main(argv=["--raiseerr", "upgrade", "head"])
    os.chdir(cwd)

    yield

    # os.chdir("./app")  # switch dir to where alembic.ini placed.
    # alembic.config.main(argv=["--raiseerr", "downgrade", "base"])
    # os.chdir(cwd)


class TestingSession(Session):
    def commit(self):
        # Not persistence because of testing
        self.flush()
        self.expire_all()


@pytest.fixture(scope="function", autouse=True, name="testdb")
def handle_testdb():
    testing_session_local = sessionmaker(
        class_=TestingSession, autocommit=False, autoflush=False, bind=engine
    )
    db = testing_session_local()

    def override_get_db():
        try:
            yield db
        except SQLAlchemyError as sql_error:
            print("SQL ERROR:", sql_error)
            db.rollback()

    app.dependency_overrides[get_db] = override_get_db
    with patch("app.database.get_db") as mock:  # for open_db_session called from background tasks
        mock.side_effect = override_get_db
        yield db

    db.rollback()
    db.close()
