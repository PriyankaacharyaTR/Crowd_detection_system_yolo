import React from 'react'

export const EventLog = ({ events = [] }) => {
  const displayEvents = events.slice().reverse().slice(0, 10)

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
      <h3 className="text-lg font-semibold text-white mb-4">📋 Event Log</h3>
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {displayEvents.length === 0 ? (
          <p className="text-gray-500 text-sm">No events logged yet</p>
        ) : (
          displayEvents.map((event, idx) => (
            <div key={idx} className="bg-gray-800 p-3 rounded text-sm border-l-4 border-yellow-500">
              <p className="text-gray-400 text-xs">{new Date(event.timestamp).toLocaleTimeString()}</p>
              <p className="text-white font-medium">{event.type}</p>
              <p className="text-gray-300 text-xs mt-1">
                Count: {event.data.count} | Avg: {event.data.average.toFixed(1)} | Spike: {event.data.spike.toFixed(1)}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
