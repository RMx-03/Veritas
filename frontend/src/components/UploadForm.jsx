import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Camera, X } from 'lucide-react'
import { analyzeImage } from '../utils/api'

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
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-primary-400 bg-primary-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center space-y-4">
            <div className="bg-gray-100 p-4 rounded-full">
              {isDragActive ? (
                <Camera className="h-8 w-8 text-primary-600" />
              ) : (
                <Upload className="h-8 w-8 text-gray-400" />
              )}
            </div>
            <div>
              <p className="text-lg font-medium text-gray-900">
                {isDragActive ? 'Drop your image here' : 'Upload food label image'}
              </p>
              <p className="text-gray-600 mt-1">
                Drag & drop or click to select • PNG, JPG, WEBP up to 10MB
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
              className="w-full max-w-md mx-auto rounded-lg shadow-sm"
            />
            <button
              onClick={handleReset}
              className="absolute top-2 right-2 bg-white rounded-full p-1 shadow-sm hover:shadow-md transition-shadow"
            >
              <X className="h-4 w-4 text-gray-600" />
            </button>
          </div>
          
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-4">
              Ready to analyze: {selectedFile.name}
            </p>
            <div className="flex justify-center space-x-3">
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
      
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-medium text-blue-900 mb-2">What Veritas analyzes:</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Nutritional facts and daily values</li>
          <li>• Ingredient list and potential allergens</li>
          <li>• Health claims verification</li>
          <li>• Harmful ingredient warnings</li>
          <li>• Overall health recommendation</li>
        </ul>
      </div>
    </div>
  )
}

export default UploadForm
