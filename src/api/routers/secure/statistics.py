from fastapi import APIRouter, Depends

import core.auth as auth

router = APIRouter(
    tags=["statistics"],          # このルーターのタグを統一
    dependencies=[Depends(auth.get_current_user)]
)

@router.get("/users/statistics")
def get_user_statistics():
  return {
    "apples": "26",
    "CO2_saved": "1.23",
    "money_saved": "1234",
    "last_money_saved": "12345",
    "total_CO2_saved": "12345678"
  }