import { AlertTriangle, Shield, Info, X } from 'lucide-react'

function IngredientAnalysis({ analysis }) {
  const getRiskLevel = (risk) => {
    switch (risk) {
      case 'high':
        return { color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200', icon: X }
      case 'medium':
        return { color: 'text-yellow-600', bg: 'bg-yellow-50', border: 'border-yellow-200', icon: AlertTriangle }
      case 'low':
        return { color: 'text-green-600', bg: 'bg-green-50', border: 'border-green-200', icon: Shield }
      default:
        return { color: 'text-gray-600', bg: 'bg-gray-50', border: 'border-gray-200', icon: Info }
    }
  }

  return (
    <div className="card">
      <h3 className="font-semibold text-gray-900 mb-4">Ingredient Analysis</h3>
      
      {(analysis?.ingredients || analysis?.beneficial || analysis?.concerning) ? (
        <div className="space-y-4">
          {/* Beneficial Ingredients */}
          {analysis.beneficial && analysis.beneficial.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-3">🌿 Beneficial Ingredients</h4>
              <div className="space-y-2">
                {analysis.beneficial.map((ingredient, index) => (
                  <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-3">
                    <div className="flex items-center space-x-2">
                      <Shield className="h-5 w-5 text-green-600" />
                      <span className="font-medium text-green-800">{ingredient}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Concerning Ingredients */}
          {analysis.concerning && analysis.concerning.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-3">⚠️ Ingredients of Concern</h4>
              <div className="space-y-2">
                {analysis.concerning.map((ingredient, index) => (
                  <div key={index} className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <div className="flex items-center space-x-2">
                      <AlertTriangle className="h-5 w-5 text-red-600" />
                      <span className="font-medium text-red-800">{ingredient}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Legacy Flagged Ingredients Support */}
          {analysis.flaggedIngredients && analysis.flaggedIngredients.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-3">⚠️ Ingredients of Concern</h4>
              <div className="space-y-3">
                {analysis.flaggedIngredients.map((ingredient, index) => {
                  const risk = getRiskLevel(ingredient.riskLevel)
                  const Icon = risk.icon
                  
                  return (
                    <div
                      key={index}
                      className={`border rounded-lg p-3 ${risk.bg} ${risk.border}`}
                    >
                      <div className="flex items-start space-x-3">
                        <Icon className={`h-5 w-5 ${risk.color} mt-0.5 flex-shrink-0`} />
                        <div>
                          <div className={`font-medium ${risk.color}`}>
                            {ingredient.name}
                          </div>
                          <div className="text-sm text-gray-700 mt-1">
                            {ingredient.reason}
                          </div>
                          {ingredient.alternatives && (
                            <div className="text-xs text-gray-600 mt-2">
                              <strong>Better alternatives:</strong> {ingredient.alternatives.join(', ')}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* All Ingredients List */}
          {(analysis.ingredients || analysis.additives) && (
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Complete Ingredient List</h4>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex flex-wrap gap-2">
                  {(analysis.ingredients || analysis.additives || []).map((ingredient, index) => {
                    const isConcerning = analysis.concerning?.some(
                      concerning => concerning.toLowerCase().includes(ingredient.toLowerCase()) || ingredient.toLowerCase().includes(concerning.toLowerCase())
                    )
                    const isBeneficial = analysis.beneficial?.some(
                      beneficial => beneficial.toLowerCase().includes(ingredient.toLowerCase()) || ingredient.toLowerCase().includes(beneficial.toLowerCase())
                    )
                    
                    return (
                      <span
                        key={index}
                        className={`inline-block px-2 py-1 rounded text-sm ${
                          isConcerning
                            ? 'bg-red-100 text-red-800 border border-red-200'
                            : isBeneficial
                            ? 'bg-green-100 text-green-800 border border-green-200'
                            : 'bg-white text-gray-700 border border-gray-200'
                        }`}
                      >
                        {ingredient}
                      </span>
                    )
                  })}
                </div>
              </div>
            </div>
          )}

          {/* Allergen Information */}
          {analysis.allergens && analysis.allergens.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-3">🚨 Allergen Warning</h4>
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="h-5 w-5 text-red-600" />
                  <span className="font-medium text-red-800">Contains:</span>
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {analysis.allergens.map((allergen, index) => (
                    <span
                      key={index}
                      className="inline-block px-2 py-1 bg-red-100 text-red-800 rounded text-sm font-medium"
                    >
                      {allergen}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Additives Summary */}
          {analysis.additives && (
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Additives Summary</h4>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">Preservatives</div>
                  <div className="font-bold text-gray-900">{analysis.additives.preservatives || 0}</div>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">Artificial Colors</div>
                  <div className="font-bold text-gray-900">{analysis.additives.artificialColors || 0}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <Info className="h-8 w-8 mx-auto mb-2" />
          <p>No ingredient information available</p>
        </div>
      )}
    </div>
  )
}

export default IngredientAnalysis
