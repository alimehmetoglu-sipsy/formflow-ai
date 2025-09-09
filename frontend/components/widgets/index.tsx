'use client'

import { WidgetConfiguration } from '@/types/dashboard'
import ChartWidget from './ChartWidget'
import StatsCardWidget from './StatsCardWidget'
import TableWidget from './TableWidget'
import TextBlockWidget from './TextBlockWidget'
import MetricWidget from './MetricWidget'
import ListWidget from './ListWidget'
import TimelineWidget from './TimelineWidget'
import GaugeWidget from './GaugeWidget'

interface WidgetRendererProps {
  widget: WidgetConfiguration
  isEditing?: boolean
  onEdit?: (widget: WidgetConfiguration) => void
  onDelete?: (widgetId: string) => void
}

export default function WidgetRenderer({ 
  widget, 
  isEditing = false,
  onEdit,
  onDelete 
}: WidgetRendererProps) {
  const renderWidget = () => {
    switch (widget.type) {
      case 'chart':
        return <ChartWidget widget={widget} isEditing={isEditing} />
      case 'stats-card':
        return <StatsCardWidget widget={widget} isEditing={isEditing} />
      case 'table':
        return <TableWidget widget={widget} isEditing={isEditing} />
      case 'text-block':
        return <TextBlockWidget widget={widget} isEditing={isEditing} />
      case 'metric':
        return <MetricWidget widget={widget} isEditing={isEditing} />
      case 'list':
        return <ListWidget widget={widget} isEditing={isEditing} />
      case 'timeline':
        return <TimelineWidget widget={widget} isEditing={isEditing} />
      case 'gauge':
        return <GaugeWidget widget={widget} isEditing={isEditing} />
      default:
        return (
          <div className="bg-gray-100 rounded-lg p-4 h-full flex items-center justify-center">
            <p className="text-gray-500">Unknown widget type: {widget.type}</p>
          </div>
        )
    }
  }

  return (
    <div className="relative h-full">
      {renderWidget()}
      {isEditing && (
        <div className="absolute top-2 right-2 flex gap-1">
          {onEdit && (
            <button
              onClick={() => onEdit(widget)}
              className="p-1 bg-white rounded shadow hover:bg-gray-100"
              title="Edit widget"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" 
                />
              </svg>
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(widget.id)}
              className="p-1 bg-white rounded shadow hover:bg-red-100"
              title="Delete widget"
            >
              <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" 
                />
              </svg>
            </button>
          )}
        </div>
      )}
    </div>
  )
}

export { ChartWidget, StatsCardWidget, TableWidget, TextBlockWidget }