# Standart lib imports
import hashlib
import hmac
import logging
import os
from decimal import Decimal

# Thirdparty imports
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError

# Projects imports
from app.services.payment.config import Account, Payment
from app.services.payment.schemas import (
    PaymentAccountBalanceResponse,
    PaymentResponse,
    PaymentSchema,
    PaymentTransactionResponse,
)

load_dotenv()

logger = logging.getLogger(__name__)


class PaymentService:

    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    async def _generate_signature(self, data: dict) -> str:
        """Метод генерирует подпись."""
        logger.info('Генерация ожидаемой подписи')
        data_without_sign = {k: v for k, v in data.items() if k != 'signature'}

        sorted_keys = sorted(data_without_sign.keys())
        concatenated = ''.join(
            str(data_without_sign[key]) for key in sorted_keys
        )
        message = concatenated + self.secret_key

        return hashlib.sha256(message.encode()).hexdigest()

    async def verify_signature(self, data: dict):
        """Метод проверяет подпись."""
        logger.info('Проверка подписи платежа')
        expected_sign = await self._generate_signature(data)
        if not hmac.compare_digest(expected_sign, data['signature']):
            logger.warning('Подпись невалидна')
            raise HTTPException(status.HTTP_403_FORBIDDEN, 'Invalid signature')

    async def create_transaction(
        self,
        account_id: int,
        transaction_id: str,
        amount: Decimal,
        session: AsyncSession,
    ) -> Payment:
        """Метод создает запись о транзакции."""
        instance = await session.execute(
            select(Payment).where(Payment.transaction_id == transaction_id)
        )

        logger.info('Проверка дубликатов')
        if instance.scalars().first():
            logger.warning('Данная транзакция уже обработана')
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Transaction already processed',
            )
        logger.info('Дубликатов не найдено')

        transaction = Payment(
            account_id=account_id,
            transaction_id=transaction_id,
            payment_amount=amount,
        )

        session.add(transaction)
        await session.flush()

        return transaction

    async def update_account_balance(
        self, session: AsyncSession, account: Account, amount: Decimal
    ):
        """Метод обновляет баланс счета."""
        locked_account = await session.execute(
            select(Account)
            .where(Account.id == account.id)
            .with_for_update()
            .execution_options(postgresql_lock_timeout=1.0)
        )
        locked_account = locked_account.scalars().one()

        locked_account.balance += amount

    def _build_response(
        self, account: Account, transaction: Payment
    ) -> PaymentResponse:
        return PaymentResponse(
            status='completed',
            transaction=PaymentTransactionResponse(
                transaction_id=transaction.transaction_id,
                amount=transaction.payment_amount,
            ),
            account=PaymentAccountBalanceResponse(
                account_id=account.id, new_balance=account.balance
            ),
        )

    async def process_transaction(
        self,
        session: AsyncSession,
        payment_dict: PaymentSchema,
        account: Account,
    ) -> dict:

        logger.info('Начат процесс транзакции')

        await self.verify_signature(payment_dict)
        logger.info('Подпись успешно проверена')

        logger.info('Созданине записи о платеже')
        transaction = await self.create_transaction(
            session=session,
            account_id=account.id,
            transaction_id=payment_dict['transaction_id'],
            amount=payment_dict['amount'],
        )
        logger.info('Запись о платеже успешно создана')

        try:
            logger.info('Обновление баланса аккаунта')
            await self.update_account_balance(
                session=session,
                account=account,
                amount=transaction.payment_amount,
            )
            await session.commit()
            logger.info('Баланс успешно обновлен')

        except OperationalError as e:
            if 'lock timeout' in str(e).lower():
                logger.error('Ошибка обновления lock-timeout')
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail='System busy. Please retry in a moment'
                )
            raise

        logger.info('Генерация ответа')
        return self._build_response(account=account, transaction=transaction)


async def get_secret_key():
    """Возвращает SECRET_KEY из переменных окружения."""
    return os.getenv('SECRET_KEY')


async def get_payment_service(
    secret_key: str = Depends(get_secret_key),
) -> PaymentService:
    return PaymentService(secret_key=secret_key)
