from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    stripe_price_id = Column(String, nullable=True)