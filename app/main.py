from fastapi import FastAPI
from app.routes import skills
from app.database import engine
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jarvis AI COO Skill Registry")

app.include_router(skills.router)

@app.get("/")
def root():
    return {"message": "Jarvis AI COO Skill Registry", "docs": "/docs"}
