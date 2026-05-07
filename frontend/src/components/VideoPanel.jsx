import React, { useEffect, useRef, useState } from 'react'

const API_BASE_URL = 'http://localhost:5000'

export const VideoPanel = ({ frameData, isLoading, liveData }) => {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)
  const fileInputRef = useRef(null)
  const [mode, setMode] = useState(frameData ? 'backend' : 'live')  // Default to backend if available
  const [cameraError, setCameraError] = useState('')
  const [uploadedPreviewUrl, setUploadedPreviewUrl] = useState('')
  const [uploadedMedia, setUploadedMedia] = useState(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState('')
  const [peopleCount, setPeopleCount] = useState(0)
  const [status, setStatus] = useState('NORMAL')

  // Update metrics from backend
  useEffect(() => {
    if (liveData) {
      setPeopleCount(liveData.count || 0)
      setStatus(liveData.status || 'NORMAL')
    }
  }, [liveData])

  // Live camera setup
  useEffect(() => {
    let cancelled = false

    const stopStream = () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop())
        streamRef.current = null
      }
    }

    const startBackendFeed = async () => {
      try {
        setCameraError('')
        stopStream()

        const response = await fetch(`${API_BASE_URL}/switch-source`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ source: 0 })
        })

        if (!response.ok) {
          throw new Error('Backend could not switch to the laptop camera')
        }

        setMode('backend')
      } catch (error) {
        console.error('Camera error:', error)
        setCameraError(`Camera error: ${error.message}`)
      }
    }

    if (mode === 'live') {
      startBackendFeed()
    } else {
      stopStream()
      if (videoRef.current) {
        videoRef.current.srcObject = null
      }
    }

    return () => {
      cancelled = true
      stopStream()
    }
  }, [mode])

  // Upload video handling
  useEffect(() => {
    if (mode === 'upload' && uploadedMedia && videoRef.current) {
      videoRef.current.srcObject = null
      const url = URL.createObjectURL(uploadedMedia)
      setUploadedPreviewUrl(url)
      videoRef.current.src = url
      videoRef.current.load()
    }
  }, [mode, uploadedMedia])

  const handleFileChange = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    setIsUploading(true)
    setUploadError('')

    try {
      // Create FormData for file upload
      const formData = new FormData()
      formData.append('file', file)

      // Upload to backend
      const response = await fetch(`${API_BASE_URL}/upload-video`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Upload failed')
      }

      const result = await response.json()
      console.log('Video uploaded successfully:', result)

      // Also show local preview
      if (uploadedPreviewUrl) {
        URL.revokeObjectURL(uploadedPreviewUrl)
      }

      setUploadedMedia(file)
      const url = URL.createObjectURL(file)
      setUploadedPreviewUrl(url)
      setMode('upload')
      
    } catch (error) {
      console.error('Upload error:', error)
      setUploadError(error.message || 'Failed to upload video')
    } finally {
      setIsUploading(false)
    }
  }

  const frameUrl = frameData ? `data:image/jpeg;base64,${frameData}` : null

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-lg overflow-hidden shadow-2xl shadow-black/20">
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 p-4 border-b border-gray-700 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          📹 Live Camera Feed
        </h3>

        <div className="flex items-center gap-2 rounded-full bg-gray-950/70 p-1 border border-gray-700 w-fit">
          <button
            onClick={() => setMode('live')}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              mode === 'live' ? 'bg-blue-600 text-white' : 'text-gray-300 hover:text-white'
            }`}
          >
            📹 Live Camera
          </button>
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              mode === 'upload' ? 'bg-blue-600 text-white' : 'text-gray-300 hover:text-white'
            } ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isUploading ? '⏳ Uploading...' : '📤 Upload Video'}
          </button>
          {frameData && (
            <button
              onClick={() => setMode('backend')}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                mode === 'backend' ? 'bg-blue-600 text-white' : 'text-gray-300 hover:text-white'
              }`}
              title="Backend detected feed with bounding boxes"
            >
              🎯 Backend Feed
            </button>
          )}
        </div>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="video/*"
        className="hidden"
        onChange={handleFileChange}
      />

      <div className="aspect-video bg-black relative flex items-center justify-center overflow-hidden">
        {uploadError && (
          <div className="absolute inset-0 flex items-center justify-center text-center px-6 bg-black/70 z-10">
            <div className="max-w-sm rounded-2xl border border-red-500/30 bg-red-500/10 p-6 text-red-100">
              <p className="text-lg font-semibold mb-2">Upload Error</p>
              <p className="text-sm text-red-200/80">{uploadError}</p>
              <button
                onClick={() => setUploadError('')}
                className="mt-3 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-500"
              >
                Dismiss
              </button>
            </div>
          </div>
        )}
        {mode === 'live' && frameData ? (
          <img
            src={frameUrl}
            alt="Backend detected feed"
            className="w-full h-full object-cover"
            key={frameData}
          />
        ) : mode === 'backend' && frameData ? (
          <img
            src={frameUrl}
            alt="Backend detected feed"
            className="w-full h-full object-cover"
            key={frameData}
          />
        ) : mode === 'upload' && uploadedPreviewUrl ? (
          <video
            ref={videoRef}
            controls
            autoPlay
            muted
            playsInline
            src={uploadedPreviewUrl}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="text-gray-500 text-center px-6">
            <p className="text-lg">📹 No video feed available</p>
            <p className="text-sm mt-2">
              {mode === 'live'
                ? 'Waiting for the backend camera feed...'
                : mode === 'backend'
                ? 'Waiting for backend detected feed...'
                : 'Select a video file to upload'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
