import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user
from app.models import User
from app.services.payment.crud import (
    AccountCRUD,
    PaymentCRUD,
    get_account_crud,
    get_payment_crud,
)
from app.services.payment.schemas import (
    PaymentResponse,
    PaymentSchema,
    ReturnAccountSchema,
    ReturnPaymentSchema,
)
from app.services.payment.utils import PaymentService, get_payment_service

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post('/payment')
async def handle_payment(
    payment_data: PaymentSchema,
    service: PaymentService = Depends(get_payment_service),
    crud: AccountCRUD = Depends(get_account_crud),
    session: AsyncSession = Depends(get_async_session),
) -> PaymentResponse:
    logging.info('Обработка нового платежа')
    payment_dict = payment_data.dict()

    account = await crud.get_or_create_account(
        session=session,
        user_id=payment_dict['user_id'],
        account_id=payment_dict['account_id'],
    )

    return await service.process_transaction(
        session=session,
        payment_dict=payment_dict,
        account=account,
    )


@router.get(
    '/payment',
    response_model=List[ReturnPaymentSchema],
)
async def get_user_payments(
    session: AsyncSession = Depends(get_async_session),
    payment_crud: PaymentCRUD = Depends(get_payment_crud),
    user: User = Depends(current_user),
) -> List[ReturnPaymentSchema]:
    logger.info('Запрос на получение списка платежей принят')
    return await payment_crud.get_payments(session=session, user_id=user.id)


@router.get(
    '/account',
    response_model=List[ReturnAccountSchema],
)
async def get_user_accounts(
    session: AsyncSession = Depends(get_async_session),
    account_crud: AccountCRUD = Depends(get_account_crud),
    user: User = Depends(current_user),
) -> List[ReturnAccountSchema]:
    logger.info('Запрос на получение списка аккаунтов принят')
    return await account_crud.get_accounts(session=session, user_id=user.id)
