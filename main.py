import sys
from contextlib import asynccontextmanager
import uvicorn
from fastapi import APIRouter, FastAPI

from src.controllers.bell import router as bell_router
from src.controllers.health import router as health_router
from src.controllers.admin import router as admin_router
from src.utils.config import postgresql_database
from src.repositories.notification import get_notification_repository
from src.utils.env import EnvVariable


def main():

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        try:
            postgresql_database.test_connection()
            print("✅ Database connection established successfully.")

            notif_repo = get_notification_repository()
            _ = next(notif_repo)

        except Exception as e:
            sys.exit(f"❌ Error: {e}")
        yield

    app = FastAPI(lifespan=lifespan)

    api = APIRouter(prefix="/v1")

    api.include_router(health_router)
    api.include_router(bell_router)
    api.include_router(admin_router)

    app.include_router(api)

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    try:
        uvicorn.run(
            app,
            host=EnvVariable().address,
            port=int(EnvVariable().port)
        )
    except KeyboardInterrupt:
        postgresql_database.close()


if __name__ == "__main__":
    main()
