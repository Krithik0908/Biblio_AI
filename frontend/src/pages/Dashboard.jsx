import { BookOpen, Clock, TrendingUp, Award } from 'lucide-react'
import BookCard from '../components/BookCard'

const Dashboard = () => {
  const userStats = {
    streak: 14,
    totalBooks: 42,
    readingTime: '68h 24m',
    level: 'Bookworm'
  }

  return (
    <div className="space-y-8">
      <div className="bg-gradient-to-r from-primary-600 to-indigo-600 rounded-2xl p-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Welcome back, Reader!</h1>
        <p className="text-primary-100">Your AI-powered reading journey continues</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Reading Streak</p>
              <p className="text-2xl font-bold">{userStats.streak} days</p>
            </div>
            <TrendingUp className="h-8 w-8 text-green-500" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Books Read</p>
              <p className="text-2xl font-bold">{userStats.totalBooks}</p>
            </div>
            <BookOpen className="h-8 w-8 text-blue-500" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Reading Time</p>
              <p className="text-2xl font-bold">{userStats.readingTime}</p>
            </div>
            <Clock className="h-8 w-8 text-purple-500" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Reader Level</p>
              <p className="text-2xl font-bold">{userStats.level}</p>
            </div>
            <Award className="h-8 w-8 text-yellow-500" />
          </div>
        </div>
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">Recommended For You</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <BookCard book={{ title: 'Deep Work', author: 'Cal Newport', rating: 4.7 }} />
          <BookCard book={{ title: 'The Psychology of Money', author: 'Morgan Housel', rating: 4.8 }} />
        </div>
      </div>
    </div>
  )
}

export default Dashboard