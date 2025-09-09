'use client'

import { WidgetConfiguration } from '@/types/dashboard'

interface TableWidgetProps {
  widget: WidgetConfiguration
  isEditing?: boolean
}

export default function TableWidget({ widget, isEditing = false }: TableWidgetProps) {
  const { title, description, data } = widget
  const columns = data?.columns || []
  const rows = data?.rows || []

  return (
    <div className={`bg-white rounded-lg shadow-sm p-4 h-full overflow-auto ${isEditing ? 'ring-2 ring-purple-500' : ''}`}>
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-1">{title}</h3>
      )}
      {description && (
        <p className="text-sm text-gray-600 mb-3">{description}</p>
      )}
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((column: any, index: number) => (
                <th
                  key={index}
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  {column.label || column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {rows.map((row: any, rowIndex: number) => (
              <tr key={rowIndex} className="hover:bg-gray-50">
                {columns.map((column: any, colIndex: number) => (
                  <td key={colIndex} className="px-4 py-3 text-sm text-gray-900">
                    {row[column.key || column] || row[colIndex] || '-'}
                  </td>
                ))}
              </tr>
            ))}
            {rows.length === 0 && (
              <tr>
                <td 
                  colSpan={columns.length} 
                  className="px-4 py-8 text-center text-sm text-gray-500"
                >
                  No data available
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}