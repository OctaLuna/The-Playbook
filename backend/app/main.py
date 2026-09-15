from fastapi import FastAPI

app = FastAPI(title="The Playbook")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
