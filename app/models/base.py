from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, CheckConstraint, Boolean

from app.core.db import Base


class DonationCharityBase(Base):
    __abstract__ = True
    full_amount = Column(Integer, CheckConstraint('full_amount > 0'),
                         nullable=False)
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime)
