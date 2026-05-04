from fastapi import FastAPI
from app.api.routes import router
app = FastAPI(title="Business OS API")

app.include_router(router)

@app.get("/")
def root():
    return {"message": "Business OS API is running 🚀"}