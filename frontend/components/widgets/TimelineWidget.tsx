'use client'

import { WidgetConfiguration } from '@/types/dashboard'

interface TimelineWidgetProps {
  widget: WidgetConfiguration
  isEditing?: boolean
}

export default function TimelineWidget({ widget, isEditing = false }: TimelineWidgetProps) {
  const { title, description, data } = widget
  const events = data?.events || []

  const formatDate = (date: string) => {
    try {
      return new Date(date).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      })
    } catch {
      return date
    }
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm p-4 h-full overflow-auto ${isEditing ? 'ring-2 ring-purple-500' : ''}`}>
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-1">{title}</h3>
      )}
      {description && (
        <p className="text-sm text-gray-600 mb-3">{description}</p>
      )}
      
      <div className="relative">
        {events.map((event: any, index: number) => (
          <div key={index} className="flex pb-8 last:pb-0">
            <div className="flex flex-col items-center mr-4">
              <div 
                className="w-3 h-3 rounded-full flex-shrink-0"
                style={{ backgroundColor: event.color || '#6366f1' }}
              />
              {index < events.length - 1 && (
                <div className="w-0.5 h-full bg-gray-300 mt-1" />
              )}
            </div>
            <div className="flex-1">
              <div className="flex items-center mb-1">
                <h4 className="font-medium text-gray-900">{event.title}</h4>
                <span className="ml-2 text-xs text-gray-500">
                  {formatDate(event.date)}
                </span>
              </div>
              {event.description && (
                <p className="text-sm text-gray-600">{event.description}</p>
              )}
              {event.tags && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {event.tags.map((tag: string, tagIndex: number) => (
                    <span 
                      key={tagIndex}
                      className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {events.length === 0 && (
          <p className="text-gray-500 text-sm">No events to display</p>
        )}
      </div>
    </div>
  )
}