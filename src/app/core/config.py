# Standart lib imports
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Thirdparty imports
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()

LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)


class Settings(BaseSettings):
    """Базовые настройки для микросервиса."""

    # project
    debug_mode: bool = os.getenv('DEBUG')
    secret_key: str = os.getenv('SECRET_KEY')
    # postgres
    database_url: str = os.getenv('DATABASE_URL')
    postgres_db: str = os.getenv('POSTGRES_DB')
    postgres_user: str = os.getenv('POSTGRES_USER')
    postgres_password: str = os.getenv('POSTGRES_PASSWORD')
    db_host: str = os.getenv('DB_HOST')
    db_port: str = os.getenv('DB_PORT')
    # superuser credentials
    first_superuser_email: str = os.getenv('FIRST_SUPERUSER_EMAIL')
    first_superuser_password: str = os.getenv('FIRST_SUPERUSER_PASSWORD')
    # test user credentials
    test_user_email: str = os.getenv('TEST_USER_EMAIL')
    test_user_password: str = os.getenv('TEST_USER_PASSWORD')

    class Config:
        env_file: str = '.env'

    @property
    def async_database_url(self) -> str:
        """Строка асинхронного подключения к postgres DB."""
        if not self.debug_mode:
            return (
                f'postgresql+asyncpg://'
                f'{self.postgres_user}:{self.postgres_password}'
                f'@{self.db_host}:{self.db_port}/{self.postgres_db}'
            )

        return 'sqlite+aiosqlite:///payments.db'


def setup_logging():
    """Настройка логгера."""

    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        filename=LOG_DIR / 'app.log', encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


settings = Settings()
