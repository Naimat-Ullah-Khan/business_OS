from sqlalchemy.orm import Session
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate

def create_expense(db: Session, data: ExpenseCreate, company_id: int):
    expense = Expense(
        title=data.title,
        amount=data.amount,
        company_id=company_id,
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense

def get_expenses(db: Session, company_id: int):
    return db.query(Expense).filter(Expense.company_id == company_id).all()