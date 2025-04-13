import contextlib

from fastapi_users.exceptions import UserAlreadyExists
from pydantic import EmailStr

from app.core.config import settings
from app.core.db import get_async_session
from app.core.user import get_user_db, get_user_manager
from app.services.payment.config import Account
from app.schemas.user import UserCreate

get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(
    email: EmailStr,
    password: str,
    is_superuser: bool = False,
    make_account=False,
):
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:

                    user = await user_manager.create(
                        UserCreate(
                            email=email,
                            password=password,
                            is_superuser=is_superuser,
                        )
                    )

                    if make_account:
                        account = Account(user_id=user.id)
                        session.add(account)
                        await session.commit()

    except UserAlreadyExists:
        pass


async def create_first_superuser():
    if (
        settings.first_superuser_email is not None
        and settings.first_superuser_password is not None
    ):
        await create_user(
            email=settings.first_superuser_email,
            password=settings.first_superuser_password,
            is_superuser=True,
        )
