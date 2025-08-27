import { CheckCircle, AlertTriangle, XCircle, TrendingUp } from 'lucide-react'

function HealthRecommendation({ recommendation }) {
  const getRecommendationStyle = (level) => {
    switch (level) {
      case 'safe':
        return {
          bg: 'bg-green-50',
          border: 'border-green-200',
          icon: CheckCircle,
          iconColor: 'text-green-600',
          title: '✅ Safe Choice',
          titleColor: 'text-green-800'
        }
      case 'moderate':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          icon: AlertTriangle,
          iconColor: 'text-yellow-600',
          title: '⚠️ Consume in Moderation',
          titleColor: 'text-yellow-800'
        }
      case 'avoid':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          icon: XCircle,
          iconColor: 'text-red-600',
          title: '❌ Consider Avoiding',
          titleColor: 'text-red-800'
        }
      default:
        return {
          bg: 'bg-gray-50',
          border: 'border-gray-200',
          icon: TrendingUp,
          iconColor: 'text-gray-600',
          title: 'Analysis Complete',
          titleColor: 'text-gray-800'
        }
    }
  }

  const style = getRecommendationStyle(recommendation?.level)
  const Icon = style.icon

  return (
    <div className="card">
      <h3 className="font-semibold text-gray-900 mb-4">Health Recommendation</h3>
      
      <div className={`border rounded-lg p-4 ${style.bg} ${style.border}`}>
        <div className="flex items-start space-x-3">
          <Icon className={`h-6 w-6 ${style.iconColor} mt-1 flex-shrink-0`} />
          <div className="flex-1">
            <h4 className={`font-bold text-lg ${style.titleColor} mb-2`}>
              {style.title}
            </h4>
            <p className="text-gray-700 mb-4">
              {recommendation?.summary || 'Analysis completed successfully.'}
            </p>
            
            {recommendation?.reasons && recommendation.reasons.length > 0 && (
              <div className="space-y-2">
                <h5 className="font-medium text-gray-900">Key Factors:</h5>
                <ul className="space-y-1">
                  {recommendation.reasons.map((reason, index) => (
                    <li key={index} className="text-sm text-gray-700 flex items-start">
                      <span className="text-gray-400 mr-2">•</span>
                      {reason}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>

      {recommendation?.tips && recommendation.tips.length > 0 && (
        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h5 className="font-medium text-blue-900 mb-2">💡 Healthy Tips</h5>
          <ul className="space-y-1">
            {recommendation.tips.map((tip, index) => (
              <li key={index} className="text-sm text-blue-800 flex items-start">
                <span className="text-blue-400 mr-2">•</span>
                {tip}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default HealthRecommendation
