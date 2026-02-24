import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import openapi
from app.auth.auth_module import get_auth_module
from app.auth.firebase_auth_module import FirebaseAuthModule
from app.auth.supabase_auth_module import SupabaseAuthModule
from app.routers import (
    actionlogs,
    auth,
    eols,
    external,
    pteams,
    tickets,
    users,
    vulns,
)
from app.ssvc import deployer_data
from app.utility.custom_middleware import CustomMiddleware


def create_app():
    app = FastAPI(title="Threatconnectome")
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

    app.add_middleware(CustomMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_headers=["*"],
        allow_methods=["DELETE", "GET", "OPTIONS", "POST", "PUT"],
        allow_origin_regex=r"https:\/\/threatconnectome--.+-[0-9a-z]{8}\.(firebaseapp\.com|web\.app)",
        allow_origins=origins,
    )

    # Register routersx
    app.include_router(auth.router)  # place auth on the top for comfortable docs
    app.include_router(actionlogs.router)
    app.include_router(external.router)
    app.include_router(pteams.router)
    app.include_router(users.router)
    app.include_router(vulns.router)
    app.include_router(tickets.router)
    app.include_router(eols.router)

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


@app.get("/internal-api/openapi.json", include_in_schema=False)
async def internal_openapi_schema():
    return openapi.custom_openapi(app)
