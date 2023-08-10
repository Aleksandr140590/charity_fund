from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Donation, CharityProject


async def get_first_unclosed_donation(
        session: AsyncSession
) -> Optional[Donation]:
    donations = await session.execute(select(Donation).where(
        Donation.fully_invested == 0
    ))
    return donations.scalars().first()


async def get_all_unclosed_projects(
        session: AsyncSession
) -> Optional[List[CharityProject]]:
    projects = await session.execute(select(CharityProject).where(
        CharityProject.fully_invested == 0
    ))
    return projects.scalars().all()


def project_donating(project: CharityProject, donation_amount: int,
                     session: AsyncSession) -> int:
    needed_amount = project.full_amount - project.invested_amount
    if donation_amount >= needed_amount:
        donation_amount -= needed_amount
        project.invested_amount = project.full_amount
        project.fully_invested = True
        project.close_date = datetime.now()
    else:
        project.invested_amount += donation_amount
        donation_amount = 0
    session.add(project)
    return donation_amount


def donation_change_invested_amount_closing(
        donation: Donation,
        remaining_amount: int,
        session: AsyncSession
) -> None:
    donation.invested_amount = (donation.full_amount -
                                remaining_amount)
    if donation.invested_amount == donation.full_amount:
        donation.fully_invested = True
        donation.close_date = datetime.now()
    session.add(donation)


async def investing(
        session: AsyncSession
):
    while True:

        donation = await get_first_unclosed_donation(session)
        projects = await get_all_unclosed_projects(session)
        if not donation or not projects:
            break
        available_donation_amount = (donation.full_amount -
                                     donation.invested_amount)
        for project in projects:
            if available_donation_amount == 0:
                break
            available_donation_amount = project_donating(
                project,
                available_donation_amount,
                session
            )
        donation_change_invested_amount_closing(
            donation,
            available_donation_amount,
            session
        )
        await session.commit()
