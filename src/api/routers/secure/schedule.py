from fastapi import APIRouter, Depends

import core.auth as auth

router = APIRouter(
    tags=["schedules"],          # このルーターのタグを統一
    dependencies=[Depends(auth.get_current_user)]
)

@router.get("/users/schedules")
def get_user_schedules():
    return {
        "schedules": []
    }