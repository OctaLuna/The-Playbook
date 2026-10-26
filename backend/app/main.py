from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.explanations import router as explanations_router
from app.api.matches import router as matches_router
from app.core.config import get_settings

app = FastAPI(title="The Playbook")
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)
app.include_router(matches_router)
app.include_router(explanations_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
