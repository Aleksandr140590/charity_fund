from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Donation, CharityProject


async def investing(
        session: AsyncSession
):
    while True:

        donations = await session.execute(select(Donation).where(
            Donation.fully_invested == 0
        ))
        donation = donations.scalars().first()
        if not donation:
            break
        available_donation = donation.full_amount - donation.invested_amount
        projects = await session.execute(select(CharityProject).where(
            CharityProject.fully_invested == 0
        ))
        projects = projects.scalars().all()
        if not projects:
            break
        for project in projects:
            if available_donation == 0:
                break
            needed_amount = project.full_amount - project.invested_amount
            if available_donation >= needed_amount:
                available_donation -= needed_amount
                project.invested_amount = project.full_amount
                project.fully_invested = True
                project.close_date = datetime.now()
            else:
                project.invested_amount += available_donation
                available_donation = 0
            session.add(project)
        donation.invested_amount = donation.full_amount - available_donation
        if donation.invested_amount == donation.full_amount:
            donation.fully_invested = True
            donation.close_date = datetime.now()
        session.add(donation)
        await session.commit()
