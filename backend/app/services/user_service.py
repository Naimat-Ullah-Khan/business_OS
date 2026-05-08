from sqlalchemy.orm import Session
from app.models.user import User
from app.models.company import Company
from app.schemas.user import UserCreate, UserInvite
from app.core.security import hash_password, verify_password, create_access_token
from app.models.plan import Plan


def create_user(db: Session, user_data: UserCreate):
    # CHECK IF USER EXISTS
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise ValueError("Email already Registered")

    plan = db.query(Plan).filter(Plan.name == "free").first()
    # CREATE COMPANY FIRST
    company = Company(
        name=user_data.company_name,
        plan_id=plan.id,
    )
    db.add(company)
    db.commit()
    db.refresh(company)

    new_user = User(
        email=user_data.email,
        password = hash_password(user_data.password),
        company_id = company.id,
        role="owner",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise ValueError("Invalid email or password")
    if not verify_password(password, user.password):
        raise ValueError("Invalid email or password")

    token = create_access_token({"sub": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
    }

def invite_user(db: Session, data: UserInvite, current_user: User):
    # Check If User Already Exists
    existing_user = db.query(User).filter(User.email == data.email).first()

    if existing_user:
        raise ValueError("User already Exists")

    # Create User In SAME Company
    new_user = User(
        email=data.email,
        password=hash_password(data.password),
        company_id=current_user.company_id,
        role=data.role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user