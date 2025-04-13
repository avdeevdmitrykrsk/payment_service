import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.schemas.user import UserCreate, UserRead
from app.services.payment.admin_crud import AdminCRUD, get_admin_crud
from app.services.payment.schemas import ReturnAccountSchema

router = APIRouter(prefix='/admin')

logger = logging.getLogger(__name__)


@router.post(
    '/users',
    dependencies=(Depends(current_superuser),),
    response_model=UserRead,
)
async def create_user(
    user_data: UserCreate,
    admin_crud: AdminCRUD = Depends(get_admin_crud),
):
    logger.info('ADMIN! Запрос на создание пользователя принят')
    return await admin_crud.create_user(user_data=user_data)


@router.get(
    '/users',
    dependencies=(Depends(current_superuser),),
    response_model=list[UserRead],
)
async def get_user_list(
    session: AsyncSession = Depends(get_async_session),
    admin_crud: AdminCRUD = Depends(get_admin_crud),
):
    logger.info('ADMIN! Запрос на получение списка пользователей принят')
    return await admin_crud.get_user_list(session)


@router.get(
    '/users/{user_id}/accounts',
    dependencies=(Depends(current_superuser),),
    response_model=list[ReturnAccountSchema],
)
async def get_user_list(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    admin_crud: AdminCRUD = Depends(get_admin_crud),
):
    logger.info(
        'ADMIN! Запрос на получение списка аккаунтов пользователя принят'
    )
    return await admin_crud.get_user_accounts(session=session, user_id=user_id)
