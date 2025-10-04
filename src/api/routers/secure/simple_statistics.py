# APIエンドポイントのための最低限のインポート

import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db

# 認証モジュールをインポート
import core.auth as auth

# 統計関連のスキーマをインポート
from schemas.statistics import (
    UserStatsResponse, 
    OverallStatsResponse,
    UpdateStatsRequest
)

# 統計関連のCRUD操作をインポート
from crud.simple_statistics import (
    read_user_statistics,
    read_overall_statistics,
    create_user_statistics,
    update_user_statistics,
    update_overall_statistics
)

router = APIRouter(
    tags=["statistics"],          # このルーターのタグを統一
    dependencies=[Depends(auth.get_current_user)]
)

@router.get("/{user_id}/simple_statistics", response_model=UserStatsResponse)
def get_user_statistics(user_id: uuid.UUID, db: Session = Depends(get_db)):
    stats = ensure_user_statistics_exists(db, user_id)

    return stats

@router.get("/overall_statistics", response_model=OverallStatsResponse)
def get_overall_statistics(db: Session = Depends(get_db)):
    stats = read_overall_statistics(db)

    return stats

@router.post("/{user_id}/simple_statistics", response_model=UserStatsResponse)
def post_achievement(user_id: uuid.UUID, achieved: UpdateStatsRequest, db: Session = Depends(get_db)):
    stats = ensure_user_statistics_exists(db, user_id)

    stats = update_user_statistics(db, user_id, achieved.money_saved, achieved.co2_reduction)
    overall_stats = update_overall_statistics(db, achieved.money_saved, achieved.co2_reduction)

    return stats

# 統計が存在しない場合に作成するユーティリティ関数
def ensure_user_statistics_exists(db: Session, user_id: uuid.UUID):
    stats = read_user_statistics(db, user_id)

    if not stats:
        stats = create_user_statistics(db, user_id)
    return stats
