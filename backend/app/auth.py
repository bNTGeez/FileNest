from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from typing import Annotated
import os 
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import TokenData

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRATION = 3600 # 24 hours
ALGORITHM = "HS256" # HS256 (HMAC with SHA-256) is a standard algorithm for JWT.

# OAuth2PasswordBearer handles token extraction from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create a JWT token with the provided data and expiration time
    
    Parameters:
    - data: Dictionary that contains data to include in the token (user ID)
    - expires_delta: Optional expiration time
    
    Returns:
    - Encoded JWT token as string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    """
    Verify JWT token and extract the current user
    
    Parameters:
    - token: JWT token (extracted by OAuth2PasswordBearer)
    - db: Database session
    
    Returns:
    - User object if token is valid
    
    Raises:
    - HTTPException with 401 status if token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode and verify the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        # Create token data model
        token_data = TokenData(user_id=user_id)
    except InvalidTokenError:
        # Handle any JWT decoding errors
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Check if the current user is active

    Parameters:
    - current_user: User object from get_current_user dependency
    
    Returns:
    - User object if active

    """

    return current_user
    
    
