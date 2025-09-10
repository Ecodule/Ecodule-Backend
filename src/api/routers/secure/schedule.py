from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

import core.auth as auth
import crud.schedule
from crud.user import get_user_by_email
from schemas.schedule import ScheduleResponse, ScheduleCreate, ScheduleUpdate

from db.session import get_db

router = APIRouter(
    tags=["schedules"],          # このルーターのタグを統一
    dependencies=[Depends(auth.get_current_user)]
)

# スケジュールを作成
@router.post("/users/{user_id}/schedules", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
def get_user_schedules(user_id: uuid.UUID, schedule: ScheduleCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.schedule.create_schedule(db=db, schedule=schedule, user_id=user_id)

# ユーザーのスケジュール一覧を取得
@router.get("/users/{user_id}/schedules", response_model=List[ScheduleResponse])
def get_user_schedules(user_id: uuid.UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    schedules = crud.schedule.get_schedules_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return schedules

# 単一のスケジュールを取得
@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
def read_schedule(schedule_id: uuid.UUID, db: Session = Depends(get_db)):
    db_schedule = crud.schedule.get_schedule(db, schedule_id=schedule_id)
    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return db_schedule

# スケジュールを更新
@router.put("/schedules/{schedule_id}", response_model=ScheduleResponse)
def update_schedule(schedule_id: uuid.UUID, schedule: ScheduleUpdate, db: Session = Depends(get_db)):
    db_schedule = crud.schedule.update_schedule(db, schedule_id=schedule_id, schedule_update=schedule)
    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return db_schedule

# スケジュールを削除
@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(schedule_id: uuid.UUID, db: Session = Depends(get_db)):
    db_schedule = crud.schedule.delete_schedule(db, schedule_id=schedule_id)
    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return None