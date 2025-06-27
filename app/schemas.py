from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Login schemas
class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: User

class UserRegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Document schemas
class DocumentBase(BaseModel):
    filename: str
    s3_url: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Embedding schemas
class EmbeddingBase(BaseModel):
    chunk_text: str
    chunk_index: int

class Embedding(EmbeddingBase):
    id: int
    document_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Query schemas
class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[dict]
    context_used: bool

class QueryHistoryEntry(BaseModel):
    id: int
    user_id: int
    query: str
    answer: str
    sources_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True