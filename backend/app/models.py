from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from passlib.context import CryptContext
from datetime import datetime, timezone
import enum

myctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PermissionType(enum.Enum):
    READ = "read"
    EDIT = "edit"
    ADMIN = "admin"

class User(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True, index=True, autoincrement=True)
  name = Column(String, nullable=False)
  email = Column(String, nullable=False, unique=True)
  hashed_password = Column(String, nullable=False)

  @classmethod
  def get_password_hash(cls, password):
    return myctx.hash(password)
  
  def verify_password(self, password: str) -> bool:
    return myctx.verify(password, self.hashed_password)
  

class File(Base):
  __tablename__ = "files"

  id = Column(Integer, primary_key=True, index=True) # auto-incrementing primary key, indexing for faster lookups
  filename = Column(String, nullable=False) # original filename uploaded by user
  s3_key = Column(String, nullable=False) # unique identifier for the file in S3
  user_id = Column(Integer, nullable=False) # user id of the owner (extract from JWT token)
  folder = Column(String, nullable=True) # folder name where the file is stored (optional)
  content_type = Column(String, nullable=True) # MIME type of the file (e.g. "application/pdf", "image/png")
  uploaded_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc)) # timestamp of when the file was uploaded
  folder_id = Column(Integer, ForeignKey('study_folders.id'), nullable=False)

  folder = relationship("StudyFolder", back_populates="files") # back-reference to the folder it belongs to

class StudyFolder(Base):
  __tablename__ = "study_folders"

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, nullable=False)
  user_id = Column(Integer, nullable=False)  # Owner of the folder
  description = Column(String, nullable=True)
  created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
  updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))

  files = relationship("File", back_populates="folder")
  flashcards = relationship("Flashcard", back_populates="folder")
  shares = relationship("FolderShare", back_populates="folder")

class Flashcard(Base):
  __tablename__ = "flashcards"

  id = Column(Integer, primary_key=True, index=True)
  question = Column(String, nullable=False)
  answer = Column(String, nullable=False)
  user_id = Column(Integer, nullable=False)
  created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
  updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
  folder_id = Column(Integer, ForeignKey('study_folders.id'), nullable=False)
  
  folder = relationship("StudyFolder", back_populates="flashcards")

class FolderShare(Base):
  __tablename__ = "folder_shares"
  
  id = Column(Integer, primary_key=True, index=True)
  folder_id = Column(Integer, ForeignKey('study_folders.id'), nullable=False)
  user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # User who has access (can be null for invitations to non-registered users)
  permission_type = Column(String, nullable=False, default=PermissionType.READ.value)  # read, edit, admin
  created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
  updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
  invitation_accepted = Column(Boolean, nullable=False, default=False)
  invitation_email = Column(String, nullable=True)  # Used for invitations to users not yet registered
  
  folder = relationship("StudyFolder", back_populates="shares")
  user = relationship("User")
