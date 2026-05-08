from sqlalchemy import Column, Integer,String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    plan_id = Column(Integer, ForeignKey('plans.id'))
    plan = relationship("Plan")