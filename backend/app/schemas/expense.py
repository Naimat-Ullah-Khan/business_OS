from pydantic import BaseModel

class ExpenseCreate(BaseModel):
    title: str
    amount: int

class ExpenseResponse(BaseModel):
    id: int
    title: str
    amount: int

    class Config:
        from_attributes = True