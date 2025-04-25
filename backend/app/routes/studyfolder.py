from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.auth import get_current_user
from app.schemas import FolderResponse, FolderCreate, FolderUpdate, FolderList
from datetime import datetime, timezone
router = APIRouter()

@router.get("/folders")
def get_folder(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  folders = db.query(models.StudyFolder).filter(models.StudyFolder.user_id == current_user.id).all()
  return FolderList(folders=folders)

@router.post("/folders", response_model=FolderResponse)
def create_folder(folder_data: FolderCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  new_folder = models.StudyFolder(
    name=folder_data.name,
    description=folder_data.description,
    user_id=current_user.id
  )
  db.add(new_folder)
  db.commit()
  db.refresh(new_folder)
  return new_folder

@router.get("/folders/{folder_id}", response_model=FolderResponse)
def get_folder_by_id(folder_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  folder = db.query(models.StudyFolder).filter(models.StudyFolder.id == folder_id, models.StudyFolder.user_id == current_user.id).first()
  if not folder:
    raise HTTPException(status_code=404, detail="Folder not found")
  return folder

@router.put("/folders/{folder_id}", response_model=FolderResponse)
def update_folder(folder_id: int, folder_data: FolderUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):


  folder = db.query(models.StudyFolder).filter(models.StudyFolder.id == folder_id, models.StudyFolder.user_id == current_user.id).first()
  if not folder:
    raise HTTPException(status_code=404, detail="Folder not found")

  if folder_data.name is not None:
    folder.name = folder_data.name
  if folder_data.description is not None:
    folder.description = folder_data.description

  folder.updated_at = datetime.now(timezone.utc)

  db.commit()
  db.refresh(folder)

  return folder

@router.delete("/folders/{folder_id}", status_code=204)
def delete_folder(folder_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  folder = db.query(models.StudyFolder).filter(models.StudyFolder.id == folder_id, models.StudyFolder.user_id == current_user.id).first()
  if not folder:
    raise HTTPException(status_code=404, detail="Folder not found")
  db.delete(folder)
  db.commit()
  return {"message": "Folder deleted successfully"}


