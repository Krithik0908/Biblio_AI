from pydantic import BaseModel
from typing import Optional, Dict, Any, List

# User schemas
class UserBase(BaseModel):
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class UserInDB(UserBase):
    id: int
    hashed_password: str
    preferences: Optional[Dict[str, Any]] = None

class User(UserBase):
    id: int
    preferences: Optional[Dict[str, Any]] = None

# Book schemas
class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    genre: Optional[str] = None
    description: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None

class Book(BookBase):
    id: int
    available: bool = True

# Borrowing schemas
class BorrowBase(BaseModel):
    user_id: int
    book_id: int

class BorrowCreate(BorrowBase):
    pass

class Borrow(BorrowBase):
    id: int
    borrow_date: str
    return_date: Optional[str] = None
    returned: bool = False

# AI Recommendation schemas
class RecommendationRequest(BaseModel):
    user_id: int
    limit: int = 5

class RecommendationResponse(BaseModel):
    book_id: int
    title: str
    author: str
    confidence: float

# Search schemas
class SearchRequest(BaseModel):
    query: str
    limit: int = 10

class SearchResponse(BaseModel):
    books: List[Book]

# Health check
class HealthResponse(BaseModel):
    status: str
    database: bool
    ai_models: Dict[str, bool]

# Add these to the BOTTOM of your schemas.py file (after the existing content)

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = Non
    phone: Optional[str] = None 
# Response schemas for API endpoints 
class UserResponse(BaseModel): 
    id: int 
    email: str 
    name: Optional[str] = None 
    phone: Optional[str] = None 
    preferences: Optional[Dict[str, Any]] = None 
 
# Response schemas for API endpoints 
class UserResponse(BaseModel): 
    id: int 
    email: str 
    name: Optional[str] = None 
    phone: Optional[str] = None 
    preferences: Optional[Dict[str, Any]] = None 
