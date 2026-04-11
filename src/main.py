from fastapi import FastAPI

from src.api.routes.accounts import router as accounts_router
from src.api.routes.health import router as health_router
from src.api.routes.results import router as results_router
from src.api.routes.uploads import router as uploads_router
from src.api.routes.auth import router as auth_router
from src.core.config import settings
from src.db.session import init_db

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def on_startup() -> None:
	init_db()
 
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(health_router, prefix="/api/v1/health", tags=["health"])
app.include_router(uploads_router, prefix="/api/v1/uploads", tags=["uploads"])
app.include_router(results_router, prefix="/api/v1/results", tags=["results"])
app.include_router(accounts_router, prefix="/api/v1/accounts", tags=["accounts"])