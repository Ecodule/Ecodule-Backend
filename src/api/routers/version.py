from fastapi import APIRouter

router = APIRouter(
    tags=["version"]
)

@router.get("/version")
def get_version():
    return {"version": "2025-09-15T22:00:00+09:00"}