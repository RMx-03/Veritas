import { Loader2, Microscope, Eye, Brain, Database } from 'lucide-react'

function LoadingScreen() {
  const steps = [
    { icon: Eye, label: 'Extracting text from image', description: 'Using OCR to read your food label' },
    { icon: Brain, label: 'Structuring nutrition data', description: 'Parsing ingredients and nutrients' },
    { icon: Database, label: 'Verifying with databases', description: 'Cross-checking with USDA & OpenFoodFacts' },
    { icon: Microscope, label: 'Generating analysis', description: 'AI-powered health recommendations' }
  ]

  return (
    <div className="max-w-2xl mx-auto">
      <div className="card text-center">
        <div className="mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
            <Loader2 className="h-8 w-8 text-primary-600 animate-spin" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Analyzing Your Food Label
          </h2>
          <p className="text-gray-600">
            Our AI nutrition scientist is hard at work...
          </p>
        </div>

        <div className="space-y-4">
          {steps.map((step, index) => {
            const Icon = step.icon
            return (
              <div
                key={index}
                className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg"
              >
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                    <Icon className="h-5 w-5 text-primary-600" />
                  </div>
                </div>
                <div className="text-left">
                  <h3 className="font-medium text-gray-900">{step.label}</h3>
                  <p className="text-sm text-gray-600">{step.description}</p>
                </div>
              </div>
            )
          })}
        </div>

        <div className="mt-8 text-sm text-gray-500">
          This usually takes 15-30 seconds
        </div>
      </div>
    </div>
  )
}

export default LoadingScreen
