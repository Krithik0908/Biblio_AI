from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from uuid import UUID
import datetime
from app import models, schemas
from app.auth import get_password_hash

# User CRUD
def get_user(db: Session, user_id: UUID):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        password_hash=hashed_password,
        age_group=user.age_group,
        preferences=user.preferences or {}
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: UUID, user_update: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def update_streak(db: Session, user_id: UUID):
    db_user = get_user(db, user_id)
    if not db_user:
        return
    
    today = datetime.datetime.utcnow().date()
    last_read = db_user.last_read_date.date() if db_user.last_read_date else None
    
    if last_read:
        days_diff = (today - last_read).days
        if days_diff == 1:
            # Consecutive day
            db_user.streak_count += 1
        elif days_diff > 1:
            # Streak broken
            db_user.streak_count = 1
    else:
        # First time reading
        db_user.streak_count = 1
    
    db_user.last_read_date = datetime.datetime.utcnow()
    db.commit()

# Book CRUD
def get_book(db: Session, book_id: UUID):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def get_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Book).offset(skip).limit(limit).all()

def get_books_count(db: Session):
    return db.query(models.Book).count()

def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    
    # Increment views for popular books
    db_book.views += 1
    db.commit()
    
    return db_book

def update_book(db: Session, book_id: UUID, book_update: schemas.BookUpdate):
    db_book = get_book(db, book_id)
    if not db_book:
        return None
    
    update_data = book_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_book, field, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book

def search_books_by_title(db: Session, title: str, limit: int = 20):
    return db.query(models.Book)\
        .filter(models.Book.title.ilike(f"%{title}%"))\
        .limit(limit)\
        .all()

def get_popular_books(db: Session, limit: int = 10):
    return db.query(models.Book)\
        .order_by(desc(models.Book.views), desc(models.Book.rating))\
        .limit(limit)\
        .all()

# Borrowing CRUD
def create_borrowing(db: Session, borrowing: schemas.BorrowingCreate, user_id: UUID):
    # Check book availability
    book = get_book(db, borrowing.book_id)
    if not book or book.available_copies < 1:
        raise ValueError("Book not available")
    
    # Calculate due date
    due_date = datetime.datetime.utcnow() + datetime.timedelta(days=borrowing.due_days)
    
    db_borrowing = models.Borrowing(
        user_id=user_id,
        book_id=borrowing.book_id,
        due_date=due_date,
        status=models.BookStatus.BORROWED
    )
    
    # Update book availability
    book.available_copies -= 1
    
    db.add(db_borrowing)
    db.commit()
    db.refresh(db_borrowing)
    
    return db_borrowing

def return_book(db: Session, borrowing_id: UUID):
    borrowing = db.query(models.Borrowing).filter(models.Borrowing.id == borrowing_id).first()
    if not borrowing:
        return None
    
    # Update borrowing record
    borrowing.returned_date = datetime.datetime.utcnow()
    borrowing.status = models.BookStatus.AVAILABLE
    
    # Update book availability
    book = get_book(db, borrowing.book_id)
    if book:
        book.available_copies += 1
    
    # Calculate fine if overdue
    if borrowing.due_date < datetime.datetime.utcnow():
        days_overdue = (datetime.datetime.utcnow() - borrowing.due_date).days
        borrowing.fine_amount = days_overdue * 5  # $5 per day
    
    db.commit()
    return borrowing

def get_user_borrowings(db: Session, user_id: UUID):
    return db.query(models.Borrowing)\
        .filter(models.Borrowing.user_id == user_id)\
        .order_by(desc(models.Borrowing.borrowed_date))\
        .all()

# Reading Session CRUD
def create_reading_session(db: Session, session_data: schemas.ReadingSessionCreate, user_id: UUID):
    db_session = models.ReadingSession(
        user_id=user_id,
        **session_data.dict()
    )
    
    # Calculate duration if end_time is provided
    if db_session.end_time:
        duration = (db_session.end_time - db_session.start_time).total_seconds() / 60
        db_session.duration_minutes = int(duration)
        
        # Update user's total reading time
        user = get_user(db, user_id)
        if user:
            user.total_reading_time += db_session.duration_minutes
            update_streak(db, user_id)
    
    # Update book progress
    book = get_book(db, session_data.book_id)
    if book and session_data.progress_percentage >= 100:
        book.views += 1
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return db_session

def get_user_reading_sessions(db: Session, user_id: UUID, limit: int = 50):
    return db.query(models.ReadingSession)\
        .filter(models.ReadingSession.user_id == user_id)\
        .order_by(desc(models.ReadingSession.start_time))\
        .limit(limit)\
        .all()

# Review CRUD
def create_review(db: Session, review: schemas.ReviewCreate, user_id: UUID):
    # Check if user has already reviewed this book
    existing = db.query(models.Review).filter(
        and_(
            models.Review.user_id == user_id,
            models.Review.book_id == review.book_id
        )
    ).first()
    
    if existing:
        raise ValueError("You have already reviewed this book")
    
    db_review = models.Review(
        user_id=user_id,
        **review.dict()
    )
    
    # Update book rating
    book = get_book(db, review.book_id)
    if book:
        book.update_rating(review.rating)
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    return db_review

def get_book_reviews(db: Session, book_id: UUID):
    return db.query(models.Review)\
        .filter(models.Review.book_id == book_id)\
        .order_by(desc(models.Review.created_at))\
        .all()