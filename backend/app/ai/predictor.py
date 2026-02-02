import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pickle
import os
import logging
from sqlalchemy.orm import Session
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import holidays

logger = logging.getLogger(__name__)

class DemandPredictor:
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self.is_initialized_flag = False
        self.model_path = "models/demand_predictor.pkl"
        
    async def initialize_model(self, db: Session = None):
        """Initialize demand prediction model"""
        try:
            if os.path.exists(self.model_path):
                logger.info("Loading demand prediction model...")
                with open(self.model_path, 'rb') as f:
                    self.model, self.label_encoders = pickle.load(f)
            else:
                logger.info("Creating new demand prediction model...")
                self.model = RandomForestRegressor(n_estimators=100, random_state=42)
                
                if db:
                    await self.train_model(db)
            
            self.is_initialized_flag = True
            logger.info("Demand prediction model initialized")
            
        except Exception as e:
            logger.error(f"Error initializing demand predictor: {e}")
            self.is_initialized_flag = False
    
    async def train_model(self, db: Session):
        """Train demand prediction model"""
        from app import models
        
        # Get historical borrowing data
        borrowings = db.query(models.Borrowing).all()
        
        if len(borrowings) < 100:  # Need sufficient data
            logger.warning(f"Not enough data ({len(borrowings)} records) for training")
            return
        
        # Prepare training data
        data = []
        for b in borrowings:
            book = db.query(models.Book).filter(models.Book.id == b.book_id).first()
            if not book:
                continue
            
            # Extract features
            borrow_date = b.borrowed_date
            
            data.append({
                'book_genre': str(book.genre),
                'book_author': book.author[:50],  # Limit length
                'month': borrow_date.month,
                'day_of_week': borrow_date.weekday(),
                'is_weekend': 1 if borrow_date.weekday() >= 5 else 0,
                'is_holiday': self._is_holiday(borrow_date),
                'book_popularity': book.views / max(book.total_copies, 1),
                'target': 1  # Demand occurred
            })
        
        if not data:
            return
        
        df = pd.DataFrame(data)
        
        # Encode categorical features
        for col in ['book_genre', 'book_author']:
            if col in df.columns:
                self.label_encoders[col] = LabelEncoder()
                df[col] = self.label_encoders[col].fit_transform(df[col])
        
        # Prepare features and target
        feature_cols = ['book_genre', 'book_author', 'month', 'day_of_week', 
                       'is_weekend', 'is_holiday', 'book_popularity']
        X = df[feature_cols].values
        y = df['target'].values
        
        # Train model
        self.model.fit(X, y)
        
        # Save model
        os.makedirs("models", exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump((self.model, self.label_encoders), f)
        
        logger.info(f"Model trained with {len(X)} samples")
    
    def _is_holiday(self, date: datetime) -> int:
        """Check if date is a holiday (India)"""
        in_holidays = holidays.India()
        return 1 if date.date() in in_holidays else 0
    
    def predict_demand(
        self, 
        book_id: str, 
        db: Session, 
        days_ahead: int = 7
    ) -> Dict[str, Any]:
        """Predict demand for a specific book"""
        if not self.is_initialized():
            return {"error": "Model not initialized"}
        
        from app import models
        
        book = db.query(models.Book).filter(models.Book.id == book_id).first()
        if not book:
            return {"error": "Book not found"}
        
        # Prepare prediction for next 'days_ahead' days
        predictions = []
        today = datetime.utcnow()
        
        for i in range(days_ahead):
            pred_date = today + timedelta(days=i)
            
            # Prepare features for this day
            features = {
                'book_genre': str(book.genre),
                'book_author': book.author[:50],
                'month': pred_date.month,
                'day_of_week': pred_date.weekday(),
                'is_weekend': 1 if pred_date.weekday() >= 5 else 0,
                'is_holiday': self._is_holiday(pred_date),
                'book_popularity': book.views / max(book.total_copies, 1)
            }
            
            # Encode categorical features
            encoded_features = []
            for col in ['book_genre', 'book_author']:
                if col in features and col in self.label_encoders:
                    try:
                        encoded = self.label_encoders[col].transform([features[col]])[0]
                        encoded_features.append(encoded)
                    except:
                        encoded_features.append(0)
                else:
                    encoded_features.append(0)
            
            # Add numerical features
            encoded_features.extend([
                features['month'],
                features['day_of_week'],
                features['is_weekend'],
                features['is_holiday'],
                features['book_popularity']
            ])
            
            # Make prediction
            prediction = self.model.predict([encoded_features])[0]
            
            predictions.append({
                'date': pred_date.strftime('%Y-%m-%d'),
                'predicted_demand': max(0, int(prediction * 10)),  # Scale
                'confidence': min(0.9, prediction)  # Cap confidence
            })
        
        # Calculate average prediction
        avg_demand = sum(p['predicted_demand'] for p in predictions) / len(predictions)
        
        return {
            'book_id': str(book_id),
            'book_title': book.title,
            'predictions': predictions,
            'average_daily_demand': round(avg_demand, 2),
            'recommended_stock': max(book.total_copies, int(avg_demand * 1.5)),
            'current_stock_status': 'adequate' if book.available_copies >= avg_demand else 'low'
        }
    
    def get_demand_predictions(
        self, 
        db: Session, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get demand predictions for top books"""
        from app import models
        
        # Get popular books
        popular_books = db.query(models.Book)\
            .order_by(models.Book.views.desc())\
            .limit(limit)\
            .all()
        
        predictions = []
        for book in popular_books:
            pred = self.predict_demand(book.id, db, days_ahead=3)
            if 'error' not in pred:
                predictions.append(pred)
        
        return predictions
    
    def is_initialized(self):
        return self.is_initialized_flag

# Global instance
demand_predictor = DemandPredictor()

# Convenience functions
async def initialize_model(db: Session = None):
    return await demand_predictor.initialize_model(db)

def is_initialized():
    return demand_predictor.is_initialized()

def get_demand_predictions(db: Session, limit: int = 5):
    return demand_predictor.get_demand_predictions(db, limit)