import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, RadialBarChart, RadialBar } from 'recharts';

const ModernDashboard = ({ analysisData, imagePreview, onReset }) => {
  // Extract data with fallbacks
  const scientificAnalysis = analysisData?.scientific_analysis || {};
  const healthScore = analysisData?.health_score || { 
    score: analysisData?.overall_score || analysisData?.overallScore || 50, 
    level: analysisData?.ai_recommendation?.level || 'moderate' 
  };
  const healthImpact = analysisData?.health_impact_assessment || {};
  const ingredientAnalysis = analysisData?.ingredients_analysis || analysisData?.ingredient_analysis || analysisData?.ingredientAnalysis || {};
  const insights = analysisData?.key_insights || analysisData?.keyInsights || [];
  const recommendations = analysisData?.recommendations || [];
  const nutritionFacts = analysisData?.nutrition_facts || analysisData?.nutritionFacts || {};

  // Chart data
  const nutritionChartData = [
    { name: 'Protein', value: nutritionFacts.protein || 0, unit: 'g', color: '#10b981' },
    { name: 'Carbs', value: nutritionFacts.total_carbs || 0, unit: 'g', color: '#3b82f6' },
    { name: 'Fat', value: nutritionFacts.total_fat || 0, unit: 'g', color: '#f59e0b' },
    { name: 'Fiber', value: nutritionFacts.dietary_fiber || 0, unit: 'g', color: '#84cc16' },
    { name: 'Sodium', value: nutritionFacts.sodium || 0, unit: 'mg', color: '#ef4444' }
  ].filter(item => item.value > 0);

  const macroData = [
    { name: 'Protein', value: scientificAnalysis.macronutrient_balance?.protein_percent || 25, fill: '#10b981' },
    { name: 'Carbs', value: scientificAnalysis.macronutrient_balance?.carb_percent || 45, fill: '#3b82f6' },
    { name: 'Fat', value: scientificAnalysis.macronutrient_balance?.fat_percent || 30, fill: '#f59e0b' }
  ].filter(item => item.value > 0);

  return (
    <div className="min-h-screen bg-primary-50">
      {/* Hero Section */}
      <div className="bg-white border-b border-primary-100">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-6">
              <div className="w-16 h-16 bg-accent-500 rounded-3xl flex items-center justify-center">
                <span className="text-white text-2xl font-black">V</span>
              </div>
              <div>
                <h1 className="text-4xl font-black text-primary-900 tracking-tight mb-2">Nutrition Analysis</h1>
                <p className="text-primary-600 font-medium">Complete Scientific Assessment</p>
              </div>
            </div>
            
            {/* Health Score Circle */}
            <div className="text-center">
              <div className="w-24 h-24 rounded-full border-4 border-primary-200 bg-white flex items-center justify-center shadow-soft mb-2">
                <span className="text-3xl font-black text-primary-900">{healthScore.score}</span>
              </div>
              <div className={`px-4 py-1 rounded-full text-xs font-bold uppercase tracking-wider text-white ${
                healthScore.level === 'excellent' ? 'bg-nutrition-excellent' :
                healthScore.level === 'good' ? 'bg-nutrition-good' :
                healthScore.level === 'moderate' ? 'bg-nutrition-moderate' :
                healthScore.level === 'poor' ? 'bg-nutrition-poor' :
                'bg-nutrition-avoid'
              }`}>
                {healthScore.level || 'moderate'}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Key Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-2xl p-6 text-center shadow-soft">
            <div className="text-3xl font-black text-primary-900 mb-1">{scientificAnalysis.nova_classification || 4}</div>
            <div className="text-xs font-bold text-primary-600 uppercase tracking-wider">NOVA Group</div>
          </div>
          <div className="bg-white rounded-2xl p-6 text-center shadow-soft">
            <div className="text-3xl font-black text-primary-900 mb-1">{scientificAnalysis.nutrient_density_score || 0}</div>
            <div className="text-xs font-bold text-primary-600 uppercase tracking-wider">Nutrient Density</div>
          </div>
          <div className="bg-white rounded-2xl p-6 text-center shadow-soft">
            <div className="text-3xl font-black text-primary-900 mb-1">{scientificAnalysis.additive_risk_score || 0}%</div>
            <div className="text-xs font-bold text-primary-600 uppercase tracking-wider">Risk Level</div>
          </div>
          <div className="bg-white rounded-2xl p-6 text-center shadow-soft">
            <div className="text-3xl font-black text-primary-900 mb-1">{scientificAnalysis.ingredient_complexity_index || 0}</div>
            <div className="text-xs font-bold text-primary-600 uppercase tracking-wider">Complexity</div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Charts */}
          <div className="lg:col-span-2 space-y-8">
            {/* Nutrition Charts */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Macro Distribution */}
              <div className="bg-white rounded-3xl p-8 shadow-soft">
                <h2 className="text-xl font-black text-primary-900 mb-6">Macronutrients</h2>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={macroData}
                        dataKey="value"
                        cx="50%"
                        cy="50%"
                        innerRadius={40}
                        outerRadius={70}
                        strokeWidth={0}
                      >
                        {macroData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => `${value}%`} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="grid grid-cols-3 gap-2 mt-4">
                  {macroData.map((macro, index) => (
                    <div key={index} className="text-center">
                      <div className="w-3 h-3 rounded-full mx-auto mb-1" style={{backgroundColor: macro.fill}}></div>
                      <div className="text-xs font-bold text-primary-900">{macro.name}</div>
                      <div className="text-xs text-primary-600">{macro.value}%</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Key Nutrients */}
              <div className="bg-white rounded-3xl p-8 shadow-soft">
                <h2 className="text-xl font-black text-primary-900 mb-6">Key Nutrients</h2>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={nutritionChartData.slice(0, 4)}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="name" tick={{fontSize: 11, fill: '#64748b'}} axisLine={false} />
                      <YAxis tick={{fontSize: 11, fill: '#64748b'}} axisLine={false} />
                      <Tooltip formatter={(value, name, props) => [`${value}${props.payload.unit}`, name]} />
                      <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                        {nutritionChartData.slice(0, 4).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Ingredients Analysis */}
            <div className="bg-white rounded-3xl p-8 shadow-soft">
              <h2 className="text-xl font-black text-primary-900 mb-6">Ingredient Analysis</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-6">
                {/* Beneficial */}
                <div>
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-8 h-8 bg-nutrition-excellent rounded-xl flex items-center justify-center text-white text-sm font-black">
                      {(ingredientAnalysis.beneficial || []).length}
                    </div>
                    <h3 className="text-lg font-black text-primary-900">Beneficial</h3>
                  </div>
                  <div className="space-y-2">
                    {(ingredientAnalysis.beneficial || []).slice(0, 4).map((ingredient, index) => (
                      <div key={index} className="flex items-center space-x-3 p-3 bg-green-50 rounded-xl">
                        <div className="w-2 h-2 bg-nutrition-excellent rounded-full"></div>
                        <span className="text-sm font-medium text-primary-800">
                          {typeof ingredient === 'string' ? ingredient : ingredient.name || 'Unknown'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Concerning */}
                <div>
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-8 h-8 bg-nutrition-avoid rounded-xl flex items-center justify-center text-white text-sm font-black">
                      {(ingredientAnalysis.concerning || []).length}
                    </div>
                    <h3 className="text-lg font-black text-primary-900">Of Concern</h3>
                  </div>
                  <div className="space-y-2">
                    {(ingredientAnalysis.concerning || []).slice(0, 4).map((ingredient, index) => (
                      <div key={index} className="flex items-center space-x-3 p-3 bg-red-50 rounded-xl">
                        <div className="w-2 h-2 bg-nutrition-avoid rounded-full"></div>
                        <span className="text-sm font-medium text-primary-800">
                          {typeof ingredient === 'string' ? ingredient : ingredient.name || 'Unknown'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Risk Bar */}
              <div className="bg-primary-50 rounded-2xl p-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-bold text-primary-900">Risk Assessment</span>
                  <span className="text-sm font-black text-primary-600">{scientificAnalysis.additive_risk_score || 0}%</span>
                </div>
                <div className="w-full bg-primary-200 rounded-full h-2">
                  <div 
                    className="h-2 rounded-full transition-all duration-700"
                    style={{
                      width: `${scientificAnalysis.additive_risk_score || 0}%`,
                      backgroundColor: `hsl(${120 - (scientificAnalysis.additive_risk_score || 0) * 1.2}, 70%, 50%)`
                    }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Insights & Recommendations */}
          <div className="space-y-8">
            {/* Health Impact */}
            <div className="bg-white rounded-3xl p-8 shadow-soft">
              <h2 className="text-xl font-black text-primary-900 mb-6">Health Impact</h2>
              <div className="space-y-4">
                {Object.entries(healthImpact).slice(0, 4).map(([system, impact]) => (
                  <div key={system} className="p-4 bg-primary-50 rounded-2xl">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="text-xl">
                        {{
                          cardiovascular: '❤️',
                          metabolic: '⚡',
                          digestive: '🦠',
                          inflammatory: '🔥'
                        }[system] || '🔬'}
                      </span>
                      <h3 className="font-black text-primary-900 capitalize text-sm">{system}</h3>
                    </div>
                    <p className={`text-xs font-medium leading-relaxed ${
                      impact.includes('LOW RISK') || impact.includes('FAVORABLE') ? 'text-nutrition-good' : 
                      impact.includes('HIGH RISK') || impact.includes('CONCERNING') ? 'text-nutrition-avoid' : 
                      'text-primary-700'
                    }`}>
                      {impact.slice(0, 120)}...
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Key Insights */}
            <div className="bg-white rounded-3xl p-8 shadow-soft">
              <h2 className="text-xl font-black text-primary-900 mb-6">Key Insights</h2>
              <div className="space-y-3">
                {insights.slice(0, 5).map((insight, index) => (
                  <div key={index} className="flex space-x-3 p-3 bg-primary-50 rounded-xl">
                    <div className="w-6 h-6 bg-accent-500 rounded-lg flex items-center justify-center flex-shrink-0">
                      <span className="text-white text-xs font-black">{index + 1}</span>
                    </div>
                    <p className="text-sm text-primary-800 font-medium leading-relaxed">
                      {typeof insight === 'string' ? insight.slice(0, 100) + '...' : insight?.text?.slice(0, 100) + '...' || 'Analysis insight'}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-white rounded-3xl p-8 shadow-soft">
              <h2 className="text-xl font-black text-primary-900 mb-6">Recommendations</h2>
              <div className="space-y-3">
                {recommendations.slice(0, 4).map((rec, index) => (
                  <div key={index} className="flex space-x-3 p-3 bg-accent-50 rounded-xl">
                    <div className="w-6 h-6 bg-nutrition-good rounded-lg flex items-center justify-center flex-shrink-0">
                      <span className="text-white text-xs">✓</span>
                    </div>
                    <p className="text-sm text-primary-800 font-medium leading-relaxed">
                      {typeof rec === 'string' ? rec.slice(0, 120) + '...' : rec?.text?.slice(0, 120) + '...' || 'Recommendation available'}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Image Preview */}
            {imagePreview && (
              <div className="bg-white rounded-3xl p-8 shadow-soft">
                <h2 className="text-xl font-black text-primary-900 mb-6">Product Label</h2>
                <div className="relative">
                  <img src={imagePreview} alt="Product label" className="w-full rounded-2xl shadow-medium" />
                  <div className="absolute top-3 left-3">
                    <span className="bg-white bg-opacity-90 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-bold text-primary-900">
                      OCR: {analysisData?.processing_notes?.ocr_confidence || 'Medium'}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between mt-12 pt-8 border-t border-primary-100">
          <div className="text-sm text-primary-600">
            <span className="font-medium">Analysis v{analysisData?.processing_notes?.analysis_version || '3.0'}</span>
            <span className="mx-2">•</span>
            <span>Generated {new Date().toLocaleDateString()}</span>
          </div>
          <button 
            onClick={onReset}
            className="flex items-center space-x-2 px-6 py-3 bg-accent-500 text-white rounded-2xl font-bold hover:bg-accent-600 transition-colors shadow-soft"
          >
            <span>🔄</span>
            <span>New Analysis</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ModernDashboard;
