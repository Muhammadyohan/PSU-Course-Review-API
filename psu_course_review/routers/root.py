from fastapi import APIRouter


router = APIRouter()


@router.get("/")
async def index() -> dict:
    return dict(message="PSU Event Hub API")
