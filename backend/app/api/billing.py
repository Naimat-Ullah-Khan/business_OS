from anyio import current_effective_deadline
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.company import Company
from app.services import billing_service

router = APIRouter(prefix="/billing", tags=["Billing"])


class CheckoutRequest(BaseModel):
    plan_name: str
    success_url: str = "http://localhost:3000/billing/success"
    cancel_url: str = "http://localhost:3000/billing/cancel"

@router.post("/create-checkout-session")
def create_checkout_session(
    data: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = db.query(Company).filter(Company.id == current_user.company.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    try:
        url = billing_service.create_checkout_session(
            db, company, data.plan_name, data.success_url, data.cancel_url
        )
        return {"checkout_url": url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/subscription-status")
def get_subscription_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = db.query(Company).filter(Company.id == current_user.company.id).first()
    return {
        "plan": company.plan.name if company.plan else "free",
        "subscription_status": company.subscription_status,
        "stripe_subscription_id": company.stripe_subscription_id,
    }