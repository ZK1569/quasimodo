from fastapi import APIRouter

from src.utils.env import EnvVariable

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
def health():
    env = EnvVariable()
    return {"status": "OK", "env": env.environnement, "version": env.version}
