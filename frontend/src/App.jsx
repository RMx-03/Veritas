import { useState } from 'react'
import { Hero, HowItWorks } from './components/ui'
import { UploadForm } from './components/forms'
import { AnalysisLayout } from './components/analysis'

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
    <div className="min-h-screen bg-neutral-50">
      {/* Skip to main content link for screen readers */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      {isLoading ? (
        <div className="min-h-screen flex items-center justify-center bg-white">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-brand-blue-200 border-t-brand-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
            <h2 className="text-xl font-bold text-neutral-900 mb-2">Analyzing Your Product</h2>
            <p className="text-neutral-600">This may take a few moments...</p>
          </div>
        </div>
      ) : analysisResults ? (
        <AnalysisLayout 
          analysisData={analysisResults} 
          imagePreview={analysisResults.processedImage}
          onReset={handleReset} 
        />
      ) : (
        <main id="main-content">
          {/* Hero Section */}
          <Hero onGetStarted={() => {
            const uploadSection = document.getElementById('upload-section');
            uploadSection?.scrollIntoView({ behavior: 'smooth' });
          }} />
          
          {/* Upload Form Section */}
          <section id="upload-section" className="py-20 bg-white" aria-labelledby="upload-heading">
            <div className="container-wide">
              <div className="max-w-2xl mx-auto text-center mb-12">
                <h2 className="text-3xl font-bold text-neutral-900 mb-4">
                  Ready to Analyze Your Product?
                </h2>
                <p className="text-lg text-neutral-600">
                  Upload a clear photo of your nutrition label and get instant AI-powered analysis
                </p>
              </div>
              
              {error && (
                <div className="max-w-2xl mx-auto mb-8">
                  <div className="p-4 bg-red-50 border border-red-200 rounded-2xl">
                    <p className="text-red-800 font-medium">{error}</p>
                  </div>
                </div>
              )}
              
              <div className="max-w-2xl mx-auto">
                <UploadForm 
                  onAnalysisStart={handleAnalysisStart}
                  onAnalysisComplete={handleAnalysisComplete}
                  onAnalysisError={handleAnalysisError}
                />
              </div>
            </div>
          </section>

          {/* How It Works Section */}
          <div id="how-it-works-section">
            <HowItWorks />
          </div>
          
          {/* Footer */}
          <footer className="bg-neutral-900 text-white py-8">
            <div className="container-wide px-4 sm:px-6">
              <div className="flex flex-col items-center text-center space-y-4">
                <img 
                  src="/VeritasLogo.png" 
                  alt="Veritas Logo" 
                  className="h-8 w-auto"
                />
                <p className="text-neutral-400 max-w-md text-sm">
                  AI-powered nutrition analysis MVP for testing and feedback.
                </p>
                <div className="text-xs text-neutral-500">
                  © 2025 Veritas. All rights reserved. Made by Rohit Mishra.
                </div>
              </div>
            </div>
          </footer>
        </main>
      )}
    </div>
  )
}

export default App
