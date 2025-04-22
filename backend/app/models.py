from sqlalchemy import Column, Integer, String
from app.database import Base

class File(Base):
  __tablename__ = "files"

  id = Column(Integer, primary_key=True, index=True) # auto-incrementing primary key, indexing for faster lookups
  filename = Column(String, nullable=False) # original filename uploaded by user
  s3_key = Column(String, nullable=False) # unique identifier for the file in S3
  user_id = Column(String, nullable=False) # user id of the owner (extract from JWT token)
  folder = Column(String, nullable=True) # folder name where the file is stored (optional)
  content_type = Column(String, nullable=True) # MIME type of the file (e.g. "application/pdf", "image/png")
  