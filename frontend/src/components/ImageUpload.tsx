import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { ArrowUpTrayIcon } from '@heroicons/react/24/outline'

interface Props {
  onUpload: (file: File) => void
}

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

export default function ImageUpload({ onUpload }: Props) {
  const [validationError, setValidationError] = useState<string | null>(null)

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    setValidationError(null)

    if (rejectedFiles.length > 0) {
      const error = rejectedFiles[0].errors[0]
      if (error.code === 'file-too-large') {
        setValidationError('File is too large. Maximum size is 10MB.')
      } else if (error.code === 'file-invalid-type') {
        setValidationError('Invalid file type. Only JPG and PNG images are accepted.')
      } else {
        setValidationError(error.message)
      }
      return
    }

    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0]
      if (file.size > MAX_FILE_SIZE) {
        setValidationError('File is too large. Maximum size is 10MB.')
        return
      }
      onUpload(file)
    }
  }, [onUpload])

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png']
    },
    maxFiles: 1,
    multiple: false,
    maxSize: MAX_FILE_SIZE
  })

  const dropzoneClass = `p-6 border-2 border-dashed rounded-lg text-center cursor-pointer transition-colors ${
    isDragReject ? 'border-red-400 bg-red-50' :
    isDragActive ? 'border-blue-400 bg-blue-50' : 
    'border-gray-300 hover:border-blue-400'
  }`

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        data-testid="dropzone"
        className={dropzoneClass}
      >
        <input {...getInputProps()} />
        <ArrowUpTrayIcon 
          className={`h-12 w-12 mx-auto ${
            isDragReject ? 'text-red-400' :
            isDragActive ? 'text-blue-400' : 
            'text-gray-400'
          }`} 
          aria-hidden="true" 
        />
        <p className="mt-4 text-lg font-medium text-gray-600">
          {isDragReject ? 'Invalid file type...' :
           isDragActive ? 'Drop the KTP image here...' : 
           'Drag and drop a KTP image, or click to select'}
        </p>
        <p className="mt-2 text-sm text-gray-500">
          Supports JPG and PNG formats up to 10MB
        </p>
      </div>

      {validationError && (
        <div className="text-sm text-red-600 text-center">
          {validationError}
        </div>
      )}
    </div>
  )
}