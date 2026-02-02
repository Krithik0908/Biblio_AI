from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
import datetime
import json

from app.database import get_db
from app.auth import get_current_active_user
from app import models, schemas, crud
from app.ai import recommender, nlp_search, predictor

router = APIRouter()

# ========== BOOK ENDPOINTS ==========
@router.get("/books", response_model=List[schemas.BookResponse])
async def get_books(
    skip: int = 0,
    limit: int = 100,
    genre: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all books with optional filtering"""
    query = db.query(models.Book)
    
    if genre:
        query = query.filter(models.Book.genre == genre)
    
    books = query.offset(skip).limit(limit).all()
    return books

@router.get("/books/{book_id}", response_model=schemas.BookResponse)
async def get_book(
    book_id: UUID,
    db: Session = Depends(get_db)
):
    """Get specific book by ID"""
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Increment views
    book.views += 1
    db.commit()
    
    return book

@router.post("/books", response_model=schemas.BookResponse)
async def create_book(
    book: schemas.BookCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new book (Librarian/Admin only)"""
    if current_user.role not in [models.UserRole.LIBRARIAN, models.UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if ISBN already exists
    existing = db.query(models.Book).filter(models.Book.isbn == book.isbn).first()
    if existing:
        raise HTTPException(status_code=400, detail="ISBN already exists")
    
    new_book = crud.create_book(db, book)
    return new_book

@router.put("/books/{book_id}")
async def update_book(
    book_id: UUID,
    book_update: schemas.BookUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update book details"""
    if current_user.role not in [models.UserRole.LIBRARIAN, models.UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    updated = crud.update_book(db, book_id, book_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return {"message": "Book updated successfully"}

@router.delete("/books/{book_id}")
async def delete_book(
    book_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete book (Admin only)"""
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(book)
    db.commit()
    
    return {"message": "Book deleted successfully"}

# ========== SEARCH ENDPOINTS ==========
@router.get("/search", response_model=List[schemas.SearchResult])
async def search_books(
    q: str = Query(..., min_length=1),
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Search books by title/author (traditional)"""
    books = crud.search_books_by_title(db, q, limit)
    
    results = []
    for book in books:
        results.append(schemas.SearchResult(
            book=book,
            similarity_score=1.0  # Exact match
        ))
    
    return results

@router.get("/search/semantic", response_model=List[schemas.SearchResult])
async def semantic_search(
    q: str = Query(..., min_length=1),
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """AI-powered semantic search"""
    # Use traditional search if AI not ready
    if not nlp_search.is_initialized():
        return await search_books(q, limit, db)
    
    # Get semantic search results
    similar_books = nlp_search.find_similar_books(q, limit, db)
    return similar_books

# ========== BORROWING ENDPOINTS ==========
@router.post("/borrow", response_model=schemas.BorrowingResponse)
async def borrow_book(
    borrow_data: schemas.BorrowingCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Borrow a book"""
    try:
        borrowing = crud.create_borrowing(db, borrow_data, current_user.id)
        return borrowing
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/return/{borrowing_id}")
async def return_book(
    borrowing_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Return a borrowed book"""
    borrowing = crud.return_book(db, borrowing_id)
    if not borrowing:
        raise HTTPException(status_code=404, detail="Borrowing record not found")
    
    if borrowing.user_id != current_user.id and current_user.role == models.UserRole.READER:
        raise HTTPException(status_code=403, detail="Cannot return others' books")
    
    return {"message": "Book returned successfully", "fine": borrowing.fine_amount}

@router.get("/my-borrowings", response_model=List[schemas.BorrowingResponse])
async def get_my_borrowings(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's current borrowings"""
    borrowings = crud.get_user_borrowings(db, current_user.id)
    return borrowings

# ========== READING ENDPOINTS ==========
@router.post("/reading/start", response_model=schemas.ReadingSessionResponse)
async def start_reading_session(
    session_data: schemas.ReadingSessionCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start a reading session"""
    # Check if user has borrowed the book
    borrowing = db.query(models.Borrowing).filter(
        models.Borrowing.user_id == current_user.id,
        models.Borrowing.book_id == session_data.book_id,
        models.Borrowing.status == models.BookStatus.BORROWED
    ).first()
    
    if not borrowing and current_user.role == models.UserRole.READER:
        raise HTTPException(
            status_code=400, 
            detail="You need to borrow the book first"
        )
    
    session = crud.create_reading_session(db, session_data, current_user.id)
    return session

@router.post("/reading/end/{session_id}")
async def end_reading_session(
    session_id: UUID,
    pages_read: int = Query(..., gt=0),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """End a reading session"""
    session = db.query(models.ReadingSession).filter(
        models.ReadingSession.id == session_id,
        models.ReadingSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.end_time = datetime.datetime.utcnow()
    session.pages_read = pages_read
    
    # Calculate duration
    duration = (session.end_time - session.start_time).total_seconds() / 60
    session.duration_minutes = int(duration)
    
    # Update user reading time
    current_user.total_reading_time += session.duration_minutes
    
    db.commit()
    
    return {
        "message": "Reading session ended",
        "duration_minutes": session.duration_minutes,
        "total_reading_time": current_user.total_reading_time
    }

@router.get("/reading/stats", response_model=schemas.ReadingStats)
async def get_reading_stats(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's reading statistics"""
    # Get all reading sessions
    sessions = crud.get_user_reading_sessions(db, current_user.id, limit=1000)
    
    # Calculate stats
    total_books = len(set([s.book_id for s in sessions]))
    total_pages = sum([s.pages_read or 0 for s in sessions])
    total_time = sum([s.duration_minutes or 0 for s in sessions])
    
    # Get favorite genre
    book_ids = [s.book_id for s in sessions]
    if book_ids:
        genre_counts = db.query(
            models.Book.genre, 
            func.count(models.Book.genre)
        ).filter(
            models.Book.id.in_(book_ids)
        ).group_by(models.Book.genre).all()
        
        favorite_genre = max(genre_counts, key=lambda x: x[1])[0] if genre_counts else "None"
    else:
        favorite_genre = "None"
    
    # Calculate monthly reading
    monthly_data = {}
    for session in sessions:
        month_key = session.start_time.strftime("%Y-%m")
        monthly_data[month_key] = monthly_data.get(month_key, 0) + (session.duration_minutes or 0)
    
    # Get streak info
    from app.crud import update_streak
    update_streak(db, current_user.id)
    
    return schemas.ReadingStats(
        total_books_read=total_books,
        total_pages_read=total_pages,
        total_reading_time=total_time,
        current_streak=current_user.streak_count,
        longest_streak=current_user.streak_count,  # Simplified
        favorite_genre=favorite_genre,
        monthly_reading=monthly_data
    )

# ========== REVIEW ENDPOINTS ==========
@router.post("/reviews", response_model=schemas.ReviewResponse)
async def create_review(
    review: schemas.ReviewCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a book review"""
    try:
        new_review = crud.create_review(db, review, current_user.id)
        return new_review
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/books/{book_id}/reviews", response_model=List[schemas.ReviewResponse])
async def get_book_reviews(
    book_id: UUID,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get reviews for a book"""
    reviews = crud.get_book_reviews(db, book_id)
    return reviews[skip:skip + limit]

# ========== AI RECOMMENDATION ENDPOINTS ==========
@router.get("/recommendations", response_model=List[schemas.BookRecommendation])
async def get_recommendations(
    current_user: models.User = Depends(get_current_active_user),
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get AI-powered book recommendations"""
    # If AI not ready, return popular books
    if not recommender.is_initialized():
        popular = crud.get_popular_books(db, limit)
        return [
            schemas.BookRecommendation(
                book=book,
                score=0.8,
                reason="Popular among readers"
            )
            for book in popular
        ]
    
    # Get user's last borrowed book
    last_borrowing = db.query(models.Borrowing).filter(
        models.Borrowing.user_id == current_user.id
    ).order_by(models.Borrowing.borrowed_date.desc()).first()
    
    recommendations = []
    
    if last_borrowing:
        # Content-based recommendations
        content_recs = recommender.get_content_based_recommendations(
            last_borrowing.book_id, 
            limit // 2
        )
        
        for rec in content_recs:
            book = crud.get_book(db, rec["book_id"])
            if book:
                recommendations.append(schemas.BookRecommendation(
                    book=book,
                    score=rec["score"],
                    reason=rec["reason"]
                ))
    
    # Fill remaining with popular books
    if len(recommendations) < limit:
        remaining = limit - len(recommendations)
        popular = crud.get_popular_books(db, remaining)
        
        for book in popular:
            if book.id not in [r.book.id for r in recommendations]:
                recommendations.append(schemas.BookRecommendation(
                    book=book,
                    score=0.7,
                    reason="Trending now"
                ))
    
    return recommendations[:limit]

@router.get("/recommendations/{book_id}", response_model=List[schemas.BookRecommendation])
async def get_book_recommendations(
    book_id: UUID,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """Get books similar to a specific book"""
    if not recommender.is_initialized():
        return []
    
    recommendations = recommender.get_content_based_recommendations(book_id, limit)
    
    result = []
    for rec in recommendations:
        book = crud.get_book(db, rec["book_id"])
        if book:
            result.append(schemas.BookRecommendation(
                book=book,
                score=rec["score"],
                reason=rec["reason"]
            ))
    
    return result

# ========== ANALYTICS ENDPOINTS ==========
@router.get("/analytics/library", response_model=schemas.LibraryAnalytics)
async def get_library_analytics(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get library-wide analytics (Librarian/Admin only)"""
    if current_user.role not in [models.UserRole.LIBRARIAN, models.UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Basic counts
    total_books = db.query(models.Book).count()
    total_users = db.query(models.User).count()
    active_borrowings = db.query(models.Borrowing).filter(
        models.Borrowing.status == models.BookStatus.BORROWED
    ).count()
    
    # Popular books
    popular_books = crud.get_popular_books(db, 10)
    
    # Demand predictions
    predictions = []
    if predictor.is_initialized():
        predictions = predictor.get_demand_predictions(db, limit=5)
    
    return schemas.LibraryAnalytics(
        total_books=total_books,
        total_users=total_users,
        active_borrowings=active_borrowings,
        popular_books=popular_books,
        demand_predictions=predictions
    )

# ========== POPULAR & TRENDING ==========
@router.get("/books/popular", response_model=List[schemas.BookResponse])
async def get_popular_books(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get most popular books"""
    return crud.get_popular_books(db, limit)

@router.get("/books/trending", response_model=List[schemas.BookResponse])
async def get_trending_books(
    days: int = 7,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get recently popular books"""
    since_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    
    trending = db.query(
        models.Book,
        func.count(models.Borrowing.id).label('recent_borrows')
    ).join(
        models.Borrowing,
        models.Borrowing.book_id == models.Book.id
    ).filter(
        models.Borrowing.borrowed_date >= since_date
    ).group_by(
        models.Book.id
    ).order_by(
        func.count(models.Borrowing.id).desc()
    ).limit(limit).all()
    
    return [book for book, _ in trending]

# ========== USER PROFILE ==========
@router.get("/profile/stats")
async def get_user_profile_stats(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive user profile data"""
    stats = await get_reading_stats(current_user, db)
    
    # Get currently borrowed books
    current_borrowings = db.query(models.Borrowing).filter(
        models.Borrowing.user_id == current_user.id,
        models.Borrowing.status == models.BookStatus.BORROWED
    ).all()
    
    # Get reading history
    reading_sessions = crud.get_user_reading_sessions(db, current_user.id, limit=20)
    
    return {
        "user_info": {
            "name": current_user.name,
            "email": current_user.email,
            "streak": current_user.streak_count,
            "total_reading_hours": round(current_user.total_reading_time / 60, 1)
        },
        "reading_stats": stats.dict(),
        "current_borrowings": [
            {
                "book_title": crud.get_book(db, b.book_id).title if crud.get_book(db, b.book_id) else "Unknown",
                "due_date": b.due_date,
                "days_remaining": (b.due_date - datetime.datetime.utcnow()).days
            }
            for b in current_borrowings
        ],
        "recent_reading": [
            {
                "book_title": crud.get_book(db, s.book_id).title if crud.get_book(db, s.book_id) else "Unknown",
                "date": s.start_time.date(),
                "duration_minutes": s.duration_minutes or 0,
                "pages_read": s.pages_read or 0
            }
            for s in reading_sessions[:5]
        ]
    }