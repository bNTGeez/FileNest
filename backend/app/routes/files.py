from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.services.s3 import upload_file, generate_presigned_url
from app.auth import get_current_user
from uuid import uuid4
from datetime import datetime, timezone
import os
from typing import List
# group all /files endpoints together
router = APIRouter()

# get all files from the postgresql database to the user
@router.get("/files")
def get_files(db: Session = Depends(get_db)):
  return db.query(models.File).all() # get all files from the postgresql database to the user


# Generate a unique S3 key under the user's folder
# Upload the file to S3
# Save the metadata and S3 key to the PostgreSQL database
# Return the file URL
@router.post("/upload")
async def upload_file_route(
    file: List[UploadFile] = File(...),
    folder_id: int = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    
    user_id = str(current_user.id)

    # makes sure the folder exists and name it default if nothing provided
    if folder_id is None:
        default_folder = db.query(models.StudyFolder).filter_by(user_id=user_id, name="Default").first()
        if default_folder is None:
            default_folder = models.StudyFolder(
                name="Default",
                user_id=user_id,
                description="Default folder",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(default_folder)
            db.commit()
            db.refresh(default_folder)
        folder_id = default_folder.id
    uploaded_files = []
    for f in file:
      # make the filename unique if it already exists
      original_filename = f.filename
      base_name, extension = os.path.splitext(original_filename)
      unique_filename = original_filename
      duplicate_count = 1

      # Check if the filename is unique in the folder and increment if needed 
      while db.query(models.File).filter_by(folder_id=folder_id, filename=unique_filename).first():
          unique_filename = f"{base_name} ({duplicate_count}){extension}"
          duplicate_count += 1

      # Generate a unique S3 key for storage
      s3_key = f"{user_id}/{uuid4().hex}_{unique_filename}"

      # Upload the file to S3
      try:
          url = await upload_file(f.file, s3_key)
      except Exception as e:
          raise HTTPException(status_code=500, detail=str(e))

      # Save file metadata to the database
      record = models.File(
          filename=unique_filename,
          s3_key=s3_key,
          user_id=user_id,
          content_type=f.content_type,
          folder_id=folder_id,
      )
      db.add(record)
      db.commit()
      db.refresh(record)

      # Return file info to the frontend
      uploaded_files.append({
        "file_id": record.id,
        "url": url,
        "filename": record.filename
      })

    return uploaded_files

  # download the file from S3
@router.get("/files/{file_id}/download")
def download_file(file_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  # Extract user_id from the User object
  user_id = str(current_user.id)
  
  # check ownership of the file
  record = db.query(models.File).filter_by(id=file_id, user_id=user_id).first()
  if not record:
    raise HTTPException(status_code=403, detail="Not authorized to access this file")

  try:
    # generate a time-limited presigned URL for the file (60 minutes)
    signed_url = generate_presigned_url(
      record.s3_key, 
      expiration=3600,
      response_headers={
        'ResponseContentDisposition': 'attachment',
        'ResponseContentType': record.content_type
      }
    )
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

  return {"url": signed_url}

# preview the file from S3
@router.get("/files/{file_id}/preview")
def preview_file(file_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  # Extract user_id from the User object
  user_id = str(current_user.id)
  
  # check ownership of the file
  record = db.query(models.File).filter_by(id=file_id, user_id=user_id).first()
  if not record:
    raise HTTPException(status_code=403, detail="Not authorized to access this file")

  try:
    # generate a presigned URL for the file (1 hour)
    signed_url = generate_presigned_url(
      record.s3_key, 
      expiration=3600,  # 1 hour
      response_headers={
        'ResponseContentDisposition': 'inline',
        'ResponseContentType': record.content_type
      }
    )
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
  
  return {"url": signed_url}

@router.delete("/files/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

  file = db.query(models.File).filter_by(id=file_id, user_id=current_user.id).first()
  if not file:
    raise HTTPException(status_code=404, detail="File not found")
  
  db.delete(file)
  db.commit()
  return {"message": "File deleted successfully"}

  
  

