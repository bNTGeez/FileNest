from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os 
from dotenv import load_dotenv

load_dotenv()

def get_current_user():
    """
    Mock user ID for development
    """
    return "test-user-123"
    
    
