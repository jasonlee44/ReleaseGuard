from fastapi import APIRouter
from app.schemas.build import Build, BuildCreate
from app.services.build_service import create_build, list_builds

router = APIRouter()

@router.post("/builds")
async def create_new_build(payload: BuildCreate) -> Build:
    return create_build(payload)

@router.get("/builds")
async def get_builds() -> list[Build]:
    return list_builds()