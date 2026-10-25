from fastapi import FastAPI

from app.api.explanations import router as explanations_router
from app.api.matches import router as matches_router

app = FastAPI(title="The Playbook")
app.include_router(matches_router)
app.include_router(explanations_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
