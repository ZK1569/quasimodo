import uvicorn
from fastapi import APIRouter, FastAPI
import sys
from src.controllers.bell import router as bell_router
from src.controllers.health import router as health_router
from src.utils.config import postgresql_database
from contextlib import asynccontextmanager


def main():

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            postgresql_database.test_connection()
            print("✅ Database connection established successfully.")
        except Exception as e:
            sys.exit(f"❌ Error: {e}")
        yield

    app = FastAPI(lifespan=lifespan)


    api = APIRouter(prefix="/v1")

    api.include_router(health_router)
    api.include_router(bell_router)

    app.include_router(api)

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    uvicorn.run(app, host="localhost", port=8080)

    postgresql_database.close()


if __name__ == "__main__":
    main()
