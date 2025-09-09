'use client'

import { WidgetConfiguration } from '@/types/dashboard'

interface MetricWidgetProps {
  widget: WidgetConfiguration
  isEditing?: boolean
}

export default function MetricWidget({ widget, isEditing = false }: MetricWidgetProps) {
  const { title, data, config } = widget
  const value = data?.value || 0
  const unit = data?.unit || ''
  const label = data?.label || title || 'Metric'
  const color = config?.color || '#6366f1'
  const target = data?.target
  const progress = target ? (value / target) * 100 : null

  return (
    <div className={`bg-white rounded-lg shadow-sm p-6 h-full flex flex-col justify-center ${isEditing ? 'ring-2 ring-purple-500' : ''}`}>
      <div className="text-center">
        <p className="text-sm text-gray-600 mb-2">{label}</p>
        <div className="mb-3">
          <span 
            className="text-4xl font-bold"
            style={{ color }}
          >
            {value}
          </span>
          {unit && (
            <span className="text-2xl text-gray-600 ml-1">{unit}</span>
          )}
        </div>
        
        {progress !== null && (
          <div className="mt-4">
            <div className="flex justify-between text-xs text-gray-600 mb-1">
              <span>Progress</span>
              <span>{progress.toFixed(0)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="h-2 rounded-full transition-all duration-300"
                style={{ 
                  width: `${Math.min(progress, 100)}%`,
                  backgroundColor: color
                }}
              />
            </div>
            {target && (
              <p className="text-xs text-gray-500 mt-1">
                Target: {target}{unit}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}