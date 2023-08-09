from datetime import datetime

from pydantic import BaseModel, PositiveInt, Extra
from typing import Optional


class DonationCreate(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str]

    class Config:
        extra = Extra.forbid


class DonationDB(DonationCreate):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]
    user_id: int

    class Config:
        orm_mode = True
