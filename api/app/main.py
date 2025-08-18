import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect

from app.auth.auth_module import get_auth_module
from app.auth.firebase_auth_module import FirebaseAuthModule
from app.auth.supabase_auth_module import SupabaseAuthModule
from app.database import create_session
from app.models import ObjectCategory
from app.routers import (
    actionlogs,
    actions,
    auth,
    external,
    pteams,
    tickets,
    users,
    vulns,
)
from app.ssvc import deployer_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize default categories in the database
    SessionLocal = create_session()
    with SessionLocal() as db:
        inspector = inspect(db.bind)
        if 'objectcategory' in inspector.get_table_names():
            ObjectCategory.ensure_default_categories(db)
            logging.info("Default ObjectCategory categories initialized successfully")

    yield


def create_app():
    app = FastAPI(title="Threatconnectome", lifespan=lifespan)
    origins = [
        "http://localhost:3000",  # dev
        "http://localhost:4173",  # dev: vite preview
        "http://localhost:5173",  # dev: vite dev
        "http://localhost:8080",  # dev
        "http://localhost",  # dev
        "https://threatconnectome.firebase.app",  # prod-alias
        "https://threatconnectome.metemcyber.ntt.com",  # prod
        "https://threatconnectome.web.app",  # prod-alias
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_headers=["*"],
        allow_methods=["DELETE", "GET", "OPTION", "POST", "PUT"],
        allow_origin_regex=r"https:\/\/threatconnectome--.+-[0-9a-z]{8}\.(firebaseapp\.com|web\.app)",
        allow_origins=origins,
    )

    # Register routersx
    app.include_router(auth.router)  # place auth on the top for comfortable docs
    app.include_router(actionlogs.router)
    app.include_router(actions.router)
    app.include_router(external.router)
    app.include_router(pteams.router)
    app.include_router(users.router)
    app.include_router(vulns.router)
    app.include_router(tickets.router)

    # setup auth

    auth_service = os.environ.get("AUTH_SERVICE")
    match auth_service:
        case "FIREBASE":
            auth_module = FirebaseAuthModule()
        case "SUPABASE":
            auth_module = SupabaseAuthModule()
        case _:
            raise Exception(f"Unsupported AUTH_SERVICE: {auth_service}")

    # Dependency injection as needed
    app.dependency_overrides[get_auth_module] = lambda: auth_module

    return app


app = create_app()

LOGLEVEL = os.environ.get("API_LOGLEVEL", "INFO").upper()
logging.basicConfig(
    level=LOGLEVEL if LOGLEVEL != "" else "INFO",
    format="%(levelname)s - %(asctime)s - %(name)s - %(message)s",
)

try:
    deployer_data.initialize()
except OSError as error:
    raise Exception(f"Cannot open file Deployer.json. detail: {error}")
except (KeyError, TypeError) as error:
    raise Exception(f"File Deployer.json has invalid syntax. detail: {error}")
