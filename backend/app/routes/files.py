from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.services.s3 import upload_file, generate_presigned_url
from app.auth import get_current_user
from uuid import uuid4

# group all /files endpoints together
router = APIRouter()

@router.get("/files")
def get_files(db: Session = Depends(get_db)):
  return db.query(models.File).all() # get all files from the postgresql database to the user


# Generate a unique S3 key under the user's folder
# Upload the file to S3
# Save the metadata and S3 key to the PostgreSQL database
# Return the file URL
@router.post("/upload")
async def upload_file_route(file: UploadFile = File(...), db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):

  key = f"{user_id}/{uuid4().hex}_{file.filename}"

  # upload the file to S3
  try:
    url = await upload_file(file.file, key)
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

  # save the metadata and S3 key to the postgresql database
  record = models.File(
    filename=file.filename,
    s3_key = key,
    user_id = user_id,
    content_type = file.content_type,
    folder = None,
  )

  db.add(record)
  db.commit()
  db.refresh(record)

  # return the URL and the file id
  return {"file_id": record.id, "url": url}

# download the file from S3
@router.get("/files/{file_id}/download")
def download_file(file_id: int, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
  # check ownership of the file
  record = db.query(models.File).filter_by(id=file_id, user_id = user_id).first()
  if not record:
    raise HTTPException(status_code=403, detail="Not authorized to access this file")

  try:
    # generate a time-limited presigned URL for the file (5 minutes)
    signed_url = generate_presigned_url(record.s3_key, expiration=300)
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
  
  return {"url": signed_url}



