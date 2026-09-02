from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app import crud, schemas, models
from app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_org(org_id: Optional[int] = Header(None, alias="X-Organization-ID")):
    if org_id is None:
        raise HTTPException(status_code=400, detail="X-Organization-ID header required")
    return org_id

# 1. Active skills route (MUST come before /skills/{skill_id})
@router.get("/skills/active", response_model=List[schemas.Skill])
def get_active_skills(
    db: Session = Depends(get_db),
    org_id: int = Depends(get_current_org)
):
    return db.query(models.Skill).filter(
        models.Skill.organization_id == org_id,
        models.Skill.status == "active"
    ).all()

@router.post("/skills", response_model=schemas.Skill)
def create_skill(
    skill: schemas.SkillCreate,
    db: Session = Depends(get_db),
    org_id: int = Depends(get_current_org)
):
    return crud.create_skill(db, skill, org_id)

@router.get("/skills", response_model=List[schemas.Skill])
def list_skills(
    db: Session = Depends(get_db),
    org_id: int = Depends(get_current_org)
):
    return crud.get_skills(db, org_id)

@router.get("/skills/{skill_id}", response_model=schemas.Skill)
def get_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    org_id: int = Depends(get_current_org)
):
    skill = crud.get_skill(db, skill_id, org_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    skill.versions = crud.get_skill_versions(db, skill_id)
    return skill

@router.post("/skills/{skill_id}/versions", response_model=schemas.SkillVersion)
def create_version(
    skill_id: int,
    version: schemas.SkillVersionCreate,
    db: Session = Depends(get_db),
    org_id: int = Depends(get_current_org)
):
    skill = crud.get_skill(db, skill_id, org_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    if skill.status == "active":
        raise HTTPException(status_code=400, detail="Cannot add version to active skill")
    new_version = crud.create_skill_version(db, skill_id, version)
    crud.log_action(db, org_id, version.created_by, "created_version", new_version.id)
    return new_version

@router.post("/skills/{skill_id}/activate")
def activate_skill(
    skill_id: int,
    version_id: int,
    actor: str,
    db: Session = Depends(get_db),
    org_id: int = Depends(get_current_org)
):
    skill = crud.get_skill(db, skill_id, org_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    if actor != "owner":
        raise HTTPException(status_code=403, detail="Only owner can activate")
    version = crud.get_version(db, version_id)
    if not version or version.skill_id != skill_id:
        raise HTTPException(status_code=404, detail="Version not found")
    if skill.status == "active" and skill.active_version_id == version_id:
        return {"message": "Skill already active with this version"}
    skill.status = "active"
    skill.active_version_id = version_id
    db.commit()
    db.refresh(skill)
    crud.log_action(db, org_id, actor, "activated_skill", version_id)
    return {"message": f"Skill {skill_id} activated with version {version_id}"}

@router.delete("/skills/{skill_id}")
def disable_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    org_id: int = Depends(get_current_org)
):
    skill = crud.get_skill(db, skill_id, org_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    if skill.status == "disabled":
        raise HTTPException(status_code=400, detail="Skill already disabled")
    skill.status = "disabled"
    db.commit()
    crud.log_action(db, org_id, "system", "disabled_skill", 0)
    return {"message": f"Skill {skill_id} disabled"}

@router.post("/organizations", response_model=schemas.Organization)
def create_organization(
    org: schemas.OrganizationCreate,
    db: Session = Depends(get_db)
):
    return crud.create_organization(db, org)
