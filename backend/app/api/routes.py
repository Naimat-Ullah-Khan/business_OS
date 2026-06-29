from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, require_role, rate_limit_by_ip
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token, UserInvite
from app.schemas.company import CompanyCreate, CompanyResponse
from app.schemas.expense import ExpenseCreate, ExpenseResponse
from app.services.user_service import create_user, login_user, invite_user
from app.services.company_service import create_company
from app.services.expense_service import create_expense, get_expenses
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, dependencies=[Depends(rate_limit_by_ip(limit=5, window=60))])
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token, dependencies=[Depends(rate_limit_by_ip(limit=5, window=60))])
def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
        return login_user(db, user.email, user.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email
    }


@router.post("/companies", response_model=CompanyResponse)
def create_new_company(data: CompanyCreate, db: Session = Depends(get_db)):
    return create_company(db, data)


# CREATE EXPENSE
@router.post("/expenses", response_model=ExpenseResponse)
def create_expense_api(data: ExpenseCreate, db: Session = Depends(get_db),
                       current_user: User = Depends(require_role(["owner", "admin"])),
                       _: User = Depends(require_role(["pro", "enterprise"]))):
    return create_expense(db, data, current_user.company_id)


# GET EXPENSE
@router.get("/expenses", response_model=list[ExpenseResponse])
def get_expenses_api(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_expenses(db, current_user.company_id)


@router.post("/users/invite", response_model=UserResponse)
def invite_user_api(data: UserInvite, db: Session = Depends(get_db),
                    current_user: User = Depends(require_role(["owner", "admin"]))):
    try:
        return invite_user(db, data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
