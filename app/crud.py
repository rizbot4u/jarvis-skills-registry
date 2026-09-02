from sqlalchemy.orm import Session
from app import models, schemas

def create_organization(db: Session, org: schemas.OrganizationCreate):
    db_org = models.Organization(name=org.name)
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

def create_skill(db: Session, skill: schemas.SkillCreate, org_id: int):
    db_skill = models.Skill(
        name=skill.name,
        description=skill.description,
        organization_id=org_id,
        status="draft"
    )
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill

def get_skills(db: Session, org_id: int):
    return db.query(models.Skill).filter(models.Skill.organization_id == org_id).all()

def get_skill(db: Session, skill_id: int, org_id: int):
    return db.query(models.Skill).filter(
        models.Skill.id == skill_id,
        models.Skill.organization_id == org_id
    ).first()

def create_skill_version(db: Session, skill_id: int, version: schemas.SkillVersionCreate):
    max_version = db.query(models.SkillVersion).filter(
        models.SkillVersion.skill_id == skill_id
    ).order_by(models.SkillVersion.version_number.desc()).first()
    next_version = (max_version.version_number + 1) if max_version else 1
    db_version = models.SkillVersion(
        skill_id=skill_id,
        version_number=next_version,
        configuration=version.configuration,
        created_by=version.created_by
    )
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    return db_version

def get_skill_versions(db: Session, skill_id: int):
    return db.query(models.SkillVersion).filter(
        models.SkillVersion.skill_id == skill_id
    ).order_by(models.SkillVersion.version_number).all()

def get_version(db: Session, version_id: int):
    return db.query(models.SkillVersion).filter(
        models.SkillVersion.id == version_id
    ).first()

def log_action(db: Session, org_id: int, actor: str, event: str, version_id: int):
    audit = models.AuditLog(
        organization_id=org_id,
        actor=actor,
        event=event,
        version_id=version_id
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit
