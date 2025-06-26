from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from ..database import get_db
from .. import crud, schemas, auth
from ..config import settings

router = APIRouter()

# Request/Response schemas for authentication
class UserRegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: schemas.User

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: str

@router.post("/register", response_model=UserResponse)
def register(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Create a new user account
    
    - **email**: User's email address (must be unique)
    - **username**: User's username (must be unique)
    - **password**: User's password (will be hashed)
    """
    # Check if email already exists
    db_user = crud.get_user_by_email(db, email=user_data.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    
    # Check if username already exists
    db_user = crud.get_user_by_username(db, username=user_data.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username already taken"
        )
    
    # Create user schema and save to database
    user_create = schemas.UserCreate(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password
    )
    
    user = crud.create_user(db=db, user=user_create)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        is_active=user.is_active,
        created_at=user.created_at.isoformat()
    )

@router.post("/login", response_model=UserLoginResponse)
async def login(user_data: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token
    
    - **username**: User's username or email
    - **password**: User's password
    """
    # Authenticate user
    user = auth.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = auth.create_access_token(email=user.email)
    
    return UserLoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=schemas.User(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Get current authenticated user information
    
    Requires valid JWT token in Authorization header
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat()
    ) 