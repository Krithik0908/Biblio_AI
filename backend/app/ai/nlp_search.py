import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os
import logging
from sqlalchemy.orm import Session
from uuid import UUID

from app import schemas, crud

logger = logging.getLogger(__name__)

class SemanticSearch:
    def __init__(self):
        self.model = None
        self.index = None
        self.book_ids = []
        self.book_data = []
        self.is_initialized_flag = False
        self.model_path = "models/semantic_search.pkl"
        
    async def initialize_model(self, db: Session = None):
        """Initialize semantic search model"""
        try:
            if os.path.exists(self.model_path):
                logger.info("Loading semantic search model...")
                with open(self.model_path, 'rb') as f:
                    self.model, self.index, self.book_ids, self.book_data = pickle.load(f)
            else:
                logger.info("Downloading and setting up semantic model...")
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                
                if db:
                    await self.build_index(db)
            
            self.is_initialized_flag = True
            logger.info(f"Semantic search initialized with {len(self.book_ids)} books")
            
        except Exception as e:
            logger.error(f"Error initializing semantic search: {e}")
            self.is_initialized_flag = False
    
    async def build_index(self, db: Session):
        """Build FAISS index from books"""
        from app import models
        
        books = db.query(models.Book).all()
        
        if not books:
            logger.warning("No books to index")
            return
        
        # Prepare text for embedding
        texts = []
        self.book_ids = []
        self.book_data = []
        
        for book in books:
            # Create rich text representation
            text = f"Title: {book.title}. Author: {book.author}. Genre: {book.genre}."
            if book.description:
                text += f" Description: {book.description[:200]}"
            if book.sub_genre:
                text += f" Sub-genre: {book.sub_genre}."
            
            texts.append(text)
            self.book_ids.append(book.id)
            self.book_data.append({
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "genre": str(book.genre)
            })
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} books...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        
        # Save model
        os.makedirs("models", exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump((self.model, self.index, self.book_ids, self.book_data), f)
        
        logger.info(f"FAISS index built with {self.index.ntotal} vectors")
    
    def find_similar_books(
        self, 
        query: str, 
        limit: int = 10,
        db: Session = None
    ) -> List[schemas.SearchResult]:
        """Find books similar to query"""
        if not self.is_initialized():
            return []
        
        # Encode query
        query_embedding = self.model.encode([query])
        
        # Search in index
        distances, indices = self.index.search(
            query_embedding.astype('float32'), 
            min(limit * 2, len(self.book_ids))
        )
        
        # Prepare results
        results = []
        seen_books = set()
        
        for i, idx in enumerate(indices[0]):
            if idx < len(self.book_ids) and idx >= 0:
                book_id = self.book_ids[idx]
                
                # Avoid duplicates
                if book_id in seen_books:
                    continue
                
                # Get book from database
                if db:
                    book = crud.get_book(db, book_id)
                else:
                    # Use cached data
                    book_data = self.book_data[idx]
                    book = type('Book', (), {
                        'id': book_id,
                        'title': book_data['title'],
                        'author': book_data['author'],
                        'genre': book_data['genre']
                    })()
                
                if book:
                    # Convert distance to similarity score (0-1)
                    similarity = 1.0 / (1.0 + distances[0][i])
                    
                    results.append(schemas.SearchResult(
                        book=book,
                        similarity_score=float(similarity)
                    ))
                    seen_books.add(book_id)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def find_similar_to_book(
        self, 
        book_id: UUID, 
        limit: int = 5,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Find books similar to a given book"""
        if not self.is_initialized():
            return []
        
        # Find book index
        try:
            book_idx = self.book_ids.index(book_id)
        except ValueError:
            return []
        
        # Get book embedding from index (we need to reconstruct)
        # For simplicity, we'll use the query method
        book_data = self.book_data[book_idx]
        query_text = f"Title: {book_data['title']}. Author: {book_data['author']}."
        
        similar = self.find_similar_books(query_text, limit + 1, db)
        
        # Remove the book itself from results
        return [
            result for result in similar 
            if str(result.book.id) != str(book_id)
        ][:limit]
    
    def is_initialized(self):
        return self.is_initialized_flag

# Global instance
semantic_search = SemanticSearch()

# Convenience functions
async def initialize_model(db: Session = None):
    return await semantic_search.initialize_model(db)

def is_initialized():
    return semantic_search.is_initialized()

def find_similar_books(query: str, limit: int = 10, db: Session = None):
    return semantic_search.find_similar_books(query, limit, db)