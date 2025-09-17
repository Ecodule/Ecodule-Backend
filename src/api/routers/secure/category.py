from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from db.session import get_db
from core.auth import get_current_user
from schemas.category import CategoryResponse
from models.category import Category

router = APIRouter(
    tags=["categories"],          # このルーターのタグを統一
    dependencies=[Depends(get_current_user)]
)

@router.get("/categories", response_model=list[CategoryResponse])
def read_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()

    return categories
