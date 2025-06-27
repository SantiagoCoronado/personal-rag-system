from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from .. import crud, schemas, auth
from ..config import settings

router = APIRouter()

# Request/Response models for login
class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: schemas.User

class TokenVerifyRequest(BaseModel):
    token: str

@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account
    
    - **email**: User's email address (must be unique)
    - **username**: User's username (must be unique)  
    - **password**: User's password (will be hashed)
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    return crud.create_user(db=db, user=user)

@router.post("/login", response_model=UserLoginResponse)
async def login(
    login_request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token
    
    - **username**: User's username or email
    - **password**: User's password
    """
    user = auth.authenticate_user(db, login_request.username, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token using email
    access_token = auth.create_access_token(email=user.email)
    
    return UserLoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )


@router.get("/me", response_model=schemas.User)
async def get_current_user_info(current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Get current authenticated user information
    
    Requires valid JWT token in Authorization header
    """
    return current_user

@router.post("/verify-token")
async def verify_token_endpoint(token_request: TokenVerifyRequest):
    """Verify a token and return the payload"""
    try:
        payload = auth.verify_token(token_request.token)
        return {"valid": True, "payload": payload}
    except HTTPException as e:
        return {"valid": False, "error": e.detail}