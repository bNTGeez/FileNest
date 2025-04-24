from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
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
  email: EmailStr

  class Config:
    from_attributes = True # allows us to convert database objects to api response objects

class Token(BaseModel):
  access_token: str
  token_type: str 

class TokenData(BaseModel): # store extracted user_id from JWT token
  user_id: int | None = None 

class FolderBase(BaseModel):
  name: str
  description: Optional[str] = None 

class FolderCreate(FolderBase):
  pass # just takes in the name and description which is from folderbase

class FolderUpdate(BaseModel):
  name: Optional[str] = None
  description: Optional[str] = None

class FolderResponse(BaseModel):
  id: int
  name: str
  description: Optional[str] = None
  user_id: str
  created_at: datetime
  updated_at: datetime

  class Config:
    from_attributes = True 

class FolderList(BaseModel):
  folders: List[FolderResponse]

class FlashcardBase(BaseModel):
  question: str
  answer: str
  folder_id: int

class FlashcardCreate(FlashcardBase):
  pass

class FlashcardUpdate(BaseModel):
  question: Optional[str] = None
  answer: Optional[str] = None
  folder_id: Optional[int] = None

class FlashcardResponse(BaseModel):
  id: int
  question: str
  answer: str
  user_id: str
  folder_id: int
  created_at: datetime
  updated_at: datetime

  class Config:
    from_attributes = True 

class FlashcardList(BaseModel):
  flashcards: List[FlashcardResponse]

class FlashcardGenerationOptions(BaseModel):
  num_cards: Optional[int] = 10
  focus_area: Optional[str] = None

class ShareBase(BaseModel):
  folder_id: int
  permission_type: str

class ShareCreate(BaseModel):
  folder_id: int
  user_email: EmailStr
  permission_type: str

class ShareUpdate(BaseModel):
  permission_type: Optional[str] = None

class ShareResponse(BaseModel):
  id: int
  folder_id: int
  user_id: int
  user_email: Optional[EmailStr] = None
  permission_type: str
  invitation_accepted: bool
  invitation_email: Optional[str] = None
  created_at: datetime
  updated_at: datetime

  class Config:
    from_attributes = True 

class ShareList(BaseModel):
  shares: List[ShareResponse]
    