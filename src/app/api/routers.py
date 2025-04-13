from fastapi import APIRouter

from app.api.endpoints import user_router
from app.services.payment import admin_router, payment_router

main_router = APIRouter(prefix='/api')
main_router.include_router(user_router)
main_router.include_router(admin_router)
main_router.include_router(payment_router)
