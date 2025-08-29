import React from 'react';
import { Info } from 'lucide-react';

const NutritionTable = ({ nutritionFacts }) => {
  // Define nutrition data with DV percentages and categories
  const nutritionData = [
    {
      key: 'calories',
      label: 'Calories',
      value: nutritionFacts.calories || 0,
      unit: '',
      dv: null,
      category: 'energy'
    },
    {
      key: 'total_fat',
      label: 'Total Fat',
      value: nutritionFacts.total_fat || 0,
      unit: 'g',
      dv: nutritionFacts.total_fat ? Math.round((nutritionFacts.total_fat / 65) * 100) : 0,
      category: 'macronutrient'
    },
    {
      key: 'saturated_fat',
      label: 'Saturated Fat',
      value: nutritionFacts.saturated_fat || 0,
      unit: 'g',
      dv: nutritionFacts.saturated_fat ? Math.round((nutritionFacts.saturated_fat / 20) * 100) : 0,
      category: 'macronutrient',
      indent: true
    },
    {
      key: 'trans_fat',
      label: 'Trans Fat',
      value: nutritionFacts.trans_fat || 0,
      unit: 'g',
      dv: null,
      category: 'macronutrient',
      indent: true
    },
    {
      key: 'cholesterol',
      label: 'Cholesterol',
      value: nutritionFacts.cholesterol || 0,
      unit: 'mg',
      dv: nutritionFacts.cholesterol ? Math.round((nutritionFacts.cholesterol / 300) * 100) : 0,
      category: 'other'
    },
    {
      key: 'sodium',
      label: 'Sodium',
      value: nutritionFacts.sodium || 0,
      unit: 'mg',
      dv: nutritionFacts.sodium ? Math.round((nutritionFacts.sodium / 2300) * 100) : 0,
      category: 'mineral'
    },
    {
      key: 'total_carbs',
      label: 'Total Carbohydrates',
      value: nutritionFacts.total_carbs || 0,
      unit: 'g',
      dv: nutritionFacts.total_carbs ? Math.round((nutritionFacts.total_carbs / 300) * 100) : 0,
      category: 'macronutrient'
    },
    {
      key: 'dietary_fiber',
      label: 'Dietary Fiber',
      value: nutritionFacts.dietary_fiber || 0,
      unit: 'g',
      dv: nutritionFacts.dietary_fiber ? Math.round((nutritionFacts.dietary_fiber / 25) * 100) : 0,
      category: 'macronutrient',
      indent: true
    },
    {
      key: 'total_sugars',
      label: 'Total Sugars',
      value: nutritionFacts.total_sugars || nutritionFacts.sugars || 0,
      unit: 'g',
      dv: null,
      category: 'macronutrient',
      indent: true
    },
    {
      key: 'added_sugars',
      label: 'Added Sugars',
      value: nutritionFacts.added_sugars || 0,
      unit: 'g',
      dv: nutritionFacts.added_sugars ? Math.round((nutritionFacts.added_sugars / 50) * 100) : 0,
      category: 'macronutrient',
      indent: true
    },
    {
      key: 'protein',
      label: 'Protein',
      value: nutritionFacts.protein || 0,
      unit: 'g',
      dv: nutritionFacts.protein ? Math.round((nutritionFacts.protein / 50) * 100) : 0,
      category: 'macronutrient'
    }
  ];

  // Additional vitamins and minerals
  const vitaminsAndMinerals = [
    {
      key: 'vitamin_d',
      label: 'Vitamin D',
      value: nutritionFacts.vitamin_d || 0,
      unit: 'mcg',
      dv: nutritionFacts.vitamin_d ? Math.round((nutritionFacts.vitamin_d / 20) * 100) : 0
    },
    {
      key: 'calcium',
      label: 'Calcium',
      value: nutritionFacts.calcium || 0,
      unit: 'mg',
      dv: nutritionFacts.calcium ? Math.round((nutritionFacts.calcium / 1300) * 100) : 0
    },
    {
      key: 'iron',
      label: 'Iron',
      value: nutritionFacts.iron || 0,
      unit: 'mg',
      dv: nutritionFacts.iron ? Math.round((nutritionFacts.iron / 18) * 100) : 0
    },
    {
      key: 'potassium',
      label: 'Potassium',
      value: nutritionFacts.potassium || 0,
      unit: 'mg',
      dv: nutritionFacts.potassium ? Math.round((nutritionFacts.potassium / 4700) * 100) : 0
    }
  ];

  const getDVColor = (dv) => {
    if (dv === null || dv === 0) return 'text-neutral-400';
    if (dv < 5) return 'text-nutrition-poor';
    if (dv < 10) return 'text-nutrition-moderate';
    if (dv < 20) return 'text-nutrition-good';
    return 'text-nutrition-excellent';
  };

  const getDVBg = (dv) => {
    if (dv === null || dv === 0) return 'bg-neutral-100';
    if (dv < 5) return 'bg-red-100';
    if (dv < 10) return 'bg-amber-100';
    if (dv < 20) return 'bg-lime-100';
    return 'bg-emerald-100';
  };

  // Filter out zero values for vitamins/minerals
  const significantVitamins = vitaminsAndMinerals.filter(item => item.value > 0);

  return (
    <div className="space-y-6">
      {/* Main Nutrition Facts Table */}
      <div className="bg-white border-2 border-neutral-900 rounded-lg overflow-hidden font-mono">
        {/* Header */}
        <div className="bg-neutral-900 text-white p-4">
          <h3 className="text-lg font-bold">Nutrition Facts</h3>
          <p className="text-sm text-neutral-300">Per serving</p>
        </div>

        {/* Nutrition Data */}
        <div className="divide-y divide-neutral-200">
          {nutritionData.map((item, index) => {
            // Skip if no value
            if (item.value === 0 && item.key !== 'calories') return null;

            return (
              <div 
                key={item.key}
                className={`flex items-center justify-between py-2 sm:py-3 px-3 sm:px-4 hover:bg-neutral-50 transition-colors ${
                  item.indent ? 'pl-8' : ''
                } ${item.key === 'calories' ? 'border-b-2 border-neutral-900' : ''}`}
              >
                <div className="flex items-center space-x-2">
                  <span className={`font-medium text-sm sm:text-base ${
                    item.key === 'calories' ? 'text-lg font-bold' : 'text-sm'
                  } text-neutral-900`}>
                    {item.label}
                  </span>
                  {item.category === 'macronutrient' && (
                    <Info className="w-3 h-3 text-neutral-400" />
                  )}
                </div>

                <div className="flex items-center space-x-4">
                  <span className={`font-bold text-sm sm:text-base ${
                    item.key === 'calories' ? 'text-lg' : 'text-sm'
                  } text-neutral-900`}>
                    {item.value}{item.unit}
                  </span>
                  
                  {item.dv !== null && (
                    <div className="flex items-center space-x-2">
                      <span className={`text-xs sm:text-sm font-semibold ${getDVColor(item.dv)}`}>
                        {item.dv}%
                      </span>
                      <div className="w-6 sm:w-8 h-2 bg-neutral-200 rounded-full overflow-hidden">
                        <div 
                          className={`h-full transition-all duration-300 ${getDVBg(item.dv)}`}
                          style={{ width: `${Math.min(100, item.dv)}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Daily Value Footer */}
        <div className="bg-neutral-50 p-4 border-t-2 border-neutral-900">
          <p className="text-xs text-neutral-600">
            * The % Daily Value (DV) tells you how much a nutrient in a serving of food contributes to a daily diet. 
            2,000 calories a day is used for general nutrition advice.
          </p>
        </div>
      </div>

      {/* Vitamins & Minerals */}
      {significantVitamins.length > 0 && (
        <div className="card">
          <h4 className="text-lg font-bold text-neutral-900 mb-4">Vitamins & Minerals</h4>
          <div className="grid grid-cols-2 gap-4">
            {significantVitamins.map((item) => (
              <div key={item.key} className="flex items-center justify-between p-3 bg-neutral-50 rounded-xl">
                <span className="text-sm font-medium text-neutral-700">{item.label}</span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-bold text-neutral-900">
                    {item.value}{item.unit}
                  </span>
                  {item.dv > 0 && (
                    <span className={`text-xs font-semibold px-2 py-1 rounded-full ${getDVBg(item.dv)} ${getDVColor(item.dv)}`}>
                      {item.dv}%
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Nutrition Quality Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card text-center">
          <div className="text-2xl font-bold text-brand-blue-600 mb-1">
            {nutritionFacts.calories || 0}
          </div>
          <div className="text-sm text-neutral-600">Calories per serving</div>
          <div className="mt-2">
            <span className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold ${
              (nutritionFacts.calories || 0) < 100 ? 'bg-emerald-100 text-emerald-800' :
              (nutritionFacts.calories || 0) < 200 ? 'bg-lime-100 text-lime-800' :
              (nutritionFacts.calories || 0) < 400 ? 'bg-amber-100 text-amber-800' :
              'bg-red-100 text-red-800'
            }`}>
              {(nutritionFacts.calories || 0) < 100 ? 'Low' :
               (nutritionFacts.calories || 0) < 200 ? 'Moderate' :
               (nutritionFacts.calories || 0) < 400 ? 'High' : 'Very High'}
            </span>
          </div>
        </div>

        <div className="card text-center">
          <div className="text-2xl font-bold text-brand-teal-600 mb-1">
            {nutritionFacts.protein || 0}g
          </div>
          <div className="text-sm text-neutral-600">Protein content</div>
          <div className="mt-2">
            <span className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold ${
              (nutritionFacts.protein || 0) < 5 ? 'bg-red-100 text-red-800' :
              (nutritionFacts.protein || 0) < 10 ? 'bg-amber-100 text-amber-800' :
              (nutritionFacts.protein || 0) < 20 ? 'bg-lime-100 text-lime-800' :
              'bg-emerald-100 text-emerald-800'
            }`}>
              {(nutritionFacts.protein || 0) < 5 ? 'Low' :
               (nutritionFacts.protein || 0) < 10 ? 'Moderate' :
               (nutritionFacts.protein || 0) < 20 ? 'Good' : 'Excellent'}
            </span>
          </div>
        </div>

        <div className="card text-center">
          <div className="text-2xl font-bold text-brand-purple-600 mb-1">
            {nutritionFacts.dietary_fiber || 0}g
          </div>
          <div className="text-sm text-neutral-600">Dietary fiber</div>
          <div className="mt-2">
            <span className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold ${
              (nutritionFacts.dietary_fiber || 0) < 2 ? 'bg-red-100 text-red-800' :
              (nutritionFacts.dietary_fiber || 0) < 5 ? 'bg-amber-100 text-amber-800' :
              (nutritionFacts.dietary_fiber || 0) < 10 ? 'bg-lime-100 text-lime-800' :
              'bg-emerald-100 text-emerald-800'
            }`}>
              {(nutritionFacts.dietary_fiber || 0) < 2 ? 'Low' :
               (nutritionFacts.dietary_fiber || 0) < 5 ? 'Moderate' :
               (nutritionFacts.dietary_fiber || 0) < 10 ? 'Good' : 'Excellent'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NutritionTable;
