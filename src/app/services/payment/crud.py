# Standart lib imports
import logging
from typing import List, Union

# Thirdparty imports
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

# Projects imports
from app.services.payment.config import Account, Payment

logger = logging.getLogger(__name__)


class BaseCRUD:

    def __init__(self, model):
        self.model = model

    async def _get_all(self, session: AsyncSession, stmt: Select) -> List:
        result = await session.execute(stmt)
        logger.info('Список получен')
        return result.scalars().all()


class AccountCRUD(BaseCRUD):

    async def get_accounts(self, session: AsyncSession, user_id: int) -> List:
        stmt = select(self.model).where(self.model.user_id == user_id)
        logger.info('Получение списка аккаунтов')
        return await self._get_all(session=session, stmt=stmt)

    async def create(self, session: AsyncSession, user_id: int):
        logger.info('Создание нового аккаунта')
        instance = self.model(user_id=user_id)
        session.add(instance)
        await session.flush()

        logger.info('Аккаунт создан')
        return instance

    async def get_or_create_account(
        self,
        user_id: int,
        session: AsyncSession,
        account_id: int,
    ) -> Union[Account, Payment]:
        """Метод получает или создает аккаунт пользователя."""
        logger.info('Получение аккаунта пользователя')
        result = await session.execute(
            select(self.model).where(
                and_(
                    self.model.user_id == user_id,
                    self.model.id == account_id,
                )
            )
        )
        instance = result.scalars().first()

        if not instance:
            logger.info('Аккаунт не найден')
            return await self.create(session=session, user_id=user_id)

        logger.info('Аккаунт найден.')
        return instance


class PaymentCRUD(BaseCRUD):

    async def get_payments(self, session: AsyncSession, user_id: int) -> List:
        stmt = (
            select(self.model)
            .join(self.model.account)
            .where(Account.user_id == user_id)
        )
        logger.info('Получение списка платежей')
        return await self._get_all(session=session, stmt=stmt)


async def get_account_crud() -> AccountCRUD:
    return AccountCRUD(Account)


async def get_payment_crud() -> PaymentCRUD:
    return PaymentCRUD(Payment)
