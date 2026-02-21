import { Star, Users, Clock, BookOpen } from 'lucide-react'

const BookCard = ({ book }) => {
  return (
    <div className="card hover:shadow-lg transition-shadow cursor-pointer">
      <div className="flex space-x-4">
        {/* Show book cover if available, otherwise show placeholder */}
        {book.cover_url ? (
          <div className="w-24 h-32 rounded-lg overflow-hidden flex-shrink-0">
            <img 
              src={book.cover_url} 
              alt={book.title}
              className="w-full h-full object-cover"
              onError={(e) => {
                // If image fails to load, show placeholder
                e.target.style.display = 'none'
                e.target.parentElement.innerHTML = `
                  <div class="w-24 h-32 bg-gradient-to-br from-primary-100 to-primary-200 rounded-lg flex items-center justify-center">
                    <svg class="h-12 w-12 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                  </div>
                `
              }}
            />
          </div>
        ) : (
          <div className="w-24 h-32 bg-gradient-to-br from-primary-100 to-primary-200 rounded-lg flex items-center justify-center flex-shrink-0">
            <BookOpen className="h-12 w-12 text-primary-600" />
          </div>
        )}
        
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">{book.title || 'Untitled Book'}</h3>
          <p className="text-gray-600 mb-2">by {book.author || 'Unknown Author'}</p>
          
          <div className="flex items-center space-x-2 mb-3">
            <div className="flex items-center">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`h-4 w-4 ${i < Math.floor(book.rating || 4) ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`}
                />
              ))}
            </div>
            <span className="text-sm text-gray-500">{(book.rating || 4.0).toFixed(1)}</span>
            {book.genre && (
              <span className="ml-2 px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                {book.genre}
              </span>
            )}
          </div>
          
          {book.description && (
            <p className="text-sm text-gray-600 mb-3 line-clamp-2">{book.description}</p>
          )}
          
          <div className="flex items-center space-x-4 text-sm text-gray-500">
            <div className="flex items-center space-x-1">
              <Users className="h-4 w-4" />
              <span>{book.views?.toLocaleString() || '0'} reads</span>
            </div>
            <div className="flex items-center space-x-1">
              <Clock className="h-4 w-4" />
              <span>{book.available_copies || 0} available</span>
            </div>
          </div>
          
          <div className="mt-4 flex space-x-2">
            <button className="btn-primary text-sm px-3 py-1">Borrow Now</button>
            <button className="btn-secondary text-sm px-3 py-1">Add to Wishlist</button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default BookCard