from fastapi import FastAPI

from app.database import Base, engine
from app.routes import tasks, users

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo API", version="1.0.0")

app.include_router(tasks.router)
app.include_router(users.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
