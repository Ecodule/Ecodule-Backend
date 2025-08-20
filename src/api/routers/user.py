from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import auth
import crud.user, schemas.user
from db.session import get_db

# define the rule to get token from the request
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter()

# endpoint to create a new user
@router.post("/users/create", response_model=schemas.user.UserResponse, status_code=status.HTTP_201_CREATED, tags=["users"])
def create_new_user(user: schemas.user.UserCreate, db: Session = Depends(get_db)):
    # check if the user already exists
    db_user = crud.user.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="このメールアドレスは既に使用されています。")

    # create new user
    created_user = crud.user.create_user(db=db, email=user.email, password=user.password)
    return created_user

# authentication and token generation
@router.post("/auth/login/", response_model=schemas.user.Token,tags=["auth"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # verify user credentials and generate token
    user = crud.user.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # create access token
    access_token = auth.create_access_token(
        data={"sub": user.email} # sub is the unique identifier in JWT, typically the user ID or email
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.user.UserResponse, tags=["users"])
def read_users_me(current_user: schemas.user.UserResponse = Depends(auth.get_current_user)):
    return current_user
