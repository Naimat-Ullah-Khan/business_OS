from sqlalchemy.orm import Session
from app.models.company import Company
from app.schemas.company import CompanyCreate

def create_company(db: Session, data: CompanyCreate):
    company = Company(name=data.name)

    db.add(company)
    db.commit()
    db.refresh(company)

    return company