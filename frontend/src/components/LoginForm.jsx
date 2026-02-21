import { useState } from 'react'
import { Mail, Lock, UserPlus } from 'lucide-react'
import { authAPI } from '../services/api'
import toast from 'react-hot-toast'
import { useNavigate } from 'react-router-dom'

const LoginForm = () => {
  const navigate = useNavigate()
  const [isLogin, setIsLogin] = useState(true)
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    phone: ''
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    
    try {
      let response
      
      if (isLogin) {
        // Login flow
        response = await authAPI.login(formData.email, formData.password)
      } else {
        // Register flow
        response = await authAPI.register(formData)
      }
      
      // Save token
      localStorage.setItem('token', response.data.access_token)
      
      // Show success message
      toast.success(isLogin ? 'Login successful!' : 'Registration successful!')
      
      // Redirect to dashboard
      navigate('/dashboard')
      
    } catch (error) {
      // SAFE error handling - never render objects
      let errorMessage = 'An error occurred'
      
      if (error.response?.data) {
        // Handle FastAPI validation errors
        if (Array.isArray(error.response.data.detail)) {
          // Multiple validation errors
          errorMessage = error.response.data.detail
            .map(err => `${err.loc[1]}: ${err.msg}`)
            .join(', ')
        } else if (error.response.data.detail) {
          // Single error message
          errorMessage = error.response.data.detail
        } else if (error.response.data.message) {
          errorMessage = error.response.data.message
        }
      } else if (error.message) {
        errorMessage = error.message
      }
      
      toast.error(errorMessage)
      
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto card">
      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        {isLogin ? 'Welcome Back' : 'Create Account'}
      </h2>
      <p className="text-gray-600 mb-6">
        {isLogin ? 'Sign in to continue to your dashboard' : 'Fill in your details to get started'}
      </p>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {!isLogin && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Full Name *
            </label>
            <input
              type="text"
              className="input-field"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              placeholder="Enter your full name"
              required={!isLogin}
              disabled={isLoading}
            />
          </div>
        )}
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email *
          </label>
          <div className="relative">
            <Mail className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
            <input
              type="email"
              className="input-field pl-10"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              placeholder="you@example.com"
              required
              disabled={isLoading}
            />
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Password *
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
            <input
              type="password"
              className="input-field pl-10"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              placeholder="••••••••"
              required
              minLength="6"
              disabled={isLoading}
            />
          </div>
          {!isLogin && (
            <p className="mt-1 text-xs text-gray-500">
              Password must be at least 6 characters
            </p>
          )}
        </div>
        
        {!isLogin && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Phone Number (Optional)
            </label>
            <input
              type="tel"
              className="input-field"
              value={formData.phone}
              onChange={(e) => setFormData({...formData, phone: e.target.value})}
              placeholder="+1 (555) 123-4567"
              disabled={isLoading}
            />
          </div>
        )}
        
        <button 
          type="submit" 
          className="w-full btn-primary py-3 flex items-center justify-center"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </>
          ) : (
            isLogin ? 'Sign In' : 'Create Account'
          )}
        </button>
      </form>
      
      <div className="mt-6 pt-6 border-t border-gray-200 text-center">
        <button
          onClick={() => {
            if (!isLoading) {
              setIsLogin(!isLogin)
              setFormData({
                email: '',
                password: '',
                name: '',
                phone: ''
              })
            }
          }}
          className="text-primary-600 hover:text-primary-700 font-medium flex items-center justify-center space-x-2 mx-auto disabled:opacity-50"
          disabled={isLoading}
        >
          <UserPlus className="h-5 w-5" />
          <span>
            {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
          </span>
        </button>
      </div>
    </div>
  )
}

export default LoginForm