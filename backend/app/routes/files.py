from fastapi import APIRouter, Depends, HTTPException 
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

# group all /files endpoints together
router = APIRouter()

@router.get("/files")
def get_files(db: Session = Depends(get_db)):
  return db.query(models.File).all() # get all files from the database