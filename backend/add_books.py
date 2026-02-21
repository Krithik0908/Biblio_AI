# backend/add_books.py
import requests
import json

BASE_URL = "http://localhost:3000"

SAMPLE_BOOKS = [
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "description": "A story of decadence and idealism in the Jazz Age",
        "cover_url": "https://m.media-amazon.com/images/I/71FTb9X6wsL._AC_UF1000,1000_QL80_.jpg",
        "isbn": "9780743273565",
        "published_year": 1925,
        "genre": "Classic",
        "rating": 4.2
    },
    {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "description": "A novel about racial injustice and moral growth",
        "cover_url": "https://m.media-amazon.com/images/I/71FxgtFKcQL._AC_UF1000,1000_QL80_.jpg",
        "isbn": "9780446310789",
        "published_year": 1960,
        "genre": "Fiction",
        "rating": 4.3
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "description": "A dystopian social science fiction novel",
        "cover_url": "https://m.media-amazon.com/images/I/71kxa1-0mfL._AC_UF1000,1000_QL80_.jpg",
        "isbn": "9780451524935",
        "published_year": 1949,
        "genre": "Dystopian",
        "rating": 4.2
    },
    {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "description": "A romantic novel of manners",
        "cover_url": "https://m.media-amazon.com/images/I/71Q1tPupKjL._AC_UF1000,1000_QL80_.jpg",
        "isbn": "9780141439518",
        "published_year": 1813,
        "genre": "Romance",
        "rating": 4.3
    },
    {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "description": "A fantasy novel about Bilbo Baggins' adventure",
        "cover_url": "https://m.media-amazon.com/images/I/710+HcoP38L._AC_UF1000,1000_QL80_.jpg",
        "isbn": "9780547928227",
        "published_year": 1937,
        "genre": "Fantasy",
        "rating": 4.3
    }
]

def add_books():
    print("Adding sample books to database...")
    
    for i, book in enumerate(SAMPLE_BOOKS, 1):
        try:
            response = requests.post(f"{BASE_URL}/books", json=book)
            if response.status_code in [200, 201]:
                print(f"✅ Book {i}: {book['title']} - Added successfully")
            else:
                print(f"❌ Book {i}: {book['title']} - Failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Book {i}: {book['title']} - Error: {str(e)}")
    
    print("\n✅ Done! Check your frontend now.")

if __name__ == "__main__":
    add_books()