import { useState } from 'react'
import axios from 'axios'
import { KTPData } from '@/types/ktp'
import ImageUpload from '@/components/ImageUpload'
import KTPDisplay from '@/components/KTPDisplay'
import Loading from '@/components/Loading'
import ErrorBoundary from '@/components/ErrorBoundary'

const API_URL = import.meta.env.VITE_API_URL

import './App.css'

function App() {
  const [ktpData, setKtpData] = useState<KTPData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)

  const handleUpload = async (file: File) => {
    try {
      setLoading(true)
      setError(null)

      // Create image preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result as string)
      }
      reader.readAsDataURL(file)

      const formData = new FormData()
      formData.append('file', file)

      // Upload image
      await axios.post(`${API_URL}/upload`, formData)

      // Extract information
      const extractResponse = await axios.post(`${API_URL}/extract`, formData)
      setKtpData(extractResponse.data.ktp_data)
    } catch (err) {
      setImagePreview(null) // Clear preview on error
      if (axios.isAxiosError(err)) {
        const errorMessage = err.response?.data?.error || err.response?.data?.detail?.error || err.message
        setError(errorMessage)
      } else {
        setError('Failed to process KTP image. Please try again.')
      }
      console.error('Error processing KTP:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setKtpData(null)
    setError(null)
    setImagePreview(null)
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
        <div className="relative py-3 sm:max-w-xl sm:mx-auto">
          <div className="relative px-4 py-10 bg-white mx-8 md:mx-0 shadow rounded-3xl sm:p-10">
            <div className="max-w-md mx-auto">
              <div className="divide-y divide-gray-200">
                <div className="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                  <h1 className="text-2xl font-bold text-center mb-8">
                    Indonesian KTP Recognition
                  </h1>
                  
                  {loading ? (
                    <Loading />
                  ) : ktpData ? (
                    <KTPDisplay data={ktpData} onReset={handleReset} />
                  ) : (
                    <div className="space-y-6">
                      <ImageUpload onUpload={handleUpload} />
                      {imagePreview && (
                        <div className="mt-4">
                          <p className="text-sm text-gray-500 mb-2">Image Preview:</p>
                          <img 
                            src={imagePreview} 
                            alt="KTP Preview" 
                            className="max-w-full h-auto rounded-lg shadow-md"
                          />
                        </div>
                      )}
                    </div>
                  )}

                  {error && (
                    <div className="mt-4 bg-red-50 border-l-4 border-red-400 p-4">
                      <div className="flex">
                        <div className="flex-shrink-0">
                          <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <div className="ml-3">
                          <p className="text-sm text-red-700">
                            {error}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  )
}

export default App
