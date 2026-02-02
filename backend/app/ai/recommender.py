import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import pickle
import os
import asyncio
import logging
from datetime import datetime, timedelta
from uuid import UUID

logger = logging.getLogger(__name__)

class RecommendationEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=10000)
        self.book_vectors = None
        self.book_ids = []
        self.model_initialized = False
        self.model_path = "models/recommender.pkl"
        
    async def initialize_model(self, db: Session = None):
        """Initialize or load recommendation model"""
        try:
            if os.path.exists(self.model_path):
                logger.info("Loading pre-trained recommendation model...")
                with open(self.model_path, 'rb') as f:
                    self.vectorizer, self.book_vectors, self.book_ids = pickle.load(f)
            else:
                logger.info("Training new recommendation model...")
                if db:
                    await self.train_model(db)
            
            self.model_initialized = True
            logger.info(f"Recommendation model initialized with {len(self.book_ids)} books")
            
        except Exception as e:
            logger.error(f"Error initializing recommendation model: {e}")
            self.model_initialized = False
    
    async def train_model(self, db: Session):
        """Train recommendation model using book data"""
        from app import crud, models
        
        # Get all books
        books = db.query(models.Book).all()
        
        if not books:
            logger.warning("No books found for training")
            return
        
        # Prepare book features
        book_texts = []
        self.book_ids = []
        
        for book in books:
            # Combine title, author, genre, description
            text = f"{book.title} {book.author} {book.genre} {book.sub_genre or ''} {book.description or ''}"
            book_texts.append(text)
            self.book_ids.append(book.id)
        
        # Create TF-IDF vectors
        self.book_vectors = self.vectorizer.fit_transform(book_texts)
        
        # Save model
        os.makedirs("models", exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump((self.vectorizer, self.book_vectors, self.book_ids), f)
        
        logger.info(f"Model trained with {len(books)} books")
    
    def get_content_based_recommendations(
        self, 
        book_id: UUID, 
        n_recommendations: int = 5
    ) -> List[Dict[str, Any]]:
        """Get similar books based on content"""
        if not self.model_initialized:
            raise RuntimeError("Recommendation model not initialized")
        
        # Find book index
        try:
            book_idx = self.book_ids.index(book_id)
        except ValueError:
            return []
        
        # Calculate similarities
        book_vector = self.book_vectors[book_idx]
        similarities = cosine_similarity(book_vector, self.book_vectors).flatten()
        
        # Get top similar books (excluding itself)
        similar_indices = similarities.argsort()[::-1][1:n_recommendations+1]
        
        recommendations = []
        for idx in similar_indices:
            recommendations.append({
                "book_id": self.book_ids[idx],
                "score": float(similarities[idx]),
                "reason": "Similar content"
            })
        
        return recommendations
    
    def get_collaborative_recommendations(
        self, 
        user_id: UUID, 
        db: Session, 
        n_recommendations: int = 5
    ) -> List[Dict[str, Any]]:
        """Get recommendations based on similar users"""
        from app import models
        
        # Get user's borrowing history
        user_borrowings = db.query(models.Borrowing)\
            .filter(models.Borrowing.user_id == user_id)\
            .all()
        
        if not user_borrowings:
            return []
        
        # Get all borrowings to find similar users
        all_borrowings = db.query(models.Borrowing).all()
        
        # Create user-book matrix (simplified)
        user_books = {}
        for b in all_borrowings:
            user_books.setdefault(str(b.user_id),