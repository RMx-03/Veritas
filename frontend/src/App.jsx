import { useState } from 'react'
import Header from './components/Header'
import UploadForm from './components/UploadForm'
import ResultsDashboard from './components/ResultsDashboard'
import LoadingScreen from './components/LoadingScreen'

function App() {
  const [analysisResults, setAnalysisResults] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalysisComplete = (results) => {
    setAnalysisResults(results)
    setIsLoading(false)
    setError(null)
  }

  const handleAnalysisStart = () => {
    setIsLoading(true)
    setAnalysisResults(null)
    setError(null)
  }

  const handleAnalysisError = (errorMessage) => {
    setError(errorMessage)
    setIsLoading(false)
    setAnalysisResults(null)
  }

  const handleReset = () => {
    setAnalysisResults(null)
    setIsLoading(false)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {isLoading ? (
          <LoadingScreen />
        ) : analysisResults ? (
          <ResultsDashboard 
            results={analysisResults} 
            onReset={handleReset}
          />
        ) : (
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                Your Pocket Nutrition Scientist
              </h1>
              <p className="text-lg text-gray-600">
                Upload a food label image and get instant AI-powered nutrition analysis, 
                claim verification, and health recommendations.
              </p>
            </div>
            
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-800">{error}</p>
              </div>
            )}
            
            <UploadForm 
              onAnalysisStart={handleAnalysisStart}
              onAnalysisComplete={handleAnalysisComplete}
              onAnalysisError={handleAnalysisError}
            />
          </div>
        )}
      </main>
    </div>
  )
}

export default App
