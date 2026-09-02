from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    status = Column(String, default="draft")
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    active_version_id = Column(Integer, nullable=True)
    organization = relationship("Organization")

class SkillVersion(Base):
    __tablename__ = "skill_versions"
    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"))
    version_number = Column(Integer)
    configuration = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    actor = Column(String)
    event = Column(String)
    version_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
