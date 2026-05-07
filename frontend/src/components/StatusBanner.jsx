import React from 'react'

export const StatusBanner = ({ status, count, average }) => {
  const isAlert = status === 'ALERT'
  const bgColor = isAlert ? 'bg-red-600/20 border-red-500' : 'bg-green-600/20 border-green-500'
  const textColor = isAlert ? 'text-red-400' : 'text-green-400'
  const pulse = isAlert ? 'animate-pulse' : ''

  return (
    <div className={`border ${bgColor} rounded-lg p-6 mb-6 ${pulse}`}>
      <div className="flex items-center justify-between">
        <div>
          <h2 className={`text-4xl font-bold ${textColor} mb-2`}>
            {isAlert ? '🚨 SUDDEN CROWD DETECTED' : '✓ NORMAL CONDITIONS'}
          </h2>
          <p className="text-gray-300">
            Current Count: <span className="font-bold text-white">{count}</span> | 
            Average: <span className="font-bold text-white">{average.toFixed(1)}</span>
          </p>
        </div>
        <div className={`text-6xl ${pulse}`}>
          {isAlert ? '⚠️' : '✓'}
        </div>
      </div>
    </div>
  )
}
