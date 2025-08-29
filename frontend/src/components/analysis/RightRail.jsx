import React from 'react';
import { Clock, Camera, TrendingUp, Lightbulb, Share2, Download } from 'lucide-react';
import { ClaimBadgeExtended } from './ClaimBadge';

const RightRail = ({ imagePreview, insights, recommendations, analysisData }) => {
  const processingTime = analysisData?.processing_notes?.analysis_time || '2.3';
  const confidence = analysisData?.processing_notes?.ocr_confidence || 'High';
  
  return (
    <div className="space-y-6 sticky top-24">
      {/* Product Image */}
      {imagePreview && (
        <div className="card">
          <h3 className="text-lg font-bold text-neutral-900 mb-4">Analyzed Product</h3>
          <div className="relative group">
            <img 
              src={imagePreview} 
              alt="Product label" 
              className="w-full rounded-2xl shadow-medium transition-transform duration-300 group-hover:scale-105" 
            />
            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all duration-300 rounded-2xl"></div>
            <div className="absolute top-3 right-3">
              <div className="bg-white bg-opacity-90 backdrop-blur-sm px-3 py-1 rounded-full">
                <div className="flex items-center space-x-2">
                  <Camera className="w-3 h-3 text-neutral-600" />
                  <span className="text-xs font-semibold text-neutral-700">
                    OCR: {confidence}
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Analysis Meta */}
          <div className="mt-4 grid grid-cols-2 gap-3">
            <div className="bg-neutral-50 rounded-xl p-3 text-center">
              <Clock className="w-4 h-4 text-brand-blue-500 mx-auto mb-1" />
              <div className="text-xs text-neutral-600">Analysis Time</div>
              <div className="text-sm font-bold text-neutral-900">{processingTime}s</div>
            </div>
            <div className="bg-neutral-50 rounded-xl p-3 text-center">
              <TrendingUp className="w-4 h-4 text-brand-teal-500 mx-auto mb-1" />
              <div className="text-xs text-neutral-600">Confidence</div>
              <div className="text-sm font-bold text-neutral-900">{confidence}</div>
            </div>
          </div>
        </div>
      )}

      {/* Health Assessment */}
      <div className="card">
        <h3 className="text-lg font-bold text-neutral-900 mb-4">Health Assessment</h3>
        <ClaimBadgeExtended 
          level={analysisData?.ai_recommendation?.level || 'moderate'} 
          showDescription={true}
        />
      </div>

      {/* Key Insights */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <Lightbulb className="w-5 h-5 text-brand-purple-500" />
          <h3 className="text-lg font-bold text-neutral-900">Key Insights</h3>
        </div>
        
        <div className="space-y-3">
          {insights.slice(0, 4).map((insight, index) => (
            <div key={index} className="p-3 bg-neutral-50 rounded-xl">
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-brand-blue-100 text-brand-blue-700 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs font-bold">{index + 1}</span>
                </div>
                <p className="text-sm text-neutral-700 leading-relaxed">
                  {typeof insight === 'string' ? insight.slice(0, 120) + (insight.length > 120 ? '...' : '') : 
                   insight?.text?.slice(0, 120) + (insight?.text?.length > 120 ? '...' : '') || 'Analysis insight'}
                </p>
              </div>
            </div>
          ))}
          
          {insights.length === 0 && (
            <div className="text-center py-8">
              <Lightbulb className="w-8 h-8 text-neutral-300 mx-auto mb-2" />
              <p className="text-sm text-neutral-500">No insights available</p>
            </div>
          )}
        </div>
      </div>

      {/* Recommendations */}
      <div className="card">
        <h3 className="text-lg font-bold text-neutral-900 mb-4">Recommendations</h3>
        
        <div className="space-y-3">
          {recommendations.slice(0, 3).map((rec, index) => (
            <div key={index} className="flex space-x-3 p-3 bg-emerald-50 rounded-xl border border-emerald-100">
              <div className="w-6 h-6 bg-emerald-500 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-white text-xs">✓</span>
              </div>
              <p className="text-sm text-emerald-800 leading-relaxed">
                {typeof rec === 'string' ? rec.slice(0, 100) + (rec.length > 100 ? '...' : '') : 
                 rec?.text?.slice(0, 100) + (rec?.text?.length > 100 ? '...' : '') || 'Recommendation available'}
              </p>
            </div>
          ))}
          
          {recommendations.length === 0 && (
            <div className="text-center py-6">
              <div className="w-8 h-8 bg-neutral-200 rounded-lg mx-auto mb-2 flex items-center justify-center">
                <span className="text-neutral-400 text-xs">?</span>
              </div>
              <p className="text-sm text-neutral-500">No recommendations available</p>
            </div>
          )}
        </div>
      </div>

      {/* AI Analysis Details */}
      {analysisData?.ai_recommendation?.aiAnalysis && (
        <div className="card">
          <h3 className="text-lg font-bold text-neutral-900 mb-4">AI Analysis</h3>
          <div className="bg-gradient-to-br from-brand-blue-50 to-brand-teal-50 rounded-2xl p-4 border border-brand-blue-100">
            <details className="group">
              <summary className="cursor-pointer flex items-center justify-between text-sm font-semibold text-brand-blue-900 hover:text-brand-blue-700 transition-colors">
                <span>View Full Analysis</span>
                <span className="group-open:rotate-180 transition-transform">▼</span>
              </summary>
              <div className="mt-4 pt-4 border-t border-brand-blue-200">
                <div className="text-xs text-brand-blue-800 leading-relaxed max-h-64 overflow-y-auto">
                  {analysisData.ai_recommendation.aiAnalysis.slice(0, 500)}
                  {analysisData.ai_recommendation.aiAnalysis.length > 500 && '...'}
                </div>
              </div>
            </details>
          </div>
        </div>
      )}

      {/* Processing Info */}
      <div className="card bg-neutral-50 border-neutral-200">
        <h3 className="text-lg font-bold text-neutral-900 mb-4">Analysis Details</h3>
        
        <div className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-neutral-600">Analysis Version:</span>
            <span className="font-semibold text-neutral-900">
              {analysisData?.processing_notes?.analysis_version || 'v3.0'}
            </span>
          </div>
          
          <div className="flex justify-between">
            <span className="text-neutral-600">Processing Time:</span>
            <span className="font-semibold text-neutral-900">{processingTime} seconds</span>
          </div>
          
          <div className="flex justify-between">
            <span className="text-neutral-600">OCR Engine:</span>
            <span className="font-semibold text-neutral-900">
              {analysisData?.processing_notes?.ocr_engine || 'Advanced'}
            </span>
          </div>
          
          <div className="flex justify-between">
            <span className="text-neutral-600">Generated:</span>
            <span className="font-semibold text-neutral-900">
              {new Date().toLocaleDateString()}
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-6 pt-4 border-t border-neutral-200 space-y-2">
          <button className="w-full btn-secondary btn-sm">
            <Share2 className="w-4 h-4" />
            <span>Share Report</span>
          </button>
          <button className="w-full btn-ghost btn-sm">
            <Download className="w-4 h-4" />
            <span>Download PDF</span>
          </button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="card bg-gradient-to-br from-brand-blue-50 to-brand-teal-50 border-brand-blue-100">
        <h3 className="text-lg font-bold text-neutral-900 mb-4">Quick Stats</h3>
        
        <div className="grid grid-cols-2 gap-3">
          <div className="text-center">
            <div className="text-2xl font-black text-brand-blue-600 mb-1">
              {analysisData?.scientific_analysis?.nova_classification || 4}
            </div>
            <div className="text-xs text-neutral-600">NOVA Group</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-black text-brand-teal-600 mb-1">
              {analysisData?.scientific_analysis?.nutrient_density_score || 0}
            </div>
            <div className="text-xs text-neutral-600">Nutrient Score</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-black text-brand-purple-600 mb-1">
              {(analysisData?.ingredients_analysis?.beneficial || []).length}
            </div>
            <div className="text-xs text-neutral-600">Beneficial</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-black text-red-600 mb-1">
              {(analysisData?.ingredients_analysis?.concerning || []).length}
            </div>
            <div className="text-xs text-neutral-600">Concerns</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RightRail;
