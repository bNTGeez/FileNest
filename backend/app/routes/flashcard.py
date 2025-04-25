from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.auth import get_current_user
from app.schemas import FlashcardResponse, FlashcardCreate, FlashcardList, FlashcardGenerationRequest, FlashcardUpdate
from app.utils.gpt import generate_flashcards
router = APIRouter()


@router.get("/folders/{folder_id}/flashcards", response_model=FlashcardList)
def get_flashcards(folder_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  # Check if folder exists and user is the owner
  folder = db.query(models.StudyFolder).filter(models.StudyFolder.id == folder_id, models.StudyFolder.user_id == current_user.id).first()
  
  # If user is not the owner, check if they have shared access
  if not folder:
    # Check for shared access
    shared_access = db.query(models.FolderShare).filter(
      models.FolderShare.folder_id == folder_id,
      models.FolderShare.user_id == current_user.id,
      models.FolderShare.invitation_accepted == True
    ).first()
    
    # If no shared access either, folder not found or not accessible
    if not shared_access:
      raise HTTPException(status_code=404, detail="Folder not found or you don't have access")
    
    # Double-check folder exists
    folder = db.query(models.StudyFolder).filter(models.StudyFolder.id == folder_id).first()
    if not folder:
      raise HTTPException(status_code=404, detail="Folder not found")
  
  # Get flashcards for the folder
  flashcards = db.query(models.Flashcard).filter(models.Flashcard.folder_id == folder_id).all()
  return {"flashcards": flashcards}


@router.post("/folders/{folder_id}/flashcards", response_model=FlashcardList)
def create_flashcards(folder_id: int, flashcard_data: FlashcardGenerationRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  # Check if folder exists and user is the owner
  folder = db.query(models.StudyFolder).filter(models.StudyFolder.id == folder_id, models.StudyFolder.user_id == current_user.id).first()
  
  # If user is not the owner, check if they have shared access with edit or admin permissions
  if not folder:
    # Check for shared access with edit permissions
    shared_access = db.query(models.FolderShare).filter(
      models.FolderShare.folder_id == folder_id,
      models.FolderShare.user_id == current_user.id,
      models.FolderShare.invitation_accepted == True,
      models.FolderShare.permission_type.in_(["edit", "admin"])
    ).first()
    
    # If no edit access, folder not found or not accessible
    if not shared_access:
      raise HTTPException(status_code=404, detail="Folder not found or you don't have edit permission")
    
    # Double-check folder exists
    folder = db.query(models.StudyFolder).filter(models.StudyFolder.id == folder_id).first()
    if not folder:
      raise HTTPException(status_code=404, detail="Folder not found")
  
  flashcards = generate_flashcards(flashcard_data.topic, flashcard_data.num_flashcards)
  created_flashcards = []

  for flashcard in flashcards:
    flashcard_create = models.Flashcard(
      question = flashcard["question"],
      answer = flashcard["answer"],
      folder_id = folder_id,
      user_id = current_user.id
    )
    db.add(flashcard_create)
    created_flashcards.append(flashcard_create)

  db.commit()
  for flashcard in created_flashcards:
    db.refresh(flashcard)

  return {"flashcards": created_flashcards}

@router.get("/flashcards/{flashcard_id}", response_model=FlashcardResponse)
def get_individual_flashcard(flashcard_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  # First try to find the flashcard by ID and user
  flashcard = db.query(models.Flashcard).filter(models.Flashcard.id == flashcard_id).first()
  
  if not flashcard:
    raise HTTPException(status_code=404, detail="Flashcard not found")
  
  # If user owns the flashcard, return it
  if flashcard.user_id == current_user.id:
    return flashcard
    
  # Otherwise, check if they have shared access to the folder
  shared_access = db.query(models.FolderShare).filter(
    models.FolderShare.folder_id == flashcard.folder_id,
    models.FolderShare.user_id == current_user.id,
    models.FolderShare.invitation_accepted == True
  ).first()
  
  if not shared_access:
    raise HTTPException(status_code=403, detail="Not authorized to access this flashcard")
  
  return flashcard

@router.get("/flashcards", response_model=FlashcardList)
def get_all_flashcards(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  # Get all flashcards the user directly owns
  own_flashcards = db.query(models.Flashcard).filter(models.Flashcard.user_id == current_user.id).all()
  
  # Get folder IDs where the user has shared access
  shared_folder_ids = db.query(models.FolderShare.folder_id).filter(
    models.FolderShare.user_id == current_user.id,
    models.FolderShare.invitation_accepted == True
  ).distinct()
  
  # Get flashcards from shared folders
  shared_flashcards = db.query(models.Flashcard).filter(
    models.Flashcard.folder_id.in_(shared_folder_ids)
  ).all()
  
  # Combine both sets of flashcards
  all_flashcards = own_flashcards + shared_flashcards
  
  return {"flashcards": all_flashcards}

@router.post("/flashcards", response_model=FlashcardResponse)
def create_individual_flashcard(flashcard_data: FlashcardCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  # Check if the folder exists
  folder = db.query(models.StudyFolder).filter(models.StudyFolder.id == flashcard_data.folder_id).first()
  if not folder:
    raise HTTPException(status_code=404, detail="Folder not found")
  
  # Check if user is folder owner or has edit permission
  if folder.user_id != current_user.id:
    # Check for shared access with edit permissions
    shared_access = db.query(models.FolderShare).filter(
      models.FolderShare.folder_id == flashcard_data.folder_id,
      models.FolderShare.user_id == current_user.id,
      models.FolderShare.invitation_accepted == True,
      models.FolderShare.permission_type.in_(["edit", "admin"])
    ).first()
    
    if not shared_access:
      raise HTTPException(status_code=403, detail="Not authorized to create flashcards in this folder")
  
  flashcard = models.Flashcard(
    question = flashcard_data.question,
    answer = flashcard_data.answer,
    folder_id = flashcard_data.folder_id,
    user_id = current_user.id
  )
  db.add(flashcard)
  db.commit()
  db.refresh(flashcard)
  return flashcard

@router.put("/flashcards/{id}", response_model=FlashcardResponse)
def update_flashcard(id: int, flashcard_data: FlashcardUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  # First get the existing flashcard
  existing_flashcard = db.query(models.Flashcard).filter(models.Flashcard.id == id).first()
  if not existing_flashcard:
    raise HTTPException(status_code=404, detail="Flashcard not found")
  
  # Check current folder permissions
  current_folder = db.query(models.StudyFolder).filter(models.StudyFolder.id == existing_flashcard.folder_id).first()
  if not current_folder:
    raise HTTPException(status_code=404, detail="Associated folder not found")
    
  # Check if user has edit permission on current folder (owner or shared edit/admin access)
  has_current_folder_permission = False
  if current_folder.user_id == current_user.id: # if user is the owner of the folder
    has_current_folder_permission = True
  else:
    # Check for shared access with edit permissions
    shared_access = db.query(models.FolderShare).filter(
      models.FolderShare.folder_id == existing_flashcard.folder_id,
      models.FolderShare.user_id == current_user.id,
      models.FolderShare.invitation_accepted == True,
      models.FolderShare.permission_type.in_(["edit", "admin"])
    ).first()
    
    if shared_access:
      has_current_folder_permission = True
      
  if not has_current_folder_permission:
    raise HTTPException(status_code=403, detail="Not authorized to update this flashcard")
  
  # Update fields if provided
  if flashcard_data.question is not None:
    existing_flashcard.question = flashcard_data.question
  if flashcard_data.answer is not None:
    existing_flashcard.answer = flashcard_data.answer
  if flashcard_data.folder_id is not None:
    # Check if user has access to the target folder they're moving the flashcard to
    target_folder = db.query(models.StudyFolder).filter(models.StudyFolder.id == flashcard_data.folder_id).first()
    if not target_folder:
      raise HTTPException(status_code=404, detail="Target folder not found")
    
    # Check if user has edit permission on target folder (either owner or shared edit/admin access)
    has_target_folder_permission = False
    if target_folder.user_id == current_user.id:
      has_target_folder_permission = True
    else:
      # Check for edit permission on target folder
      target_access = db.query(models.FolderShare).filter(
        models.FolderShare.folder_id == flashcard_data.folder_id,
        models.FolderShare.user_id == current_user.id,
        models.FolderShare.invitation_accepted == True,
        models.FolderShare.permission_type.in_(["edit", "admin"])
      ).first()
      
      if target_access:
        has_target_folder_permission = True
        
    if not has_target_folder_permission:
      raise HTTPException(status_code=403, detail="Not authorized to move flashcard to target folder")
    
    existing_flashcard.folder_id = flashcard_data.folder_id
  
  db.commit()
  db.refresh(existing_flashcard)
  return existing_flashcard

@router.delete("/flashcards/{id}", status_code=204)
def delete_flashcard(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  flashcard = db.query(models.Flashcard).filter(models.Flashcard.id == id).first()
  if not flashcard:
    raise HTTPException(status_code=404, detail="Flashcard not found")
  
  # Check folder permissions
  folder = db.query(models.StudyFolder).filter(models.StudyFolder.id == flashcard.folder_id).first()
  if not folder:
    raise HTTPException(status_code=404, detail="Associated folder not found")
    
  # Check if user has admin permission on folder (either owner or shared admin access)
  has_admin_permission = False
  if folder.user_id == current_user.id:
    has_admin_permission = True
  else:
    # Check for shared access with admin permissions
    shared_access = db.query(models.FolderShare).filter(
      models.FolderShare.folder_id == flashcard.folder_id,
      models.FolderShare.user_id == current_user.id,
      models.FolderShare.invitation_accepted == True,
      models.FolderShare.permission_type == "admin"
    ).first()
    
    if shared_access:
      has_admin_permission = True
      
  if not has_admin_permission:
    raise HTTPException(status_code=403, detail="Not authorized to delete this flashcard")
  
  db.delete(flashcard)
  db.commit()
  return {"message": "Flashcard deleted successfully"}



