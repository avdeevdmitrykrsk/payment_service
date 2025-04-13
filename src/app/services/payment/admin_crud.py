# Standart lib imports
import logging
from typing import List

# Thirdparty imports
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi_users.exceptions import UserAlreadyExists
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User

# Projects imports
from app.core.user import get_user_manager, UserManager
from app.schemas.user import UserCreate, UserRead
from app.services.payment.config import Account

logger = logging.getLogger(__name__)


class AdminCRUD:

    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager

    async def create_user(
        self,
        user_data: UserCreate,
    ) -> UserRead:
        logger.info('ADMIN! Создание пользователя')
        try:
            user = await self.user_manager.create(user_data)
            logger.info(f'ADMIN! Пользователь {user.email} успешно создан')

            return user

        except UserAlreadyExists:
            logger.warning('ADMIN! Пользователь с данным email уже сущесвует')
            raise HTTPException(
                detail='Пользователь с данным email уже сущесвует',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    async def get_user_list(self, session: AsyncSession) -> List:
        logger.info('ADMIN! Получение списка пользователей')
        result = await session.execute(select(User))

        logger.info('ADMIN! Список получен')
        return result.scalars().all()

    async def get_user_accounts(
        self, session: AsyncSession, user_id: int
    ) -> List:
        logger.info('ADMIN! Получение списка аккаунтов')
        result = await session.execute(
            select(Account).where(Account.user_id == user_id)
        )

        logger.info('ADMIN! Список получен')
        return result.scalars().all()


async def get_admin_crud(user_manager=Depends(get_user_manager)) -> AdminCRUD:
    return AdminCRUD(user_manager)
