from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserBase(BaseModel):
  email: EmailStr 
  
class UserCreate(UserBase):
  name: str 
  password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
  email: EmailStr
  password: str  

class UserResponse(BaseModel):
  id: int
  name: str

  class Config:
    from_attributes = True # allows us to convert database objects to api response objects

class Token(BaseModel):
  access_token: str
  token_type: str 

class TokenData(BaseModel): # store extracted user_id from JWT token
  user_id: int | None = None 