import { useState, useEffect } from 'react'
import { Search, Filter, Grid, List } from 'lucide-react'
import BookCard from '../components/BookCard'
import { booksAPI } from '../services/api'
import toast from 'react-hot-toast'

// MOCK DATA - Will show books immediately
const MOCK_BOOKS = [
  {
    id: 1,
    title: "The Great Gatsby",
    author: "F. Scott Fitzgerald",
    description: "A story of decadence and idealism in the Jazz Age",
    cover_url: "https://m.media-amazon.com/images/I/71FTb9X6wsL._AC_UF1000,1000_QL80_.jpg",
    rating: 4.2,
    genre: "Classic",
    published_year: 1925,
    pages: 218,
    isbn: "9780743273565"
  },
  {
    id: 2,
    title: "To Kill a Mockingbird",
    author: "Harper Lee",
    description: "A novel about racial injustice and moral growth",
    cover_url: "https://m.media-amazon.com/images/I/71FxgtFKcQL._AC_UF1000,1000_QL80_.jpg",
    rating: 4.3,
    genre: "Fiction",
    published_year: 1960,
    pages: 281,
    isbn: "9780446310789"
  },
  {
    id: 3,
    title: "1984",
    author: "George Orwell",
    description: "A dystopian social science fiction novel",
    cover_url: "https://m.media-amazon.com/images/I/71kxa1-0mfL._AC_UF1000,1000_QL80_.jpg",
    rating: 4.2,
    genre: "Dystopian",
    published_year: 1949,
    pages: 328,
    isbn: "9780451524935"
  },
  {
    id: 4,
    title: "Pride and Prejudice",
    author: "Jane Austen",
    description: "A romantic novel of manners",
    cover_url: "https://m.media-amazon.com/images/I/71Q1tPupKjL._AC_UF1000,1000_QL80_.jpg",
    rating: 4.3,
    genre: "Romance",
    published_year: 1813,
    pages: 432,
    isbn: "9780141439518"
  },
  {
    id: 5,
    title: "The Hobbit",
    author: "J.R.R. Tolkien",
    description: "A fantasy novel about Bilbo Baggins' adventure",
    cover_url: "https://m.media-amazon.com/images/I/710+HcoP38L._AC_UF1000,1000_QL80_.jpg",
    rating: 4.3,
    genre: "Fantasy",
    published_year: 1937,
    pages: 310,
    isbn: "9780547928227"
  },
  {
    id: 6,
    title: "Harry Potter and the Philosopher's Stone",
    author: "J.K. Rowling",
    description: "The first book in the Harry Potter series",
    cover_url: "https://m.media-amazon.com/images/I/81iqZ2HHD-L._AC_UF1000,1000_QL80_.jpg",
    rating: 4.5,
    genre: "Fantasy",
    published_year: 1997,
    pages: 223,
    isbn: "9780747532699"
  }
]

const Books = () => {
  const [books, setBooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState('grid')
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    fetchBooks()
  }, [])

  const fetchBooks = async () => {
    try {
      // Try to get books from backend
      const response = await booksAPI.getAll()
      
      // Check if backend returns valid data
      if (response.data && Array.isArray(response.data) && response.data.length > 0) {
        setBooks(response.data)
        console.log('Loaded books from backend:', response.data.length)
      } else if (response.data?.books && response.data.books.length > 0) {
        // If data is in response.data.books format
        setBooks(response.data.books)
        console.log('Loaded books from backend (nested):', response.data.books.length)
      } else {
        // If backend returns empty, use mock data
        console.log('Backend returned empty, using mock data')
        setBooks(MOCK_BOOKS)
      }
    } catch (error) {
      console.error('Failed to fetch books, using mock data:', error)
      // Use mock data if API fails
      setBooks(MOCK_BOOKS)
      toast.error('Using demo data. Backend connection failed.')
    } finally {
      setLoading(false)
    }
  }

  const filteredBooks = books.filter(book =>
    book.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    book.author?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    book.genre?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600 mb-4"></div>
        <p className="text-gray-600">Loading books...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Book Collection</h1>
          <p className="text-gray-600">
            Browse {filteredBooks.length} {filteredBooks.length === 1 ? 'book' : 'books'}
            {searchTerm && ` for "${searchTerm}"`}
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by title, author, or genre..."
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg w-full sm:w-64 focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="flex items-center border border-gray-300 rounded-lg p-1">
              <button 
                onClick={() => setViewMode('grid')} 
                className={`p-2 rounded ${viewMode === 'grid' ? 'bg-primary-100 text-primary-600' : 'text-gray-600 hover:bg-gray-100'}`}
                title="Grid view"
              >
                <Grid className="h-5 w-5" />
              </button>
              <button 
                onClick={() => setViewMode('list')} 
                className={`p-2 rounded ${viewMode === 'list' ? 'bg-primary-100 text-primary-600' : 'text-gray-600 hover:bg-gray-100'}`}
                title="List view"
              >
                <List className="h-5 w-5" />
              </button>
            </div>
            
            <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <Filter className="h-5 w-5" />
              <span className="hidden sm:inline">Filters</span>
            </button>
          </div>
        </div>
      </div>

      {filteredBooks.length === 0 ? (
        <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-xl">
          <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No books found</h3>
          <p className="text-gray-600 max-w-md mx-auto">
            {searchTerm ? `No results for "${searchTerm}". Try a different search term.` : 'No books available in the collection.'}
          </p>
          {searchTerm && (
            <button 
              onClick={() => setSearchTerm('')}
              className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Clear Search
            </button>
          )}
        </div>
      ) : (
        <>
          <div className={viewMode === 'grid' 
            ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6' 
            : 'space-y-4'
          }>
            {filteredBooks.map((book) => (
              <BookCard key={book.id} book={book} viewMode={viewMode} />
            ))}
          </div>
          
          <div className="pt-4 border-t border-gray-200">
            <p className="text-sm text-gray-500 text-center">
              Showing {filteredBooks.length} of {books.length} books
              {books === MOCK_BOOKS && ' (demo data)'}
            </p>
          </div>
        </>
      )}
    </div>
  )
}

export default Books