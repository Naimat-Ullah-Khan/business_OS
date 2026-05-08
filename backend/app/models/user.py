from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    company_id = Column(Integer, ForeignKey('companies.id'))
    company = relationship("Company")

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False, )
    is_active = Column(Boolean, default=True)
    role = Column(String, default='owner')