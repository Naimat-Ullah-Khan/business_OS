import stripe
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.company import Company
from app.models.plan import Plan
from app.models.webhook_event import WebhookEvent

stripe.api_key = settings.STRIPE_SECRET_KEY

def get_or_create_stripe_customer(db: Session, company: Company) ->str:
    if company.stripe_customer_id:
        return company.stripe_customer_id
    customer = stripe.Customer.create(
        name=company.name,
        metadata={"company_id": company.id},
    )
    company.stripe_customer_id = customer.id
    db.commit()
    return customer.id


def create_checkout_session(db: Session, company: Company, plan_name: str, success_url: str, cancel_url: str) -> str:
    plan = db.query(Plan).filter(Plan.name == plan_name).first()
    if not plan or not plan.stripe_price_id:
        raise ValueError(f"{plan_name} not found or has no Stripe Price")

    customer_id = get_or_create_stripe_customer(db, company)

    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{"price": plan.stripe_price_id, "quantity": 1}],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"company_id": str(company.id), "plan_name": plan_name},
    )
    return session.url

def handle_webhook(db: Session, payload: bytes, sig_header: str) -> dict :
    try:
        event = stripe.webhook.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except ValueError:
        raise ValueError("Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise ValueError("Invalid signature")

    # Idempotency — skip if already processed
    existing = db.query(WebhookEvent).filter(WebhookEvent.stripe_event_id == event["id"]).first()
    if existing:
        return {"status": "already_processed"}

    # Record the event BEFORE processing
    db.add(WebhookEvent(stripe_event_id=event["id"], event_type=event["type"]))
    db.commit()

    if event["type"] == "checkout.session.completed":
        _handle_checkout_completed(db, event["data"]["object"])
    elif event["type"] == "customer.subscription.deleted":
        _handle_subscription_deleted(db, event["data"]["object"])
    elif event["type"] == "invoice.payment_failed":
        _handle_payment_failed(db, event["data"]["object"])

    return {"status": "processed"}

def _handle_checkout_completed(db: Session, session):
    company_id = int(session["metadata"]["company_id"])
    plan_name = session["metadata"]["plan_name"]
    subscription_id = session["subscription"]

    company = db.query(Company).filter(Company.id == company_id).first()
    plan = db.query(Plan).filter(Plan.name == plan_name).first()
    if company and plan:
        company.plan_id = plan.id
        company.stripe_subscription_id = subscription_id
        company.subscription_status = "active"
        db.commit()

def _handle_subscription_deleted(db: Session, subscription):
    company = db.query(Company).filter(
        Company.stripe_subscription_id == subscription["id"]
    ).first()
    if company:
        free_plan = db.query(Plan).filter(Plan.name == "free").first()
        company.plan_id = free_plan.id
        company.stripe_subscription_id = None
        company.subscription_status = "free"
        db.commit()

def _handle_payment_failed(db: Session, invoice):
    company = db.query(Company).filter(
        Company.stripe_customer_id == invoice["customer"]
    ).first()
    if company:
        company.subscription_status = "past_due"
        db.commit()