import { BookOpen, Brain, TrendingUp, Shield } from 'lucide-react'
import { Link } from 'react-router-dom'

const Home = () => {
  const features = [
    {
      icon: <Brain className="h-8 w-8" />,
      title: 'AI Recommendations',
      description: 'Personalized book suggestions based on your reading history'
    },
    {
      icon: <TrendingUp className="h-8 w-8" />,
      title: 'Smart Predictions',
      description: 'Predict return dates and book popularity using ML'
    },
    {
      icon: <Shield className="h-8 w-8" />,
      title: 'Secure Platform',
      description: 'Your data is protected with security measures'
    },
    {
      icon: <BookOpen className="h-8 w-8" />,
      title: 'Vast Collection',
      description: 'Access thousands of books across multiple genres'
    }
  ]

  return (
    <div className="space-y-12">
      <section className="text-center py-12">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Welcome to <span className="text-primary-600">BiblioAI</span>
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
          AI-powered library management system that personalizes your reading experience.
        </p>
        <div className="flex justify-center space-x-4">
          <Link to="/books" className="btn-primary px-8 py-3 text-lg">Browse Books</Link>
          <Link to="/login" className="btn-secondary px-8 py-3 text-lg">Get Started</Link>
        </div>
      </section>

      <section>
        <h2 className="text-3xl font-bold text-center mb-12">Why Choose BiblioAI?</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="card text-center">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <div className="text-primary-600">{feature.icon}</div>
              </div>
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="bg-gradient-to-r from-primary-600 to-indigo-600 rounded-2xl p-8 text-white">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div><div className="text-4xl font-bold mb-2">10K+</div><div className="text-primary-100">Books</div></div>
          <div><div className="text-4xl font-bold mb-2">95%</div><div className="text-primary-100">Accuracy</div></div>
          <div><div className="text-4xl font-bold mb-2">24/7</div><div className="text-primary-100">AI</div></div>
          <div><div className="text-4xl font-bold mb-2">5K+</div><div className="text-primary-100">Readers</div></div>
        </div>
      </section>

      <section className="text-center">
        <h2 className="text-3xl font-bold mb-4">Ready to transform your reading?</h2>
        <Link to="/login" className="btn-primary px-10 py-3 text-lg">Start Free Trial</Link>
      </section>
    </div>
  )
}

export default Home