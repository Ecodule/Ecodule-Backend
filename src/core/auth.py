import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from dotenv import load_dotenv

import crud.user
from db.session import get_db

load_dotenv()

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

# define the rule to get token from the request
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Decode the JWT token to get the current user
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報が無効です",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    try:
        # Decode the token and get the payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # get the email from the payload
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
    except JWTError:
        # If the token were invalid or expired, raise an exception
        raise credentials_exception

    # get user from the database by email
    user = crud.user.get_user_by_email(db, email=email)
    
    if user is None:
        raise credentials_exception
    
    return user