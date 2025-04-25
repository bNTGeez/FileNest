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
    """Create two test users - one folder owner and one with shared access"""
    # Create owner user
    owner_email = random_email()
    owner = models.User(
        email=owner_email,
        name="Test Owner",
        hashed_password=models.User.get_password_hash("password123")
    )
    db.add(owner)
    
    # Create collaborator user
    collaborator_email = random_email()
    collaborator = models.User(
        email=collaborator_email,
        name="Test Collaborator",
        hashed_password=models.User.get_password_hash("password123")
    )
    db.add(collaborator)
    
    db.commit()
    db.refresh(owner)
    db.refresh(collaborator)
    
    return {"owner": owner, "collaborator": collaborator}

@pytest.fixture
def test_folder(db, test_users):
    """Create a test folder owned by the owner user"""
    folder = models.StudyFolder(
        name="Test Folder",
        description="For testing flashcards",
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
    
    # Get token for collaborator
    collaborator_response = client.post(
        "/token",
        data={"username": test_users["collaborator"].email, "password": "password123"}
    )
    collaborator_token = collaborator_response.json()["access_token"]
    
    return {
        "owner": {"Authorization": f"Bearer {owner_token}"},
        "collaborator": {"Authorization": f"Bearer {collaborator_token}"}
    }

@pytest.fixture
def shared_folder(db, test_users, test_folder, auth_tokens):
    """Create a folder share with edit permissions"""
    # Create the share
    share = models.FolderShare(
        folder_id=test_folder.id,
        user_id=test_users["collaborator"].id,
        permission_type="edit",
        invitation_accepted=True,
        invitation_email=test_users["collaborator"].email
    )
    db.add(share)
    db.commit()
    db.refresh(share)
    return share

@pytest.fixture
def test_flashcard(db, test_users, test_folder):
    """Create a test flashcard in the test folder"""
    flashcard = models.Flashcard(
        question="Test Question",
        answer="Test Answer",
        folder_id=test_folder.id,
        user_id=test_users["owner"].id
    )
    db.add(flashcard)
    db.commit()
    db.refresh(flashcard)
    return flashcard

def test_create_individual_flashcard(test_folder, auth_tokens):
    """Test creating an individual flashcard"""
    flashcard_data = {
        "question": "What is the capital of France?",
        "answer": "Paris",
        "folder_id": test_folder.id
    }
    
    response = client.post(
        "/flashcards",
        json=flashcard_data,
        headers=auth_tokens["owner"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == flashcard_data["question"]
    assert data["answer"] == flashcard_data["answer"]
    assert data["folder_id"] == test_folder.id

def test_collaborator_create_flashcard(test_folder, auth_tokens, shared_folder):
    """Test that a collaborator with edit permissions can create a flashcard"""
    flashcard_data = {
        "question": "What is the capital of Germany?",
        "answer": "Berlin",
        "folder_id": test_folder.id
    }
    
    response = client.post(
        "/flashcards",
        json=flashcard_data,
        headers=auth_tokens["collaborator"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == flashcard_data["question"]
    assert data["user_id"] == shared_folder.user_id  # Should be created by the collaborator

def test_get_folder_flashcards(test_folder, auth_tokens, db, test_users):
    """Test getting all flashcards in a folder"""
    # Create multiple flashcards
    for i in range(3):
        flashcard = models.Flashcard(
            question=f"Question {i}",
            answer=f"Answer {i}",
            folder_id=test_folder.id,
            user_id=test_users["owner"].id
        )
        db.add(flashcard)
    
    db.commit()
    
    # Get flashcards
    response = client.get(
        f"/folders/{test_folder.id}/flashcards",
        headers=auth_tokens["owner"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "flashcards" in data
    assert len(data["flashcards"]) >= 3

def test_get_individual_flashcard(test_flashcard, auth_tokens):
    """Test getting a specific flashcard"""
    response = client.get(
        f"/flashcards/{test_flashcard.id}",
        headers=auth_tokens["owner"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_flashcard.id
    assert data["question"] == test_flashcard.question
    assert data["answer"] == test_flashcard.answer

def test_collaborator_access_flashcard(test_flashcard, auth_tokens, shared_folder):
    """Test that a collaborator can access a flashcard in a shared folder"""
    response = client.get(
        f"/flashcards/{test_flashcard.id}",
        headers=auth_tokens["collaborator"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_flashcard.id

def test_update_flashcard(test_flashcard, auth_tokens):
    """Test updating a flashcard"""
    update_data = {
        "question": "Updated Question",
        "answer": "Updated Answer"
    }
    
    response = client.put(
        f"/flashcards/{test_flashcard.id}",
        json=update_data,
        headers=auth_tokens["owner"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_flashcard.id
    assert data["question"] == update_data["question"]
    assert data["answer"] == update_data["answer"]

def test_collaborator_update_flashcard(test_flashcard, auth_tokens, shared_folder):
    """Test that a collaborator with edit permissions can update a flashcard"""
    update_data = {
        "question": "Collaborator Updated Question",
        "answer": "Collaborator Updated Answer"
    }
    
    response = client.put(
        f"/flashcards/{test_flashcard.id}",
        json=update_data,
        headers=auth_tokens["collaborator"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == update_data["question"]

def test_partial_update_flashcard(test_flashcard, auth_tokens):
    """Test partial update of a flashcard (only question or only answer)"""
    # Update only the question
    update_data = {
        "question": "Only Question Updated"
    }
    
    response = client.put(
        f"/flashcards/{test_flashcard.id}",
        json=update_data,
        headers=auth_tokens["owner"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == update_data["question"]
    assert data["answer"] == test_flashcard.answer  # Should be unchanged

def test_delete_flashcard(test_folder, auth_tokens, db, test_users):
    """Test deleting a flashcard"""
    # Create a flashcard to delete
    flashcard = models.Flashcard(
        question="Delete Me",
        answer="Delete Answer",
        folder_id=test_folder.id,
        user_id=test_users["owner"].id
    )
    db.add(flashcard)
    db.commit()
    db.refresh(flashcard)
    
    # Delete the flashcard
    response = client.delete(
        f"/flashcards/{flashcard.id}",
        headers=auth_tokens["owner"]
    )
    
    assert response.status_code == 204
    
    # Try to get the deleted flashcard
    response = client.get(
        f"/flashcards/{flashcard.id}",
        headers=auth_tokens["owner"]
    )
    
    # Should return 404 Not Found
    assert response.status_code == 404

def test_move_flashcard_between_folders(test_folder, auth_tokens, db, test_users):
    """Test moving a flashcard to a different folder"""
    # Create a second folder
    second_folder = models.StudyFolder(
        name="Second Test Folder",
        description="Another test folder",
        user_id=test_users["owner"].id
    )
    db.add(second_folder)
    db.commit()
    db.refresh(second_folder)
    
    # Create a flashcard in the first folder
    flashcard = models.Flashcard(
        question="Move Me",
        answer="Move Answer",
        folder_id=test_folder.id,
        user_id=test_users["owner"].id
    )
    db.add(flashcard)
    db.commit()
    db.refresh(flashcard)
    
    # Move the flashcard to the second folder
    update_data = {
        "folder_id": second_folder.id
    }
    
    response = client.put(
        f"/flashcards/{flashcard.id}",
        json=update_data,
        headers=auth_tokens["owner"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["folder_id"] == second_folder.id

def test_get_all_user_flashcards(auth_tokens, db, test_users):
    """Test getting all flashcards belonging to a user across folders"""
    # Create multiple folders
    folders = []
    for i in range(2):
        folder = models.StudyFolder(
            name=f"Folder {i}",
            description=f"Description {i}",
            user_id=test_users["owner"].id
        )
        db.add(folder)
        db.commit()
        db.refresh(folder)
        folders.append(folder)
    
    # Create flashcards in different folders
    for i, folder in enumerate(folders):
        for j in range(2):
            flashcard = models.Flashcard(
                question=f"Question {i}-{j}",
                answer=f"Answer {i}-{j}",
                folder_id=folder.id,
                user_id=test_users["owner"].id
            )
            db.add(flashcard)
    
    db.commit()
    
    # Get all flashcards
    response = client.get(
        "/flashcards",
        headers=auth_tokens["owner"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "flashcards" in data
    assert len(data["flashcards"]) >= 4  # At least 4 flashcards (2 per folder) 