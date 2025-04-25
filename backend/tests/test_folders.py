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
def test_user(db):
    """Create a test user"""
    email = random_email()
    user = models.User(
        email=email,
        name="Test User",
        hashed_password=models.User.get_password_hash("password123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def auth_token(test_user):
    """Get authentication token for test user"""
    response = client.post(
        "/token",
        data={"username": test_user.email, "password": "password123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_folder(auth_token):
    """Test creating a new folder"""
    folder_data = {
        "name": "Test Folder",
        "description": "This is a test folder"
    }
    
    response = client.post(
        "/folders",
        json=folder_data,
        headers=auth_token
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == folder_data["name"]
    assert data["description"] == folder_data["description"]
    
    # Store folder ID as a variable instead of returning it
    folder_id = data["id"]

def test_get_folders(auth_token, test_user, db):
    """Test getting all folders for a user"""
    # Create a few folders for the user
    for i in range(3):
        folder = models.StudyFolder(
            name=f"Test Folder {i}",
            description=f"Test description {i}",
            user_id=test_user.id
        )
        db.add(folder)
    
    db.commit()
    
    # Get all folders
    response = client.get(
        "/folders",
        headers=auth_token
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "folders" in data
    assert len(data["folders"]) >= 3
    
    # Check that folders belong to the user
    for folder in data["folders"]:
        assert folder["user_id"] == test_user.id

def test_get_folder(auth_token, test_user, db):
    """Test getting a specific folder"""
    # Create a folder
    folder = models.StudyFolder(
        name="Specific Test Folder",
        description="For testing get specific folder",
        user_id=test_user.id
    )
    db.add(folder)
    db.commit()
    db.refresh(folder)
    
    # Get the specific folder
    response = client.get(
        f"/folders/{folder.id}",
        headers=auth_token
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == folder.id
    assert data["name"] == folder.name
    assert data["description"] == folder.description

def test_update_folder(auth_token, test_user, db):
    """Test updating a folder"""
    # Create a folder
    folder = models.StudyFolder(
        name="Update Test Folder",
        description="Before update",
        user_id=test_user.id
    )
    db.add(folder)
    db.commit()
    db.refresh(folder)
    
    # Update data
    update_data = {
        "name": "Updated Name",
        "description": "After update"
    }
    
    response = client.put(
        f"/folders/{folder.id}",
        json=update_data,
        headers=auth_token
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == folder.id
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]

def test_partial_update_folder(auth_token, test_user, db):
    """Test partial update of a folder (only name or only description)"""
    # Create a folder
    folder = models.StudyFolder(
        name="Partial Update Test",
        description="Original description",
        user_id=test_user.id
    )
    db.add(folder)
    db.commit()
    db.refresh(folder)
    
    # Update only name
    update_data = {
        "name": "New Name Only"
    }
    
    response = client.put(
        f"/folders/{folder.id}",
        json=update_data,
        headers=auth_token
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == folder.description  # Should be unchanged

def test_delete_folder(auth_token, test_user, db):
    """Test deleting a folder"""
    # Create a folder
    folder = models.StudyFolder(
        name="Delete Test Folder",
        description="For testing deletion",
        user_id=test_user.id
    )
    db.add(folder)
    db.commit()
    db.refresh(folder)
    
    # Delete the folder
    response = client.delete(
        f"/folders/{folder.id}",
        headers=auth_token
    )
    
    assert response.status_code == 204
    
    # Try to get the deleted folder
    response = client.get(
        f"/folders/{folder.id}",
        headers=auth_token
    )
    
    # Should return 404 Not Found
    assert response.status_code == 404

def test_access_another_user_folder(auth_token, db):
    """Test that a user cannot access another user's folder"""
    # Create another user
    other_email = random_email()
    other_user = models.User(
        email=other_email,
        name="Other User",
        hashed_password=models.User.get_password_hash("password123")
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)
    
    # Create a folder for the other user
    other_folder = models.StudyFolder(
        name="Other User's Folder",
        description="Should not be accessible",
        user_id=other_user.id
    )
    db.add(other_folder)
    db.commit()
    db.refresh(other_folder)
    
    # Try to access the other user's folder
    response = client.get(
        f"/folders/{other_folder.id}",
        headers=auth_token
    )
    
    # Should return 404 Not Found (to not leak existence of folders)
    assert response.status_code == 404 