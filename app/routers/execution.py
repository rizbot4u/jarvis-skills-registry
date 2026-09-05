from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.auth import get_current_user
from app.models import Skill, SkillVersion, AuditLog
from app.services.validator import validate_skill_payload

router = APIRouter(prefix="/skills", tags=["Execution"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/{skill_id}/execute", status_code=status.HTTP_200_OK)
def execute_skill(
    skill_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    skill = db.query(Skill).filter(
        Skill.id == skill_id,
        Skill.organization_id == current_user["org_id"]
    ).first()
    
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    
    if skill.status != "active" or not skill.active_version_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skill is not active or lacks an active version"
        )
    
    active_version = db.query(SkillVersion).filter(
        SkillVersion.id == skill.active_version_id
    ).first()
    
    if not active_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active version record missing"
        )
    
    validated_input = validate_skill_payload(active_version.configuration, payload)
    
    audit_entry = AuditLog(
        organization_id=current_user["org_id"],
        actor=current_user["sub"],
        event="SKILL_EXECUTION",
        version_id=active_version.id
    )
    db.add(audit_entry)
    db.commit()
    
    return {
        "status": "success",
        "skill_id": skill.id,
        "skill_name": skill.name,
        "active_version": active_version.version_number,
        "input": validated_input,
        "output": f"Executed skill '{skill.name}' successfully."
    }
