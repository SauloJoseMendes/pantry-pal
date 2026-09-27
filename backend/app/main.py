from app.core.config import settings
from fastapi import FastAPI

app = FastAPI(title="Pantry Pal")


@app.get("/health")
def health():
    return {"status": "ok", "jwt_algorithm": settings.jwt_algorithm}
