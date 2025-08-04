from fastapi import APIRouter

router = APIRouter()

@router.get("/users/", tags=["users"])
async def read_users():
    return [{"username": "eiei"}, {"username": "Ishi"}, {"username": "miyaso"}]