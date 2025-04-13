from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, validator, Field


class PaymentSchema(BaseModel):
    """pydantic-схема для получения данных о платеже."""

    transaction_id: str
    account_id: int
    user_id: int
    amount: Decimal = Field(..., gt=0)
    signature: str

    @validator('amount')
    def round_amount(cls, value: Decimal) -> Decimal:
        """Округляет значение до 2 знаков после запятой"""
        return value.quantize(Decimal('0.00'))


class ReturnPaymentSchema(BaseModel):

    id: int
    transaction_id: str
    account_id: int
    payment_amount: Decimal

    class Config:
        orm_mode = True


class ReturnAccountSchema(BaseModel):

    id: int
    user_id: int
    balance: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class PaymentTransactionResponse(BaseModel):
    transaction_id: str
    amount: Decimal


class PaymentAccountBalanceResponse(BaseModel):
    account_id: int
    new_balance: Decimal


class PaymentResponse(BaseModel):
    status: str
    transaction: PaymentTransactionResponse
    account: PaymentAccountBalanceResponse
