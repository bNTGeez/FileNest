from fastapi import HTTPException
from sqlalchemy.orm import Session
from app import models

def verify_folder_ownership(db: Session, folder_id: int, user_id: int):
    """Verify if a user is the owner of a folder, returning the folder if true."""
    folder = db.query(models.StudyFolder).filter(
        models.StudyFolder.id == folder_id,
        models.StudyFolder.user_id == user_id
    ).first()
    return folder

def verify_folder_access(db: Session, folder_id: int, user_id: int, permission_types=None):
    # First check if user is the owner
    folder = verify_folder_ownership(db, folder_id, user_id)
    if folder:
        return folder
    
    # If not owner, check for shared access
    share_query = db.query(models.FolderShare).filter(
        models.FolderShare.folder_id == folder_id,
        models.FolderShare.user_id == user_id,
        models.FolderShare.invitation_accepted == True
    )
    
    # If specific permission types required, add that filter
    if permission_types:
        share_query = share_query.filter(
            models.FolderShare.permission_type.in_(permission_types)
        )
    
    shared_access = share_query.first()
    
    # If no shared access either, folder not found or not accessible
    if not shared_access:
        raise HTTPException(
            status_code=404, 
            detail="Folder not found or you don't have required permissions"
        )
    
    # Double-check folder exists
    folder = db.query(models.StudyFolder).filter(models.StudyFolder.id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    return folder

def verify_flashcard_access(db: Session, flashcard_id: int, user_id: int, permission_types=None):
    flashcard = db.query(models.Flashcard).filter(models.Flashcard.id == flashcard_id).first()
    
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    # If user owns the flashcard, return it
    if flashcard.user_id == user_id:
        return flashcard
    
    # Otherwise, check folder permissions
    try:
        verify_folder_access(db, flashcard.folder_id, user_id, permission_types)
        return flashcard
    except HTTPException:
        raise HTTPException(status_code=403, detail="Not authorized to access this flashcard") 