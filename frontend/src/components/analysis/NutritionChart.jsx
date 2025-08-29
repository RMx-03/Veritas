import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

function NutritionChart({ nutritionFacts }) {
  // Map backend field names to display data
  const macroData = [
    { name: 'Carbs', value: nutritionFacts?.total_carbs || nutritionFacts?.carbohydrates || 0, color: '#3b82f6' },
    { name: 'Protein', value: nutritionFacts?.protein || 0, color: '#10b981' },
    { name: 'Fat', value: nutritionFacts?.total_fat || nutritionFacts?.fat || 0, color: '#f59e0b' }
  ]

  const dailyValueData = [
    { name: 'Calories', value: nutritionFacts?.calories || 0, dailyValue: nutritionFacts?.caloriesDV || 0 },
    { name: 'Sodium', value: nutritionFacts?.sodium || 0, dailyValue: nutritionFacts?.sodiumDV || nutritionFacts?.sodium_dv || 0 },
    { name: 'Sugar', value: nutritionFacts?.total_sugars || nutritionFacts?.sugar || 0, dailyValue: nutritionFacts?.sugarDV || 0 },
    { name: 'Fiber', value: nutritionFacts?.dietary_fiber || nutritionFacts?.fiber || 0, dailyValue: nutritionFacts?.fiberDV || nutritionFacts?.dietary_fiber_dv || 0 }
  ]

  return (
    <div className="space-y-6">
      {/* Macronutrients Pie Chart */}
      <div>
        <h4 className="font-medium text-gray-900 mb-3">Macronutrients</h4>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={macroData}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {macroData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`${value}g`, 'Amount']} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="flex justify-center space-x-4 text-sm">
          {macroData.map((item, index) => (
            <div key={index} className="flex items-center space-x-1">
              <div className={`w-3 h-3 rounded-full`} style={{ backgroundColor: item.color }} />
              <span className="text-gray-600">{item.name}: {item.value}g</span>
            </div>
          ))}
        </div>
      </div>

      {/* Daily Values Bar Chart */}
      <div>
        <h4 className="font-medium text-gray-900 mb-3">Daily Values (%)</h4>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={dailyValueData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => [`${value}%`, 'Daily Value']} />
              <Bar dataKey="dailyValue" fill="#0ea5e9" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Key Nutrition Facts */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-50 p-3 rounded-lg">
          <div className="text-sm text-gray-600">Calories</div>
          <div className="text-xl font-bold text-gray-900">{nutritionFacts?.calories || 0}</div>
        </div>
        <div className="bg-gray-50 p-3 rounded-lg">
          <div className="text-sm text-gray-600">Serving Size</div>
          <div className="text-xl font-bold text-gray-900">{nutritionFacts?.serving_size || nutritionFacts?.servingSize || 'N/A'}</div>
        </div>
      </div>
    </div>
  )
}

export default NutritionChart
