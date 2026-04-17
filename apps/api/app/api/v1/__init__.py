from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.calendar import router as calendar_router
from app.api.v1.domain import router as domain_router
from app.api.v1.focus import router as focus_router
from app.api.v1.planning import router as planning_router
from app.api.v1.reminders import router as reminders_router
from app.api.v1.settings import router as settings_router
from app.api.v1.users import router as users_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(calendar_router)
router.include_router(users_router)
router.include_router(domain_router)
router.include_router(focus_router)
router.include_router(planning_router)
router.include_router(reminders_router)
router.include_router(settings_router)
