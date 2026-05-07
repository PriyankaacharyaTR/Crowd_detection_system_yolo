import React, { useState, useEffect } from 'react'
import { Sidebar } from './components/Sidebar'
import { VideoPanel } from './components/VideoPanel'
import { StatusBanner } from './components/StatusBanner'
import { MetricCard } from './components/MetricCard'
import { CrowdChart } from './components/CrowdChart'
import { EventLog } from './components/EventLog'
import { ModelsPanel } from './components/ModelsPanel'
import { Toast } from './components/Toast'

const API_BASE_URL = 'http://localhost:5000'

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [data, setData] = useState(null)
  const [frameData, setFrameData] = useState(null)
  const [events, setEvents] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [apiError, setApiError] = useState('')
  const [lastStatus, setLastStatus] = useState(null)
  const [showToast, setShowToast] = useState(false)
  const [toastMessage, setToastMessage] = useState('')
  const [toastType, setToastType] = useState('info')

  // Fetch data from backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/data`)
        if (!response.ok) throw new Error('Failed to fetch data')
        const newData = await response.json()
        
        setData(newData)
        setApiError('')
        
        // Check for status change
        if (lastStatus && lastStatus !== newData.status && newData.status === 'ALERT') {
          showAlertToast('Sudden crowd detected!')
        }
        
        setLastStatus(newData.status)
        setIsLoading(false)
      } catch (error) {
        console.error('Error fetching data:', error)
        setApiError('Backend is not responding on port 5000')
        if (data === null) {
          setIsLoading(false)
        }
      }
    }

    const interval = setInterval(fetchData, 1000)
    fetchData()
    return () => clearInterval(interval)
  }, [lastStatus])

  // Fetch video frame
  useEffect(() => {
    const fetchFrame = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/frame`)
        if (!response.ok) throw new Error('Failed to fetch frame')
        const frameResponse = await response.json()
        setFrameData(frameResponse.frame)
      } catch (error) {
        console.error('Error fetching frame:', error)
      }
    }

    const interval = setInterval(fetchFrame, 500)
    fetchFrame()
    return () => clearInterval(interval)
  }, [])

  // Fetch events
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/events`)
        if (!response.ok) throw new Error('Failed to fetch events')
        const eventsResponse = await response.json()
        setEvents(eventsResponse.events)
      } catch (error) {
        console.error('Error fetching events:', error)
      }
    }

    const interval = setInterval(fetchEvents, 2000)
    fetchEvents()
    return () => clearInterval(interval)
  }, [])

  const showAlertToast = (message) => {
    setToastMessage(message)
    setToastType('alert')
    setShowToast(true)
  }

  const renderDashboard = () => {
    const safeData = data || {
      count: 0,
      average: 0,
      spike: 0,
      status: 'NORMAL',
      history: [],
    }

    return (
      <div className="space-y-6">
        {apiError && (
          <div className="rounded-xl border border-yellow-500/30 bg-yellow-500/10 px-4 py-3 text-sm text-yellow-200">
            {apiError}. The live camera panel still loads, but crowd metrics need the Flask API.
          </div>
        )}

        <StatusBanner status={safeData.status} count={safeData.count} average={safeData.average} />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard 
            title="People Count" 
            value={safeData.count} 
            icon="👥"
            color="blue"
          />
          <MetricCard 
            title="Average" 
            value={safeData.average} 
            icon="📊"
            color="green"
          />
          <MetricCard 
            title="Spike" 
            value={safeData.spike} 
            icon="📈"
            color={safeData.spike > 5 ? 'red' : 'yellow'}
          />
          <MetricCard 
            title="Status" 
            value={safeData.status} 
            icon={safeData.status === 'ALERT' ? '⚠️' : '✓'}
            color={safeData.status === 'ALERT' ? 'red' : 'green'}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <VideoPanel frameData={frameData} isLoading={isLoading} liveData={data} />
          </div>
          <div>
            <EventLog events={events} />
          </div>
        </div>

        <CrowdChart history={safeData.history || []} />
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-gray-950 text-white overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 overflow-y-auto">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-8">
          {activeTab === 'dashboard' && renderDashboard()}
          {activeTab === 'models' && <ModelsPanel />}
          {activeTab === 'settings' && (
            <div className="text-center py-12">
              <p className="text-gray-400 text-lg">Settings coming soon...</p>
            </div>
          )}
        </div>
      </div>

      {/* Toast Notification */}
      {showToast && (
        <div className="fixed bottom-6 right-6 z-50">
          <Toast 
            message={toastMessage} 
            type={toastType}
            onClose={() => setShowToast(false)}
          />
        </div>
      )}
    </div>
  )
}
