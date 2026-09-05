#!/usr/bin/env python3
"""Seed initial users for testing"""

from app.database import SessionLocal
from app import models
from app.auth import hash_password

def seed():
    db = SessionLocal()
    
    # Check if users already exist
    existing = db.query(models.User).first()
    if existing:
        print("⚠️ Users already exist, skipping...")
        return
    
    users = [
        {"username": "owner1", "password": "password123", "organization_id": 1, "role": "owner"},
        {"username": "user1", "password": "password123", "organization_id": 1, "role": "user"},
        {"username": "owner2", "password": "password123", "organization_id": 2, "role": "owner"},
    ]
    
    for user_data in users:
        hashed = hash_password(user_data["password"])
        user = models.User(
            username=user_data["username"],
            hashed_password=hashed,
            organization_id=user_data["organization_id"],
            role=user_data["role"]
        )
        db.add(user)
    
    db.commit()
    db.close()
    print("✅ Users seeded successfully")

if __name__ == "__main__":
    seed()
