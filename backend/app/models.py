from sqlalchemy import (
    Column, Integer, String, Float, Boolean, 
    DateTime, ForeignKey, Text, Enum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.database import Base

# Enums
class UserRole(str, enum.Enum):
    READER = "reader"
    LIBRARIAN = "librarian"
    ADMIN = "admin"

class BookStatus(str, enum.Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"
    RESERVED = "reserved"
    OVERDUE = "overdue"

class Genre(str, enum.Enum):
    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    SCIENCE = "science"
    TECHNOLOGY = "technology"
    ROMANCE = "romance"
    HORROR = "horror"
    FANTASY = "fantasy"
    BIOGRAPHY = "biography"
    SELF_HELP = "self_help"
    REFERENCE = "reference"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(15), unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.READER)
    age_group = Column(String(20))  # child, teen, adult, senior
    preferences = Column(JSON, default=dict)  # {"genres": ["fiction", "scifi"]}
    streak_count = Column(Integer, default=0)
    last_read_date = Column(DateTime)
    total_reading_time = Column(Integer, default=0)  # in minutes
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    borrowings = relationship("Borrowing", back_populates="user")
    reading_sessions = relationship("ReadingSession", back_populates="user")
    reviews = relationship("Review", back_populates="user")

class Book(Base):
    __tablename__ = "books"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False, index=True)
    author = Column(String(200), nullable=False, index=True)
    isbn = Column(String(13), unique=True, index=True)
    genre = Column(Enum(Genre), nullable=False)
    sub_genre = Column(String(50))
    description = Column(Text)
    publication_year = Column(Integer)
    publisher = Column(String(100))
    total_copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)
    location = Column(String(50))  # Shelf location
    views = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    total_ratings = Column(Integer, default=0)
    cover_image_url = Column(String(500))
    book_embedding = Column(JSON)  # For semantic search
    
    # Relationships
    borrowings = relationship("Borrowing", back_populates="book")
    reading_sessions = relationship("ReadingSession", back_populates="book")
    reviews = relationship("Review", back_populates="book")
    
    def update_rating(self, new_rating):
        """Update book rating with new review"""
        total_score = (self.rating * self.total_ratings) + new_rating
        self.total_ratings += 1
        self.rating = total_score / self.total_ratings

class Borrowing(Base):
    __tablename__ = "borrowings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)
    borrowed_date = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True))
    returned_date = Column(DateTime(timezone=True))
    status = Column(Enum(BookStatus), default=BookStatus.BORROWED)
    fine_amount = Column(Float, default=0.0)
    
    # Relationships
    user = relationship("User", back_populates="borrowings")
    book = relationship("Book", back_populates="borrowings")

class ReadingSession(Base):
    __tablename__ = "reading_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)  # Session duration
    pages_read = Column(Integer)
    progress_percentage = Column(Float)  # 0-100
    device_info = Column(JSON)
    
    # Relationships
    user = relationship("User", back_populates="reading_sessions")
    book = relationship("Book", back_populates="reading_sessions")

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text)
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    book = relationship("Book", back_populates="reviews")

class DemandPrediction(Base):
    __tablename__ = "demand_predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)
    prediction_date = Column(DateTime(timezone=True), server_default=func.now())
    predicted_demand = Column(Integer)
    confidence_score = Column(Float)
    factors_considered = Column(JSON)  # {"trends": [], "seasons": []}
    
    # Relationship
    book = relationship("Book")