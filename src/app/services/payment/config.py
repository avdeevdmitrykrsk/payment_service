from decimal import Decimal

from sqlalchemy import Column, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship

from app.core.db import Base

DEFAULT_ACCOUNT_BALANCE = Decimal('0.00')
BALANCE_PRECISION: int = 12
BALANCE_SCALE: int = 2


class Account(Base):
    """Модель финансового аккаунта пользователя."""

    balance = Column(
        Numeric(BALANCE_PRECISION, BALANCE_SCALE, asdecimal=True),
        default=DEFAULT_ACCOUNT_BALANCE,
        server_default='0.00',
        nullable=False,
    )
    user_id = Column(ForeignKey('user.id'))
    user = relationship('User', back_populates='accounts')
    payments = relationship(
        'Payment',
        back_populates='account',
    )


class Payment(Base):
    """Модель 'Платежа' пользователя."""

    transaction_id = Column(Integer, unique=True, nullable=False, index=True)
    account_id = Column(ForeignKey('account.id'))
    account = relationship('Account', back_populates='payments')
    payment_amount = Column(
        Numeric(BALANCE_PRECISION, BALANCE_SCALE, asdecimal=True),
        default=DEFAULT_ACCOUNT_BALANCE,
        server_default='0.00',
        nullable=False,
    )
