'use client'

import { WidgetConfiguration } from '@/types/dashboard'

interface StatsCardWidgetProps {
  widget: WidgetConfiguration
  isEditing?: boolean
}

export default function StatsCardWidget({ widget, isEditing = false }: StatsCardWidgetProps) {
  const { title, data, config } = widget
  const value = data?.value || 0
  const change = data?.change || 0
  const label = data?.label || title || 'Metric'
  const icon = config?.icon || '📊'
  const color = config?.color || '#6366f1'
  const trend = data?.trend || 'neutral'

  const getTrendIcon = () => {
    if (trend === 'up') return '↑'
    if (trend === 'down') return '↓'
    return '→'
  }

  const getTrendColor = () => {
    if (trend === 'up') return 'text-green-600'
    if (trend === 'down') return 'text-red-600'
    return 'text-gray-600'
  }

  const formatValue = (val: any) => {
    if (typeof val === 'number') {
      if (val >= 1000000) return `${(val / 1000000).toFixed(1)}M`
      if (val >= 1000) return `${(val / 1000).toFixed(1)}K`
      return val.toLocaleString()
    }
    return val
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm p-6 h-full ${isEditing ? 'ring-2 ring-purple-500' : ''}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-gray-600 mb-1">{label}</p>
          <div className="flex items-baseline gap-2">
            <h2 className="text-3xl font-bold text-gray-900">
              {formatValue(value)}
            </h2>
            {change !== 0 && (
              <span className={`flex items-center text-sm font-medium ${getTrendColor()}`}>
                <span className="mr-1">{getTrendIcon()}</span>
                {Math.abs(change)}%
              </span>
            )}
          </div>
        </div>
        <div 
          className="w-12 h-12 rounded-lg flex items-center justify-center text-2xl"
          style={{ backgroundColor: `${color}20` }}
        >
          {icon}
        </div>
      </div>
      {data?.subtitle && (
        <p className="text-xs text-gray-500 mt-2">{data.subtitle}</p>
      )}
    </div>
  )
}