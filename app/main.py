from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.routes import skills
from app.database import SessionLocal, engine
from app import models
from app.auth import create_access_token, authenticate_user

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jarvis AI COO Skill Registry")

app.include_router(skills.router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={
            "sub": user.username,
            "org_id": user.organization_id,
            "role": user.role
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
def root():
    return {"message": "Jarvis AI COO Skill Registry", "docs": "/docs"}
