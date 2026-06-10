from fastapi import APIRouter, Request, HTTPException, Header
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.services import billing_service
from fastapi import Depends
from typing import Optional

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/stripe")
async def stripr_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    payload = await request.body()
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")
    try:
        result = billing_service.handle_webhook(db, payload, stripe_signature)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))