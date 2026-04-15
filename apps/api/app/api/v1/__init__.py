from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.phase2 import router as phase2_router
from app.api.v1.phase3 import router as phase3_router
from app.api.v1.phase4 import router as phase4_router
from app.api.v1.users import router as users_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(phase2_router)
router.include_router(phase3_router)
router.include_router(phase4_router)
