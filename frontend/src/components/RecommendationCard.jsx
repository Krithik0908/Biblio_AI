import { Brain, Target, Zap } from 'lucide-react'

const RecommendationCard = ({ recommendation }) => {
  const getIcon = (type) => {
    switch (type) {
      case 'ai':
        return <Brain className="h-6 w-6 text-purple-600" />
      case 'trending':
        return <Zap className="h-6 w-6 text-yellow-600" />
      default:
        return <Target className="h-6 w-6 text-blue-600" />
    }
  }

  return (
    <div className="card hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gray-100 rounded-lg">
            {getIcon(recommendation.type)}
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">
              {recommendation.title}
            </h3>
            <p className="text-sm text-gray-500">
              by {recommendation.author}
            </p>
          </div>
        </div>

        <div className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
          {recommendation.confidence}% match
        </div>
      </div>

      <p className="text-gray-600 mb-4">
        {recommendation.reason}
      </p>

      <div className="flex justify-between items-center">
        <div>
          <span className="text-sm text-gray-500">Based on: </span>
          <span className="text-sm font-medium">
            {recommendation.basedOn}
          </span>
        </div>

        <button className="btn-primary text-sm px-4 py-2">
          Borrow Now
        </button>
      </div>
    </div>
  )
}

export default RecommendationCard
