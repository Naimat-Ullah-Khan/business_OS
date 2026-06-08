from app.core.database import SessionLocal
from app.models.plan import Plan

def seed_plans():
    db = SessionLocal()
    try:
        existing = {p.name for p in db.query(Plan).all()}
        for name in ["free", "pro", "enterprise"]:
            if name not in existing:
                db.add(Plan(name=name))
        db.commit()
        print("Plans seeded.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_plans()