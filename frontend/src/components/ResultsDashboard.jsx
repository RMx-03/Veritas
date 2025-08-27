import { ArrowLeft, CheckCircle, XCircle, AlertTriangle, TrendingUp } from 'lucide-react'
import NutritionChart from './NutritionChart'
import ClaimVerification from './ClaimVerification'
import IngredientAnalysis from './IngredientAnalysis'
import HealthRecommendation from './HealthRecommendation'

function ResultsDashboard({ results, onReset }) {
  const {
    nutritionFacts,
    claimVerification,
    ingredientAnalysis,
    healthRecommendation,
    overallScore,
    processedImage
  } = results

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={onReset}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
          <span>Analyze Another Product</span>
        </button>
        
        <div className="text-right">
          <div className="text-sm text-gray-600">Overall Health Score</div>
          <div className={`text-2xl font-bold ${
            overallScore >= 80 ? 'text-green-600' :
            overallScore >= 60 ? 'text-yellow-600' : 'text-red-600'
          }`}>
            {overallScore}/100
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column - Image and Overall Recommendation */}
        <div className="space-y-6">
          {processedImage && (
            <div className="card">
              <h3 className="font-semibold text-gray-900 mb-4">Analyzed Image</h3>
              <img
                src={processedImage}
                alt="Processed food label"
                className="w-full rounded-lg"
              />
            </div>
          )}
          
          <HealthRecommendation recommendation={healthRecommendation} />
        </div>

        {/* Middle Column - Nutrition Facts */}
        <div className="space-y-6">
          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
              <TrendingUp className="h-5 w-5 mr-2 text-primary-600" />
              Nutrition Analysis
            </h3>
            <NutritionChart nutritionFacts={nutritionFacts} />
          </div>
          
          <ClaimVerification claims={claimVerification} />
        </div>

        {/* Right Column - Ingredients */}
        <div>
          <IngredientAnalysis analysis={ingredientAnalysis} />
        </div>
      </div>

      {/* Bottom Section - Detailed Insights */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-4">Key Insights</h3>
          <div className="space-y-3">
            {results.keyInsights?.map((insight, index) => (
              <div key={index} className="flex items-start space-x-3">
                <div className={`flex-shrink-0 w-2 h-2 rounded-full mt-2 ${
                  insight.type === 'positive' ? 'bg-green-500' :
                  insight.type === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                }`} />
                <p className="text-sm text-gray-700">{insight.text}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-4">Recommendations</h3>
          <div className="space-y-3">
            {results.recommendations?.map((rec, index) => (
              <div key={index} className="flex items-start space-x-3">
                <CheckCircle className="flex-shrink-0 h-4 w-4 text-green-500 mt-0.5" />
                <p className="text-sm text-gray-700">{rec}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ResultsDashboard
