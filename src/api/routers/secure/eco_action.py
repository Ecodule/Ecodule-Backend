from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from db.session import get_db
from core.auth import get_current_user
from schemas.eco_action import EcoActionResponse
from models.eco_action import EcoAction

router = APIRouter(
    tags=["eco_actions"],          # このルーターのタグを統一
    dependencies=[Depends(get_current_user)]
)

@router.get("/eco_actions", response_model=list[EcoActionResponse])
def read_eco_actions(db: Session = Depends(get_db)):
    eco_actions = db.query(EcoAction).all()

    return eco_actions
