import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes timeout for OCR processing
})

export const analyzeImage = async (imageFile) => {
  try {
    const formData = new FormData()
    formData.append('image', imageFile)

    const response = await api.post('/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data
  } catch (error) {
    console.error('Analysis error:', error)
    
    if (error.response) {
      throw new Error(error.response.data.message || 'Analysis failed')
    } else if (error.request) {
      throw new Error('Network error - please check your connection')
    } else {
      throw new Error('An unexpected error occurred')
    }
  }
}

export const getAnalysisHistory = async () => {
  try {
    const response = await api.get('/history')
    return response.data
  } catch (error) {
    console.error('History fetch error:', error)
    throw new Error('Failed to fetch analysis history')
  }
}

export const saveAnalysis = async (analysisData) => {
  try {
    const response = await api.post('/save', analysisData)
    return response.data
  } catch (error) {
    console.error('Save analysis error:', error)
    throw new Error('Failed to save analysis')
  }
}

export default api
