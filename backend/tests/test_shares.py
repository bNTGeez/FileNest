import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from sqlalchemy.orm import Session
from app import models
import random
import string

client = TestClient(app)

@pytest.fixture
def db():
    # Get a DB session
    db = next(get_db())
    yield db
    # Clean up (after test)
    db.close()

def random_email():
    """Generate a random email for testing"""
    letters = string.ascii_lowercase
    username = ''.join(random.choice(letters) for i in range(8))
    return f"{username}@example.com"

@pytest.fixture
def test_users(db):
    """Create two test users - one folder owner and one recipient"""
    # Create owner user
    owner_email = random_email()
    owner = models.User(
        email=owner_email,
        name="Test Owner",
        hashed_password=models.User.get_password_hash("password123")
    )
    db.add(owner)
    
    # Create recipient user
    recipient_email = random_email()
    recipient = models.User(
        email=recipient_email,
        name="Test Recipient",
        hashed_password=models.User.get_password_hash("password123")
    )
    db.add(recipient)
    
    db.commit()
    db.refresh(owner)
    db.refresh(recipient)
    
    return {"owner": owner, "recipient": recipient}

@pytest.fixture
def test_folder(db, test_users):
    """Create a test folder owned by the owner user"""
    folder = models.StudyFolder(
        name="Test Folder",
        description="For testing folder sharing",
        user_id=test_users["owner"].id
    )
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder

@pytest.fixture
def auth_tokens(test_users):
    """Get authentication tokens for both test users"""
    # Get token for owner
    owner_response = client.post(
        "/token",
        data={"username": test_users["owner"].email, "password": "password123"}
    )
    owner_token = owner_response.json()["access_token"]
    
    # Get token for recipient
    recipient_response = client.post(
        "/token",
        data={"username": test_users["recipient"].email, "password": "password123"}
    )
    recipient_token = recipient_response.json()["access_token"]
    
    return {
        "owner": {"Authorization": f"Bearer {owner_token}"},
        "recipient": {"Authorization": f"Bearer {recipient_token}"}
    }

def test_create_share(test_folder, auth_tokens, test_users):
    """Test creating a folder share"""
    share_data = {
        "folder_id": test_folder.id,
        "user_email": test_users["recipient"].email,
        "permission_type": "view"
    }
    
    response = client.post(
        f"/folders/{test_folder.id}/share",
        json=share_data,
        headers=auth_tokens["owner"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["folder_id"] == test_folder.id
    assert data["invitation_email"] == test_users["recipient"].email
    assert data["permission_type"] == "view"
    assert data["invitation_accepted"] == False
    
    # Store share ID as a variable instead of returning it
    share_id = data["id"]

def test_duplicate_share_prevention(test_folder, auth_tokens, test_users):
    """Test that duplicate shares are prevented"""
    # First create a share
    share_data = {
        "folder_id": test_folder.id,
        "user_email": test_users["recipient"].email,
        "permission_type": "view"
    }
    
    # Create first share
    client.post(
        f"/folders/{test_folder.id}/share",
        json=share_data,
        headers=auth_tokens["owner"]
    )
    
    # Try to create duplicate share
    response = client.post(
        f"/folders/{test_folder.id}/share",
        json=share_data,
        headers=auth_tokens["owner"]
    )
    
    # Should fail with 400 error
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_get_folder_shares(test_folder, auth_tokens, test_users):
    """Test getting all shares for a folder"""
    # First create a share
    share_data = {
        "folder_id": test_folder.id,
        "user_email": test_users["recipient"].email,
        "permission_type": "view"
    }
    
    client.post(
        f"/folders/{test_folder.id}/share",
        json=share_data,
        headers=auth_tokens["owner"]
    )
    
    # Now get all shares
    response = client.get(
        f"/folders/{test_folder.id}/shares",
        headers=auth_tokens["owner"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["shares"]) >= 1
    assert data["shares"][0]["invitation_email"] == test_users["recipient"].email

def test_get_share(test_folder, auth_tokens, test_users):
    """Test getting a single share"""
    # First create a share
    share_data = {
        "folder_id": test_folder.id,
        "user_email": test_users["recipient"].email,
        "permission_type": "view"
    }
    
    create_response = client.post(
        f"/folders/{test_folder.id}/share",
        json=share_data,
        headers=auth_tokens["owner"]
    )
    
    share_id = create_response.json()["id"]
    
    # Now get the specific share
    response = client.get(
        f"/shares/{share_id}",
        headers=auth_tokens["owner"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == share_id
    assert data["folder_id"] == test_folder.id
    assert data["invitation_email"] == test_users["recipient"].email

def test_update_share(test_folder, auth_tokens, test_users):
    """Test updating a share's permissions"""
    # First create a share
    share_data = {
        "folder_id": test_folder.id,
        "user_email": test_users["recipient"].email,
        "permission_type": "view"
    }
    
    create_response = client.post(
        f"/folders/{test_folder.id}/share",
        json=share_data,
        headers=auth_tokens["owner"]
    )
    
    share_id = create_response.json()["id"]
    
    # Update the share permission
    update_data = {
        "permission_type": "admin"
    }
    
    response = client.put(
        f"/shares/{share_id}",
        json=update_data,
        headers=auth_tokens["owner"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["permission_type"] == "admin"

def test_accept_share(test_folder, auth_tokens, test_users):
    """Test accepting a share invitation"""
    # First create a share
    share_data = {
        "folder_id": test_folder.id,
        "user_email": test_users["recipient"].email,
        "permission_type": "view"
    }
    
    create_response = client.post(
        f"/folders/{test_folder.id}/share",
        json=share_data,
        headers=auth_tokens["owner"]
    )
    
    share_id = create_response.json()["id"]
    
    # Accept the share as recipient
    response = client.post(
        f"/shares/{share_id}/accept",
        headers=auth_tokens["recipient"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["invitation_accepted"] == True
    assert data["user_id"] == test_users["recipient"].id

def test_access_shared_folder(test_folder, auth_tokens, test_users):
    """Test that recipient can access a shared folder after accepting the invitation"""
    # First create a share
    share_data = {
        "folder_id": test_folder.id,
        "user_email": test_users["recipient"].email,
        "permission_type": "view"
    }
    
    create_response = client.post(
        f"/folders/{test_folder.id}/share",
        json=share_data,
        headers=auth_tokens["owner"]
    )
    
    share_id = create_response.json()["id"]
    
    # Accept the share as recipient
    client.post(
        f"/shares/{share_id}/accept",
        headers=auth_tokens["recipient"]
    )
    
    # Try to access flashcards in the folder
    response = client.get(
        f"/folders/{test_folder.id}/flashcards",
        headers=auth_tokens["recipient"]
    )
    
    assert response.status_code == 200

def test_delete_share(test_folder, auth_tokens, test_users):
    """Test deleting a share"""
    # First create a share
    share_data = {
        "folder_id": test_folder.id,
        "user_email": test_users["recipient"].email,
        "permission_type": "view"
    }
    
    create_response = client.post(
        f"/folders/{test_folder.id}/share",
        json=share_data,
        headers=auth_tokens["owner"]
    )
    
    share_id = create_response.json()["id"]
    
    # Delete the share
    response = client.delete(
        f"/shares/{share_id}",
        headers=auth_tokens["owner"]
    )
    
    assert response.status_code == 204

def test_access_revoked_after_delete(test_folder, auth_tokens, test_users):
    """Test that recipient loses access after share is deleted"""
    # First create a share
    share_data = {
        "folder_id": test_folder.id,
        "user_email": test_users["recipient"].email,
        "permission_type": "view"
    }
    
    create_response = client.post(
        f"/folders/{test_folder.id}/share",
        json=share_data,
        headers=auth_tokens["owner"]
    )
    
    share_id = create_response.json()["id"]
    
    # Accept the share as recipient
    client.post(
        f"/shares/{share_id}/accept",
        headers=auth_tokens["recipient"]
    )
    
    # Delete the share
    client.delete(
        f"/shares/{share_id}",
        headers=auth_tokens["owner"]
    )
    
    # Try to access flashcards in the folder
    response = client.get(
        f"/folders/{test_folder.id}/flashcards",
        headers=auth_tokens["recipient"]
    )
    
    # Should get 404 as access has been revoked
    assert response.status_code == 404 