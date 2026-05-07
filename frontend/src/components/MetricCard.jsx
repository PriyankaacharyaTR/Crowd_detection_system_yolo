import React from 'react'

export const MetricCard = ({ title, value, unit = '', color = 'blue', icon = '📊' }) => {
  const colorClasses = {
    blue: 'border-blue-500 bg-blue-500/10',
    green: 'border-green-500 bg-green-500/10',
    red: 'border-red-500 bg-red-500/10',
    yellow: 'border-yellow-500 bg-yellow-500/10',
  }

  return (
    <div className={`border ${colorClasses[color]} rounded-lg p-6 backdrop-blur-sm hover:shadow-lg transition-shadow`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-gray-400 text-sm font-medium mb-2">{title}</p>
          <p className="text-3xl font-bold text-white">
            {typeof value === 'number' ? value.toFixed(1) : value}
            {unit && <span className="text-lg ml-1 text-gray-400">{unit}</span>}
          </p>
        </div>
        <span className="text-3xl">{icon}</span>
      </div>
    </div>
  )
}
