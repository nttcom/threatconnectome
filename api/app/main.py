from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import get_firebase_credentials, setup_firebase_auth
from app.routers import (
    actionlogs,
    actions,
    ateams,
    auth,
    external,
    misptags,
    pteams,
    tags,
    topics,
    users,
)


def create_app():
    app = FastAPI(title="Threatconnectome")
    origins = [
        "http://localhost:3000",  # dev
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
    app.include_router(ateams.router)
    app.include_router(external.router)
    app.include_router(misptags.router)
    app.include_router(pteams.router)
    app.include_router(tags.router)
    app.include_router(topics.router)
    app.include_router(users.router)

    # setup firebase
    cred = setup_firebase_auth()

    # Dependency injection as needed
    app.dependency_overrides[get_firebase_credentials] = lambda: cred

    return app


app = create_app()
