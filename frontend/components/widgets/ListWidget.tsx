'use client'

import { WidgetConfiguration } from '@/types/dashboard'

interface ListWidgetProps {
  widget: WidgetConfiguration
  isEditing?: boolean
}

export default function ListWidget({ widget, isEditing = false }: ListWidgetProps) {
  const { title, description, data, config } = widget
  const items = data?.items || []
  const style = config?.style || 'bullet'
  const showIcons = config?.showIcons !== false
  const iconColor = config?.iconColor || '#6366f1'

  const getIcon = (item: any) => {
    if (item.icon) return item.icon
    if (style === 'check') return '✓'
    if (style === 'number') return null
    return '•'
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm p-4 h-full overflow-auto ${isEditing ? 'ring-2 ring-purple-500' : ''}`}>
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-1">{title}</h3>
      )}
      {description && (
        <p className="text-sm text-gray-600 mb-3">{description}</p>
      )}
      
      <ul className="space-y-2">
        {items.map((item: any, index: number) => {
          const isObject = typeof item === 'object'
          const text = isObject ? item.text || item.label || item.name : item
          const subtext = isObject ? item.subtext || item.description : null
          const icon = showIcons ? getIcon(item) : null
          
          return (
            <li key={index} className="flex items-start">
              {icon !== null && (
                <span 
                  className="mr-2 flex-shrink-0"
                  style={{ color: iconColor }}
                >
                  {style === 'number' ? `${index + 1}.` : icon}
                </span>
              )}
              <div className="flex-1">
                <p className="text-gray-900">{text}</p>
                {subtext && (
                  <p className="text-sm text-gray-500 mt-1">{subtext}</p>
                )}
              </div>
            </li>
          )
        })}
        {items.length === 0 && (
          <li className="text-gray-500 text-sm">No items to display</li>
        )}
      </ul>
    </div>
  )
}