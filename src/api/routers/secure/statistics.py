from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db

import core.auth as auth
from crud.statistics import get_user_statistics
from models.user import User as UserModel
from core.auth import get_current_user
from schemas.statistics import UserStatsResponse


router = APIRouter(
    prefix="/users/me/statistics", # このルーターの共通プレフィックス
    tags=["statistics"],          # このルーターのタグを統一
    dependencies=[Depends(auth.get_current_user)]
)

@router.get("/mock_data")
def get_statistics():
  return {
    "apples": "26",
    "CO2_saved": "1.23",
    "money_saved": "1234",
    "last_money_saved": "12345",
    "total_CO2_saved": "12.34",
  }

@router.get("/", response_model=UserStatsResponse)
def read_user_statistics(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    ログイン中のユーザーの個人統計を取得します。
    """
    return get_user_statistics(db=db, user_id=current_user.id)