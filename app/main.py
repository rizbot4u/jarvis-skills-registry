from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from pydantic import BaseModel
from app.routes import skills
from app.routers import execution
from app.database import SessionLocal, engine
from app import models
from app.auth import create_access_token, authenticate_user, get_current_user
from app.services.agent_orchestrator import JarvisAgentOrchestrator

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jarvis AI COO Skill Registry")

# Include routers
app.include_router(skills.router)
app.include_router(execution.router)

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

# ============================================================
# LLM Agent Endpoint
# ============================================================

class AgentRunRequest(BaseModel):
    prompt: str
    payload: Optional[Dict[str, Any]] = None

@app.post("/agent/run", tags=["LLM Agent"])
def run_agent(
    body: AgentRunRequest,
    authorization: str = Header(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Triggers the LLM Orchestrator to fetch active skills for the current
    authenticated user's organization and execute the selected tool call.
    """
    # Extract Bearer token from incoming request header
    token = authorization.replace("Bearer ", "")
    
    orchestrator = JarvisAgentOrchestrator(auth_token=token)
    
    try:
        result = orchestrator.run_agent_loop(
            user_prompt=body.prompt,
            mock_llm_choice=body.payload
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
