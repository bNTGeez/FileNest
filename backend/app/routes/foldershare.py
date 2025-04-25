from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.auth import get_current_user
from app.schemas import ShareResponse, ShareCreate, ShareList, ShareUpdate
from datetime import datetime, timezone
router = APIRouter()


@router.post("/folders/{folder_id}/share", response_model=ShareResponse)
def share_folder(folder_id: int, share_data: ShareCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  # Verify folder exists and user is the owner
  folder = db.query(models.StudyFolder).filter(models.StudyFolder.id == folder_id, models.StudyFolder.user_id == current_user.id).first()
  if not folder:
    raise HTTPException(status_code=404, detail="Folder not found or you don't have permission")
  
  # Check if a share already exists for this email and folder
  existing_share = db.query(models.FolderShare).filter(
    models.FolderShare.folder_id == folder_id,
    models.FolderShare.invitation_email == share_data.user_email
  ).first()
  
  if existing_share:
    raise HTTPException(status_code=400, detail="A share invitation already exists for this email")
  
  # Check if user exists
  user = db.query(models.User).filter(models.User.email == share_data.user_email).first()
  
  if user:
    # Create share for existing user
    new_share = models.FolderShare(
      folder_id=folder_id,
      user_id=user.id,
      permission_type=share_data.permission_type,
      invitation_accepted=False,
      invitation_email=share_data.user_email
    )
  else:
    # Create pending invitation for non-registered user
    new_share = models.FolderShare(
      folder_id=folder_id,
      user_id=None,  # Will be set when user registers
      permission_type=share_data.permission_type,
      invitation_accepted=False,
      invitation_email=share_data.user_email
    )
    
  db.add(new_share)
  db.commit()
  db.refresh(new_share)
  
  # TODO: Send invitation email 
  print(f"Would send invitation email to {share_data.user_email} for folder {folder.name}")
  
  return new_share

@router.get("/folders/{folder_id}/shares", response_model=ShareList)
def get_folder_shares(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify folder exists and user is the owner
    folder = db.query(models.StudyFolder).filter(
        models.StudyFolder.id == folder_id,
        models.StudyFolder.user_id == current_user.id
    ).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found or you don't have permission")
    
    # Get all shares for this folder
    shares = db.query(models.FolderShare).filter(
        models.FolderShare.folder_id == folder_id
    ).all()
    
    return {"shares": shares}

@router.get("/shares/{share_id}", response_model=ShareResponse)
def get_share(
    share_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # First get the share
    share = db.query(models.FolderShare).filter(
        models.FolderShare.id == share_id
    ).first()
    
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    
    # Then check if current user is either owner of the folder or the recipient
    folder = db.query(models.StudyFolder).filter(
        models.StudyFolder.id == share.folder_id
    ).first()
    
    if folder.user_id != current_user.id and share.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this share")
    
    return share

@router.put("/shares/{share_id}", response_model=ShareResponse)
def update_share(
    share_id: int,
    share_data: ShareUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # First get the share
    share = db.query(models.FolderShare).filter(
        models.FolderShare.id == share_id
    ).first()
    
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    
    # Check if current user is the folder owner
    folder = db.query(models.StudyFolder).filter(
        models.StudyFolder.id == share.folder_id
    ).first()
    
    if folder.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only folder owner can update shares")
    
    # Update permission type if provided
    if share_data.permission_type is not None:
        share.permission_type = share_data.permission_type
    
    share.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(share)
    
    return share

@router.delete("/shares/{share_id}", status_code=204)
def delete_share(
    share_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # First get the share
    share = db.query(models.FolderShare).filter(
        models.FolderShare.id == share_id
    ).first()
    
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    
    # Check if current user is the folder owner
    folder = db.query(models.StudyFolder).filter(
        models.StudyFolder.id == share.folder_id
    ).first()
    
    if folder.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only folder owner can delete shares")
    
    db.delete(share)
    db.commit()
    
    return {"message": "Share deleted successfully"}

@router.post("/shares/{share_id}/accept", response_model=ShareResponse)
def accept_share(
    share_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # First get the share
    share = db.query(models.FolderShare).filter(
        models.FolderShare.id == share_id,
        models.FolderShare.invitation_email == current_user.email,
        models.FolderShare.invitation_accepted == False
    ).first()
    
    if not share:
        raise HTTPException(status_code=404, detail="Share invitation not found or already accepted")
    
    # Update the share to link it to the current user and mark as accepted
    share.user_id = current_user.id
    share.invitation_accepted = True
    share.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(share)
    
    return share