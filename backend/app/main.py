from fastapi import FastAPI
from app.api.routes import router
from app.api.billing import router as billing_router
from app.api.webhooks import router as webhooks_router

app = FastAPI(title="Business OS API")

app.include_router(router)
app.include_router(billing_router)
app.include_router(webhooks_router)

@app.get("/")
def root():
    return {"message": "Business OS API is running 🚀"}