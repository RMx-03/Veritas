import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Camera, X, ImageIcon, FileImage, Sparkles } from 'lucide-react'
import { analyzeImage } from '../../utils/api'

function UploadForm({ onAnalysisStart, onAnalysisComplete, onAnalysisError }) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [preview, setPreview] = useState(null)

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0]
    if (file) {
      setSelectedFile(file)
      
      // Create preview
      const reader = new FileReader()
      reader.onload = (e) => {
        setPreview(e.target.result)
      }
      reader.readAsDataURL(file)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024 // 10MB
  })

  const handleAnalyze = async () => {
    if (!selectedFile) return

    try {
      onAnalysisStart()
      const results = await analyzeImage(selectedFile)
      onAnalysisComplete(results)
    } catch (error) {
      onAnalysisError(error.message || 'Failed to analyze image')
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    setPreview(null)
  }

  return (
    <div className="card">
      {!selectedFile ? (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 ${
            isDragActive
              ? 'border-brand-blue-500 bg-brand-blue-50 scale-105 shadow-xl'
              : 'border-neutral-300 hover:border-brand-blue-400 hover:bg-neutral-50'
          }`}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center space-y-6">
            <div className={`relative p-6 rounded-2xl transition-all duration-300 ${
              isDragActive 
                ? 'bg-gradient-to-br from-brand-blue-500 to-brand-blue-600 shadow-lg animate-pulse-glow' 
                : 'bg-gradient-to-br from-brand-blue-500 to-brand-blue-600 shadow-soft hover:shadow-medium'
            }`}>
              {isDragActive ? (
                <FileImage className="h-12 w-12 text-white animate-bounce-gentle" />
              ) : (
                <ImageIcon className="h-12 w-12 text-white" />
              )}
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-brand-teal-500 rounded-full flex items-center justify-center">
                <Sparkles className="w-2.5 h-2.5 text-white" />
              </div>
            </div>
            <div>
              <p className="text-xl font-bold text-neutral-900 mb-2">
                {isDragActive ? 'Drop your nutrition label here' : 'Upload Food Label Photo'}
              </p>
              <p className="text-neutral-600 text-sm">
                Drag & drop or click to browse • JPG, PNG supported
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="relative">
            <img
              src={preview}
              alt="Food label preview"
              className="w-full max-w-md mx-auto rounded-xl shadow-xl border border-white/20"
            />
            <button
              onClick={handleReset}
              className="absolute top-3 right-3 bg-white/80 backdrop-blur-sm rounded-full p-2 shadow-lg hover:bg-white transition-all duration-300"
            >
              <X className="h-5 w-5 text-primary-700" />
            </button>
          </div>
          
          <div className="text-center">
            <p className="text-primary-700 mb-6 font-medium">
              Ready to analyze: {selectedFile.name}
            </p>
            <div className="flex justify-center space-x-4">
              <button
                onClick={handleReset}
                className="btn-secondary"
              >
                Choose Different Image
              </button>
              <button
                onClick={handleAnalyze}
                className="btn-primary"
              >
                Analyze Nutrition
              </button>
            </div>
          </div>
        </div>
      )}
      
      <div className="mt-8 p-6 bg-gradient-to-br from-primary-50 to-secondary-50 backdrop-blur-sm rounded-xl border border-white/30">
        <h3 className="font-semibold text-primary-800 mb-4 text-lg">What Veritas analyzes:</h3>
        <ul className="text-primary-700 space-y-2">
          <li className="flex items-center space-x-2">
            <span className="w-2 h-2 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full"></span>
            <span>Nutritional facts and daily values</span>
          </li>
          <li className="flex items-center space-x-2">
            <span className="w-2 h-2 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full"></span>
            <span>Ingredient list and potential allergens</span>
          </li>
          <li className="flex items-center space-x-2">
            <span className="w-2 h-2 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full"></span>
            <span>Health claims verification</span>
          </li>
          <li className="flex items-center space-x-2">
            <span className="w-2 h-2 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full"></span>
            <span>Harmful ingredient warnings</span>
          </li>
          <li className="flex items-center space-x-2">
            <span className="w-2 h-2 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full"></span>
            <span>Overall health recommendation</span>
          </li>
        </ul>
      </div>
    </div>
  )
}

export default UploadForm
