'use client'

import { WidgetConfiguration } from '@/types/dashboard'

interface TextBlockWidgetProps {
  widget: WidgetConfiguration
  isEditing?: boolean
}

export default function TextBlockWidget({ widget, isEditing = false }: TextBlockWidgetProps) {
  const { title, data, config } = widget
  const content = data?.content || ''
  const alignment = config?.alignment || 'left'
  const fontSize = config?.fontSize || 'medium'

  const getFontSizeClass = () => {
    switch (fontSize) {
      case 'small': return 'text-sm'
      case 'large': return 'text-lg'
      default: return 'text-base'
    }
  }

  const getAlignmentClass = () => {
    switch (alignment) {
      case 'center': return 'text-center'
      case 'right': return 'text-right'
      default: return 'text-left'
    }
  }

  const renderContent = () => {
    if (data?.html) {
      return (
        <div 
          className={`prose prose-sm max-w-none ${getFontSizeClass()} ${getAlignmentClass()}`}
          dangerouslySetInnerHTML={{ __html: data.html }}
        />
      )
    }

    if (data?.bullets) {
      return (
        <ul className={`space-y-2 ${getFontSizeClass()}`}>
          {data.bullets.map((item: string, index: number) => (
            <li key={index} className="flex items-start">
              <span className="text-purple-600 mr-2">•</span>
              <span className="text-gray-700">{item}</span>
            </li>
          ))}
        </ul>
      )
    }

    return (
      <p className={`text-gray-700 whitespace-pre-wrap ${getFontSizeClass()} ${getAlignmentClass()}`}>
        {content}
      </p>
    )
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm p-4 h-full ${isEditing ? 'ring-2 ring-purple-500' : ''}`}>
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-3">{title}</h3>
      )}
      {renderContent()}
    </div>
  )
}