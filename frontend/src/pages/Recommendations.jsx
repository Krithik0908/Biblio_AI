import { Brain, Sparkles, Target, Zap } from 'lucide-react'
import RecommendationCard from '../components/RecommendationCard'

const Recommendations = () => {
  const recommendations = [
    {
      id: 1,
      type: 'ai',
      title: 'The Midnight Library',
      author: 'Matt Haig',
      confidence: 92,
      reason: 'Based on your interest in philosophical fiction and self-discovery themes',
      basedOn: 'Your reading history & ratings'
    },
    {
      id: 2,
      type: 'trending',
      title: 'Project Hail Mary',
      author: 'Andy Weir',
      confidence: 88,
      reason: 'Popular among readers who enjoyed The Martian',
      basedOn: 'Trending in Sci-Fi'
    },
    {
      id: 3,
      type: 'similar',
      title: 'Thinking, Fast and Slow',
      author: 'Daniel Kahneman',
      confidence: 85,
      reason: 'Similar cognitive science themes to books you\'ve rated highly',
      basedOn: 'Content similarity'
    }
  ]

  const aiFeatures = [
    {
      icon: <Brain className="h-6 w-6" />,
      title: 'Deep Learning Analysis',
      description: 'Analyzes your reading patterns, ratings, and preferences'
    },
    {
      icon: <Target className="h-6 w-6" />,
      title: 'Personalized Matching',
      description: 'Matches books to your unique reading profile'
    },
    {
      icon: <Zap className="h-6 w-6" />,
      title: 'Real-time Updates',
      description: 'Recommendations update as you read and rate more books'
    },
    {
      icon: <Sparkles className="h-6 w-6" />,
      title: 'Discovery Engine',
      description: 'Introduces you to new genres and authors you might love'
    }
  ]

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">AI-Powered Recommendations</h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Our AI analyzes your reading patterns to suggest books you'll love
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-2xl font-bold">Your Personalized Recommendations</h2>
          <div className="space-y-4">
            {recommendations.map((rec) => (
              <RecommendationCard key={rec.id} recommendation={rec} />
            ))}
          </div>
        </div>

        <div className="space-y-6">
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">How Our AI Works</h3>
            <div className="space-y-4">
              {aiFeatures.map((feature, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="p-2 bg-primary-50 rounded-lg">
                    <div className="text-primary-600">{feature.icon}</div>
                  </div>
                  <div>
                    <h4 className="font-medium">{feature.title}</h4>
                    <p className="text-sm text-gray-600">{feature.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Improve Recommendations</h3>
            <div className="space-y-3">
              <button className="w-full btn-primary py-2">Rate More Books</button>
              <button className="w-full btn-secondary py-2">Update Preferences</button>
              <button className="w-full btn-secondary py-2">Explore New Genres</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Recommendations