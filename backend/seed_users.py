"""
LinkShield AI - User Accounts Seeder
Idempotently seeds default officer and admin accounts from environment variables.
Usage:
    python backend/seed_users.py
"""
import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import SessionLocal, engine, Base
from app.models import User
from app.auth import hash_password
from app.config import settings

def seed_users():
    # Ensure tables are created
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        users_to_seed = [
            {
                "username": settings.OFFICER_DEFAULT_USERNAME.strip().lower(),
                "password": settings.OFFICER_DEFAULT_PASSWORD,
                "display_name": settings.OFFICER_DEFAULT_NAME,
                "role": "officer"
            },
            {
                "username": settings.ADMIN_DEFAULT_USERNAME.strip().lower(),
                "password": settings.ADMIN_DEFAULT_PASSWORD,
                "display_name": settings.ADMIN_DEFAULT_NAME,
                "role": "officer"
            },
            {
                "username": "citizen_demo",
                "password": "Citizen@Shield2026",
                "display_name": "Demo Citizen",
                "role": "citizen"
            }
        ]

        print("[*] Checking and seeding LinkShield accounts...")
        seeded_count = 0
        updated_count = 0

        for u in users_to_seed:
            existing = db.query(User).filter(User.username == u["username"]).first()
            if not existing:
                new_user = User(
                    id=uuid.uuid4().hex[:16],
                    username=u["username"],
                    display_name=u["display_name"],
                    password_hash=hash_password(u["password"]),
                    role=u["role"],
                    is_active=True,
                    failed_attempts=0,
                    created_at=datetime.now(timezone.utc)
                )
                db.add(new_user)
                seeded_count += 1
                print(f"    [+] Created {u['role'].upper()} account: {u['username']} ({u['display_name']})")
            else:
                # Update password hash to match .env if needed
                existing.password_hash = hash_password(u["password"])
                existing.display_name = u["display_name"]
                existing.role = u["role"]
                existing.is_active = True
                existing.locked_until = None
                existing.failed_attempts = 0
                updated_count += 1
                print(f"    [=] Verified {u['role'].upper()} account: {u['username']} (credentials synchronized)")

        db.commit()
        print(f"[SUCCESS] User seeding finished! Added: {seeded_count}, Updated/Verified: {updated_count}")
    except Exception as e:
        print(f"[ERROR] User seeding failed: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
