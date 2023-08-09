from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_name_duplicate, \
    check_charity_project_exists, check_new_full_amount_bigger_previous, \
    check_project_already_invested, check_project_is_fully_invested, check_empty_fields
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import CharityProjectDB, CharityProjectCreate, \
    CharityProjectUpdate

router = APIRouter()


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(
        session: AsyncSession = Depends(get_async_session),
):
    # Замените вызов функции на вызов метода.
    all_rooms = await charity_project_crud.get_multi(session)
    return all_rooms


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_new_charity_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    await check_name_duplicate(charity_project.name, session)
    check_empty_fields(charity_project.dict())
    # Замените вызов функции на вызов метода.
    new_project = await charity_project_crud.create(charity_project, session)
    return new_project


@router.patch('/{project_id}',
              response_model=CharityProjectDB,
              dependencies=[Depends(current_superuser)],)
async def update_project(
        project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    project = await check_charity_project_exists(
        project_id, session
    )
    check_empty_fields(obj_in.dict())
    check_project_is_fully_invested(project)
    # Проверяем, что нет пересечений с другими бронированиями.
    if project.name is not None:
        await check_name_duplicate(obj_in.name, session)
    if obj_in.full_amount:
        check_new_full_amount_bigger_previous(
            project,
            obj_in.full_amount,
        )
    # Замените вызов функции на вызов метода.
    project = await charity_project_crud.update(
        project, obj_in, session
    )
    return project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def remove_charity_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    project = await check_charity_project_exists(
        project_id, session
    )
    check_project_already_invested(project)
    # Замените вызов функции на вызов метода.
    meeting_room = await charity_project_crud.remove(project, session)
    return meeting_room
