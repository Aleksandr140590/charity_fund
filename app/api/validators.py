from typing import Dict

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject


async def check_name_duplicate(
        project_name: str | None,
        session: AsyncSession,
) -> None:
    project_id = await charity_project_crud.get_project_id_by_name(
        project_name,
        session
    )
    if project_id:
        raise HTTPException(
            status_code=400,
            detail='Проект с таким именем уже существует!',
        )


async def check_charity_project_exists(
        charity_project_id: int,
        session: AsyncSession,
) -> CharityProject:
    charity_project = await charity_project_crud.get(charity_project_id,
                                                     session)
    if not charity_project:
        raise HTTPException(
            status_code=404,
            detail='Проект не найден!'
        )
    return charity_project


def check_project_is_fully_invested(
        charity_project: CharityProject,
):
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail='Закрытый проект нельзя редактировать!',
        )


def check_new_full_amount_bigger_previous(
        charity_project: CharityProject,
        new_value_full_amount: int,
):
    if charity_project.invested_amount > new_value_full_amount:
        raise HTTPException(
            status_code=422,
            detail='Новая сумма не может быть меньше внесенной!',
        )


def check_project_already_invested(
        charity_project: CharityProject,
):
    if charity_project.invested_amount > 0:
        raise HTTPException(
            status_code=400,
            detail='В проект были внесены средства, не подлежит удалению!',
        )


def check_empty_fields(obj_data: Dict):
    if '' in obj_data.values():
        raise HTTPException(
            status_code=422,
            detail='Нельзя назначать пустое поле.',
        )
