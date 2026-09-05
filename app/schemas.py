from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

class OrganizationBase(BaseModel):
    name: str

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, description="Skill name is required")
    description: Optional[str] = None

class SkillCreate(SkillBase):
    pass

class Skill(SkillBase):
    id: int
    status: str
    organization_id: int
    active_version_id: Optional[int] = None
    versions: List['SkillVersion'] = []
    model_config = ConfigDict(from_attributes=True)

class SkillVersionBase(BaseModel):
    version_number: int
    configuration: str
    created_by: str

class SkillVersionCreate(SkillVersionBase):
    pass

class SkillVersion(SkillVersionBase):
    id: int
    skill_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AuditLog(BaseModel):
    id: int
    organization_id: int
    actor: str
    event: str
    version_id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

Skill.model_rebuild()
