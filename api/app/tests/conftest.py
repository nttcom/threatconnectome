import os
from unittest.mock import patch

import alembic.config
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.main import app
from app.models import Base

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


@pytest.fixture(autouse=True)
def clean_db(handle_db_once):
    with engine.begin() as connect:
        connect.execute(text("SET LOCAL session_replication_role = 'replica';"))
        table_names = ", ".join([table.name for table in Base.metadata.sorted_tables])
        connect.execute(text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE"))

    yield


@pytest.fixture(scope="function", autouse=True, name="testdb")
def handle_testdb():
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = testing_session_local()

    def override_create_session():
        return testing_session_local

    def override_get_db():
        try:
            yield db
        except SQLAlchemyError as sql_error:
            print("SQL ERROR:", sql_error)
            db.rollback()

    app.dependency_overrides[get_db] = override_get_db

    with patch("app.utility.progress_logger.create_session") as mock_create_session:
        mock_create_session.side_effect = override_create_session

        with patch("app.database.get_db") as mock_get_db:
            mock_get_db.side_effect = override_get_db
            yield db

    db.close()
