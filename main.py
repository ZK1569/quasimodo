import uvicorn
from fastapi import APIRouter, FastAPI

from src.controllers.bell import router as bell_router
from src.controllers.health import router as health_router


def main():
    app = FastAPI()

    api = APIRouter(prefix="/v1")

    api.include_router(health_router)
    api.include_router(bell_router)

    app.include_router(api)

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
