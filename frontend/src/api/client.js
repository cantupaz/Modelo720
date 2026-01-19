import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      console.error('API Error:', error.response.data)
    } else if (error.request) {
      console.error('Network Error:', error.message)
    }
    return Promise.reject(error)
  }
)

export const declarationsApi = {
  /**
   * Parse a .720 or CSV file
   */
  async parse(file, format = '720') {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('format', format)
    
    const response = await api.post('/api/declarations/parse', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  /**
   * Validate a declaration
   */
  async validate(declaration) {
    const response = await api.post('/api/declarations/validate', declaration)
    return response.data
  },

  /**
   * Convert between formats
   */
  async convert(file, sourceFormat, targetFormat) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('source_format', sourceFormat)
    formData.append('target_format', targetFormat)
    
    const response = await api.post('/api/declarations/convert', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      responseType: 'blob'
    })
    return response.data
  },

  /**
   * Export a declaration to file
   */
  async export(declaration, format = '720') {
    const response = await api.post(`/api/declarations/export?format=${format}`, declaration, {
      responseType: 'blob'
    })
    return response.data
  }
}

export default api
