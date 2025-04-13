"""Импорты класса Base и всех моделей для Alembic."""
from app.core.db import Base  # noqa
from app.models import User  # noqa
from app.services.payment import Account, Payment  # noqa
