import React from 'react';
import { ArrowLeft, Download, Share2, Bookmark } from 'lucide-react';
import NutritionTable from './NutritionTable';
import ClaimBadge from './ClaimBadge';
import RightRail from './RightRail';
import ClaimsAnalysis from './ClaimsAnalysis';

const AnalysisLayout = ({ analysisData, imagePreview, onReset }) => {
  // Extract data with fallbacks
  const scientificAnalysis = analysisData?.scientific_analysis || {};
  const healthScore = analysisData?.health_score || { 
    score: analysisData?.overall_score || analysisData?.overallScore || 50, 
    level: analysisData?.ai_recommendation?.level || 'moderate' 
  };
  const nutritionFacts = analysisData?.nutrition_facts || analysisData?.nutritionFacts || {};
  const ingredientAnalysis = analysisData?.ingredients_analysis || analysisData?.ingredient_analysis || {};
  const healthImpact = analysisData?.health_impact_assessment || {};
  const insights = analysisData?.key_insights || analysisData?.keyInsights || [];
  const recommendations = analysisData?.recommendations || [];

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-nutrition-excellent';
    if (score >= 60) return 'text-nutrition-good';
    if (score >= 40) return 'text-nutrition-moderate';
    if (score >= 20) return 'text-nutrition-poor';
    return 'text-nutrition-critical';
  };

  const getScoreBg = (score) => {
    if (score >= 80) return 'bg-emerald-500';
    if (score >= 60) return 'bg-lime-500';
    if (score >= 40) return 'bg-amber-500';
    if (score >= 20) return 'bg-orange-500';
    return 'bg-red-500';
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <header className="bg-white border-b border-neutral-200 sticky top-0 z-50">
        <div className="container-wide py-3 sm:py-4 px-4 sm:px-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center space-x-2 sm:space-x-4">
              <button 
                onClick={onReset}
                className="btn-ghost btn-sm"
                aria-label="Go back to upload new label"
                type="button"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back</span>
              </button>
              <div className="h-6 w-px bg-neutral-200"></div>
              <div>
                <h1 className="text-base sm:text-lg font-bold text-neutral-900">Nutrition Analysis Report</h1>
                <p className="text-xs sm:text-sm text-neutral-600 hidden sm:block">
                  Generated {new Date().toLocaleDateString()} at {new Date().toLocaleTimeString()}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2 sm:space-x-3">
              <button className="btn-ghost btn-sm">
                <Bookmark className="w-4 h-4" />
                <span>Save</span>
              </button>
              <button className="btn-ghost btn-sm">
                <Share2 className="w-4 h-4" />
                <span>Share</span>
              </button>
              <button className="btn-secondary btn-sm" aria-label="Download analysis as PDF" type="button">
                <Download className="w-4 h-4" />
                <span>Export PDF</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="container-wide py-4 sm:py-6 lg:py-8 px-4 sm:px-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-4 sm:space-y-6 lg:space-y-8">
            {/* Health Score Overview */}
            <div className="card">
              <div className="flex flex-col sm:flex-row items-start justify-between gap-4 mb-4 sm:mb-6">
                <div>
                  <h2 className="text-xl sm:text-2xl font-bold text-neutral-900 mb-2">Overall Health Assessment</h2>
                  <p className="text-sm sm:text-base text-neutral-600">Comprehensive analysis based on nutritional content and ingredient quality</p>
                </div>
                
                {/* Score Circle */}
                <div className="relative mx-auto sm:mx-0">
                  <div className="w-24 h-24 rounded-full border-8 border-neutral-200 flex items-center justify-center bg-white relative overflow-hidden">
                    <div 
                      className={`absolute inset-0 rounded-full ${getScoreBg(healthScore.score)}`}
                      style={{
                        background: `conic-gradient(${
                          healthScore.score >= 80 ? '#059669' :
                          healthScore.score >= 60 ? '#65a30d' :
                          healthScore.score >= 40 ? '#d97706' :
                          healthScore.score >= 20 ? '#ea580c' : '#dc2626'
                        } ${healthScore.score * 3.6}deg, #e5e5e5 ${healthScore.score * 3.6}deg)`
                      }}
                    ></div>
                    <div className="relative bg-white w-16 h-16 rounded-full flex items-center justify-center">
                      <span className={`text-2xl font-black ${getScoreColor(healthScore.score)}`}>
                        {healthScore.score}
                      </span>
                    </div>
                  </div>
                  <ClaimBadge 
                    level={healthScore.level} 
                    className="absolute -bottom-3 left-1/2 transform -translate-x-1/2"
                  />
                </div>
              </div>

              {/* Key Metrics Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
                <div className="text-center p-4 bg-neutral-50 rounded-2xl">
                  <div className="text-2xl font-bold text-neutral-900 mb-1">
                    {scientificAnalysis.nova_classification || 4}
                  </div>
                  <div className="text-xs sm:text-sm text-neutral-600">NOVA Group</div>
                </div>
                <div className="text-center p-4 bg-neutral-50 rounded-2xl">
                  <div className="text-2xl font-bold text-neutral-900 mb-1">
                    {scientificAnalysis.nutrient_density_score || 0}
                  </div>
                  <div className="text-sm text-neutral-600">Nutrient Density</div>
                </div>
                <div className="text-center p-4 bg-neutral-50 rounded-2xl">
                  <div className="text-2xl font-bold text-neutral-900 mb-1">
                    {scientificAnalysis.additive_risk_score || 0}%
                  </div>
                  <div className="text-sm text-neutral-600">Risk Score</div>
                </div>
                <div className="text-center p-4 bg-neutral-50 rounded-2xl">
                  <div className="text-2xl font-bold text-neutral-900 mb-1">
                    {scientificAnalysis.ingredient_complexity_index || 0}
                  </div>
                  <div className="text-sm text-neutral-600">Complexity</div>
                </div>
              </div>
            </div>

            {/* Nutrition Facts */}
            <div className="card">
              <h2 className="text-2xl font-bold text-neutral-900 mb-6">Nutrition Facts</h2>
              <NutritionTable nutritionFacts={nutritionFacts} />
            </div>

            {/* Ingredients Analysis */}
            <div className="card">
              <h2 className="text-2xl font-bold text-neutral-900 mb-6">Ingredient Analysis</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                {/* Beneficial Ingredients */}
                <div>
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-8 h-8 bg-emerald-100 text-emerald-700 rounded-xl flex items-center justify-center text-sm font-bold">
                      {(ingredientAnalysis.beneficial || []).length}
                    </div>
                    <h3 className="text-lg font-bold text-neutral-900">Beneficial Compounds</h3>
                  </div>
                  <div className="space-y-2">
                    {(ingredientAnalysis.beneficial || []).slice(0, 5).map((ingredient, index) => (
                      <div key={index} className="flex items-center space-x-3 p-3 bg-emerald-50 rounded-xl border border-emerald-100">
                        <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                        <span className="text-sm font-medium text-neutral-800">
                          {typeof ingredient === 'string' ? ingredient : ingredient.name || 'Unknown'}
                        </span>
                      </div>
                    ))}
                    {(!ingredientAnalysis.beneficial || ingredientAnalysis.beneficial.length === 0) && (
                      <p className="text-sm text-neutral-500 italic p-3">No beneficial ingredients identified</p>
                    )}
                  </div>
                </div>

                {/* Concerning Ingredients */}
                <div>
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-8 h-8 bg-red-100 text-red-700 rounded-xl flex items-center justify-center text-sm font-bold">
                      {(ingredientAnalysis.concerning || []).length}
                    </div>
                    <h3 className="text-lg font-bold text-neutral-900">Ingredients of Concern</h3>
                  </div>
                  <div className="space-y-2">
                    {(ingredientAnalysis.concerning || []).slice(0, 5).map((ingredient, index) => (
                      <div key={index} className="flex items-center space-x-3 p-3 bg-red-50 rounded-xl border border-red-100">
                        <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                        <span className="text-sm font-medium text-neutral-800">
                          {typeof ingredient === 'string' ? ingredient : ingredient.name || 'Unknown'}
                        </span>
                      </div>
                    ))}
                    {(!ingredientAnalysis.concerning || ingredientAnalysis.concerning.length === 0) && (
                      <p className="text-sm text-neutral-500 italic p-3">No concerning ingredients detected</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Risk Assessment Bar */}
              <div className="bg-neutral-50 rounded-2xl p-6">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="text-lg font-bold text-neutral-900">Overall Risk Assessment</h4>
                  <span className="text-sm font-semibold text-neutral-600">
                    {scientificAnalysis.additive_risk_score || 0}% Risk Score
                  </span>
                </div>
                <div className="w-full bg-neutral-200 rounded-full h-4">
                  <div 
                    className={`h-full transition-all duration-700 ${getScoreBg(scientificAnalysis.additive_risk_score || 0)}`}
                    style={{ width: `${Math.min(100, scientificAnalysis.additive_risk_score || 0)}%` }}
                    role="progressbar"
                    aria-valuenow={scientificAnalysis.additive_risk_score || 0}
                    aria-valuemin="0"
                    aria-valuemax="100"
                    aria-label={`${scientificAnalysis.additive_risk_score || 0}% of daily value for risk score`}
                  ></div>
                </div>
                <p className="text-sm text-neutral-600 mt-2">
                  {(scientificAnalysis.additive_risk_score || 0) < 30 ? 'Low risk - Generally safe for consumption' :
                   (scientificAnalysis.additive_risk_score || 0) < 60 ? 'Moderate risk - Consider limiting intake' :
                   'High risk - Consider alternatives'}
                </p>
              </div>
            </div>

            {/* Claims Verification */}
            <ClaimsAnalysis claims={analysisData?.claim_verification || []} />

            {/* Health Impact */}
            <div className="card">
              <h2 className="text-2xl font-bold text-neutral-900 mb-6">Health Impact Assessment</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(healthImpact).map(([system, impact]) => (
                  <div key={system} className="p-4 bg-neutral-50 rounded-2xl">
                    <div className="flex items-center space-x-3 mb-3">
                      <span className="text-2xl">
                        {{
                          cardiovascular: '❤️',
                          metabolic: '⚡',
                          digestive: '🦠',
                          inflammatory: '🔥'
                        }[system] || '🔬'}
                      </span>
                      <h3 className="font-bold text-neutral-900 capitalize">{system} System</h3>
                    </div>
                    <p className={`text-sm font-medium ${
                      impact.includes('LOW RISK') || impact.includes('FAVORABLE') ? 'text-emerald-700' : 
                      impact.includes('HIGH RISK') || impact.includes('CONCERNING') ? 'text-red-700' : 
                      'text-neutral-700'
                    }`}>
                      {impact}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Rail */}
          <div className="lg:col-span-1">
            <RightRail 
              imagePreview={imagePreview}
              insights={insights}
              recommendations={recommendations}
              analysisData={analysisData}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisLayout;
