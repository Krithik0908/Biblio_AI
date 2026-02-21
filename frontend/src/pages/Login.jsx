import LoginForm from '../components/LoginForm'

const Login = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Welcome to <span className="text-primary-600">BiblioAI</span>
          </h1>
          <p className="text-lg text-gray-600 mb-8">
            Sign in to access personalized book recommendations, track your reading progress, and manage your library.
          </p>
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 font-bold">✓</span>
              </div>
              <span>AI-powered book recommendations</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 font-bold">✓</span>
              </div>
              <span>Personalized reading dashboard</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 font-bold">✓</span>
              </div>
              <span>Smart return predictions</span>
            </div>
          </div>
        </div>
        
        <div>
          <LoginForm />
        </div>
      </div>
    </div>
  )
}

export default Login