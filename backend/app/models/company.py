from sqlalchemy import Column, Integer,String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    plan_id = Column(Integer, ForeignKey('plans.id'))
    plan = relationship("Plan")

    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True )
    subscription_status = Column(String, nullable=True, default="free")