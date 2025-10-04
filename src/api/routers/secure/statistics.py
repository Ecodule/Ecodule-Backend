# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session

# from db.session import get_db

# import core.auth as auth
# from crud.statistics import get_user_statistics
# from models.user import User as UserModel
# from models.overall_statistics import OverallStats as OverallStatsModel
# from core.auth import get_current_user
# from schemas.statistics import UserStatsResponse, OverallStatsResponse



# router = APIRouter(
#     tags=["statistics"],          # このルーターのタグを統一
#     dependencies=[Depends(auth.get_current_user)]
# )

# @router.get("/statistics/mock_data")
# def get_statistics():
#   return {
#     "apples": "26",
#     "CO2_saved": "1.23",
#     "money_saved": "1234",
#     "last_money_saved": "12345",
#     "total_CO2_saved": "12.34",
#   }

# @router.get("/users/me/statistics", response_model=UserStatsResponse)
# def read_user_statistics(
#     db: Session = Depends(get_db),
#     current_user: UserModel = Depends(get_current_user)
# ):
#     """
#     ログイン中のユーザーの個人統計を取得します。
#     """
#     return get_user_statistics(db=db, user_id=current_user.id)

# @router.get("/users/statistics", response_model=OverallStatsResponse)
# def read_overall_statistics(
#     db: Session = Depends(get_db)
# ):
#     """
#     全体統計の最新の集計結果を取得します。
#     """
#     # 最新の統計レコードを1件取得
#     latest_stats = db.query(OverallStatsModel).order_by(OverallStatsModel.calculated_at.desc()).first()

#     if not latest_stats:
#         return {"total_money_saved": 0.0, "total_co2_reduction": 0.0}
    
#     return latest_stats