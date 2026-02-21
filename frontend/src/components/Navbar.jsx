import { Link, useNavigate } from 'react-router-dom'
import { BookOpen, User, LogOut, Search, Bell } from 'lucide-react'
import { useState } from 'react'
import toast from 'react-hot-toast'

const Navbar = () => {
  const navigate = useNavigate()
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('token'))
  const [searchQuery, setSearchQuery] = useState('')

  const handleLogout = () => {
    localStorage.removeItem('token')
    setIsLoggedIn(false)
    toast.success('Logged out successfully')
    navigate('/')
  }

  const handleSearch = (e) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      navigate(`/books?search=${encodeURIComponent(searchQuery)}`)
    }
  }

  return (
    <nav className="bg-white shadow-lg border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2">
            <BookOpen className="h-8 w-8 text-primary-600" />
            <span className="text-2xl font-bold text-gray-900">Biblio<span className="text-primary-600">AI</span></span>
          </Link>

          <div className="flex-1 max-w-2xl mx-8">
            <form onSubmit={handleSearch} className="relative">
              <input
                type="text"
                placeholder="Search books..."
                className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-full focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
            </form>
          </div>

          <div className="flex items-center space-x-6">
            <Link to="/" className="text-gray-700 hover:text-primary-600 font-medium">Home</Link>
            <Link to="/books" className="text-gray-700 hover:text-primary-600 font-medium">Books</Link>
            <Link to="/recommendations" className="text-gray-700 hover:text-primary-600 font-medium">AI Recs</Link>
            
            {isLoggedIn ? (
              <>
                <Link to="/dashboard" className="text-gray-700 hover:text-primary-600 font-medium">Dashboard</Link>
                <button onClick={handleLogout} className="flex items-center space-x-2 text-red-600 hover:text-red-700">
                  <LogOut className="h-5 w-5" />
                  <span>Logout</span>
                </button>
                <Bell className="h-6 w-6 text-gray-600 cursor-pointer" />
              </>
            ) : (
              <Link to="/login" className="btn-primary">
                <User className="h-5 w-5 inline mr-2" />
                Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar