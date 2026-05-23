from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.accounts import router as accounts_router
from src.api.routes.health import router as health_router
from src.api.routes.results import router as results_router
from src.api.routes.history import router as history_router
from src.api.routes.auth import router as auth_router
from src.core.config import settings
from src.db.session import init_db

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
	init_db()
 
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(health_router, prefix="/api/v1/health", tags=["health"])
app.include_router(history_router, prefix="/api/v1/history", tags=["history"])
app.include_router(results_router, prefix="/api/v1/results", tags=["results"])
app.include_router(accounts_router, prefix="/api/v1/accounts", tags=["accounts"])
