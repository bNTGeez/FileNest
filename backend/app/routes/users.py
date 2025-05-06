from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, Token
from app.auth import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRATION

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/signup", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)): 
  db_user = db.query(User).filter(User.email == user.email).first()
  if db_user:
    raise HTTPException(status_code=400, detail="Email already registered")
  
  hashed_password = User.get_password_hash(user.password)
  db_user = User(
    email = user.email,
    name = user.name,
    hashed_password = hashed_password
  )

  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return db_user
  
@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
  user = db.query(User).filter(User.email == login_data.email).first()
  if not user or not user.verify_password(login_data.password):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid credentials",
      headers={"WWW-Authenticate": "Bearer"},
    )
  
  access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRATION)
  access_token = create_access_token(data={"user_id": str(user.id)}, expires_delta=access_token_expires)
  return {"access_token": access_token, "token_type": "Bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
  return current_user
