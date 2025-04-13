from fastapi import FastAPI

from app.api.routers import main_router
from app.core.db__init__ import create_first_superuser, create_user
from app.core.config import settings, setup_logging

app = FastAPI()
app.include_router(main_router)


@app.on_event('startup')
async def startup():
    await create_user(
        email=settings.test_user_email,
        password=settings.test_user_password,
        make_account=True,
    )
    await create_first_superuser()

logger = setup_logging()
