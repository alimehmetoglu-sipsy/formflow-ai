'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { DragDropContext, Droppable, Draggable, DropResult } from 'react-beautiful-dnd'
import WidgetRenderer from '@/components/widgets'
import { 
  DashboardTemplate, 
  WidgetConfiguration, 
  DEFAULT_THEME, 
  DEFAULT_LAYOUT,
  WidgetLibraryItem,
  WidgetType
} from '@/types/dashboard'
import { getTemplateById } from '@/lib/templates'

const widgetLibrary: WidgetLibraryItem[] = [
  {
    type: 'chart',
    name: 'Chart',
    description: 'Bar, line, pie charts',
    icon: '📊',
    defaultSize: 'medium',
    minSize: { w: 3, h: 3 },
    maxSize: { w: 12, h: 8 },
    configurable: true
  },
  {
    type: 'stats-card',
    name: 'Stats Card',
    description: 'Key metrics display',
    icon: '📈',
    defaultSize: 'small',
    minSize: { w: 3, h: 2 },
    maxSize: { w: 6, h: 4 },
    configurable: true
  },
  {
    type: 'table',
    name: 'Table',
    description: 'Data table',
    icon: '📋',
    defaultSize: 'large',
    minSize: { w: 4, h: 3 },
    maxSize: { w: 12, h: 8 },
    configurable: true
  },
  {
    type: 'text-block',
    name: 'Text Block',
    description: 'Rich text content',
    icon: '📝',
    defaultSize: 'medium',
    minSize: { w: 3, h: 2 },
    maxSize: { w: 12, h: 6 },
    configurable: true
  },
  {
    type: 'metric',
    name: 'Metric',
    description: 'Single metric with progress',
    icon: '🎯',
    defaultSize: 'small',
    minSize: { w: 3, h: 2 },
    maxSize: { w: 6, h: 4 },
    configurable: true
  },
  {
    type: 'gauge',
    name: 'Gauge',
    description: 'Visual gauge meter',
    icon: '🌡️',
    defaultSize: 'medium',
    minSize: { w: 4, h: 3 },
    maxSize: { w: 6, h: 5 },
    configurable: true
  },
  {
    type: 'list',
    name: 'List',
    description: 'Bullet or numbered list',
    icon: '📑',
    defaultSize: 'medium',
    minSize: { w: 3, h: 3 },
    maxSize: { w: 6, h: 8 },
    configurable: true
  },
  {
    type: 'timeline',
    name: 'Timeline',
    description: 'Event timeline',
    icon: '📅',
    defaultSize: 'large',
    minSize: { w: 4, h: 4 },
    maxSize: { w: 12, h: 8 },
    configurable: true
  }
]

export default function DashboardEditorPage() {
  const params = useParams()
  const router = useRouter()
  const dashboardId = params.id as string
  const [widgets, setWidgets] = useState<WidgetConfiguration[]>([])
  const [selectedWidget, setSelectedWidget] = useState<WidgetConfiguration | null>(null)
  const [isEditing, setIsEditing] = useState(true)
  const [dashboardName, setDashboardName] = useState('My Dashboard')
  const [showWidgetPanel, setShowWidgetPanel] = useState(true)

  useEffect(() => {
    if (dashboardId === 'new') {
      const savedTemplate = localStorage.getItem('selectedTemplate')
      if (savedTemplate) {
        const template: DashboardTemplate = JSON.parse(savedTemplate)
        setWidgets(template.widgets)
        setDashboardName(template.name)
        localStorage.removeItem('selectedTemplate')
      }
    } else {
      loadDashboard(dashboardId)
    }
  }, [dashboardId])

  const loadDashboard = async (id: string) => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://localhost:8000/api/v1/dashboards/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setWidgets(data.widgets || [])
        setDashboardName(data.name || 'Dashboard')
      }
    } catch (error) {
      console.error('Failed to load dashboard:', error)
    }
  }

  const handleDragEnd = (result: DropResult) => {
    if (!result.destination) return

    const { source, destination, draggableId } = result

    if (source.droppableId === 'widget-library' && destination.droppableId === 'dashboard-canvas') {
      const widgetType = draggableId.replace('library-', '')
      const libraryItem = widgetLibrary.find(item => item.type === widgetType)
      
      if (libraryItem) {
        const newWidget: WidgetConfiguration = {
          id: `widget-${Date.now()}`,
          type: libraryItem.type,
          size: libraryItem.defaultSize,
          title: `New ${libraryItem.name}`,
          position: {
            x: 0,
            y: widgets.length * 2,
            w: libraryItem.minSize.w,
            h: libraryItem.minSize.h
          },
          data: libraryItem.type === 'chart' ? {
            labels: ['Jan', 'Feb', 'Mar', 'Apr'],
            datasets: [{
              label: 'Sales',
              data: [12, 19, 3, 5]
            }]
          } : libraryItem.type === 'stats-card' ? {
            value: '1,234',
            change: '+12%',
            trend: 'up'
          } : libraryItem.type === 'gauge' ? {
            value: 75,
            min: 0,
            max: 100
          } : libraryItem.type === 'metric' ? {
            value: 42,
            target: 50,
            unit: '%'
          } : libraryItem.type === 'table' ? {
            columns: ['Name', 'Value', 'Status'],
            rows: [
              ['Item 1', '100', 'Active'],
              ['Item 2', '200', 'Pending']
            ]
          } : libraryItem.type === 'list' ? {
            items: ['First item', 'Second item', 'Third item']
          } : libraryItem.type === 'timeline' ? {
            events: [
              { date: '2024-01-01', title: 'Event 1', description: 'Description 1' },
              { date: '2024-01-02', title: 'Event 2', description: 'Description 2' }
            ]
          } : libraryItem.type === 'text-block' ? {
            content: 'This is a text block widget. You can add any content here.'
          } : undefined,
          config: libraryItem.type === 'chart' ? {
            chartType: 'bar' as const
          } : undefined
        }
        
        const newWidgets = [...widgets]
        newWidgets.splice(destination.index, 0, newWidget)
        setWidgets(newWidgets)
      }
    } else if (source.droppableId === 'dashboard-canvas' && destination.droppableId === 'dashboard-canvas') {
      const newWidgets = Array.from(widgets)
      const [reorderedWidget] = newWidgets.splice(source.index, 1)
      newWidgets.splice(destination.index, 0, reorderedWidget)
      setWidgets(newWidgets)
    }
  }

  const handleEditWidget = (widget: WidgetConfiguration) => {
    setSelectedWidget(widget)
  }

  const handleDeleteWidget = (widgetId: string) => {
    setWidgets(widgets.filter(w => w.id !== widgetId))
  }

  const handleAddWidget = (widgetType: WidgetType) => {
    const libraryItem = widgetLibrary.find(item => item.type === widgetType)
    
    if (libraryItem) {
      const newWidget: WidgetConfiguration = {
        id: `widget-${Date.now()}`,
        type: libraryItem.type,
        size: libraryItem.defaultSize,
        title: `New ${libraryItem.name}`,
        position: {
          x: 0,
          y: widgets.length * 2,
          w: libraryItem.minSize.w,
          h: libraryItem.minSize.h
        },
        data: libraryItem.type === 'chart' ? {
          labels: ['Jan', 'Feb', 'Mar', 'Apr'],
          datasets: [{
            label: 'Sales',
            data: [12, 19, 3, 5]
          }]
        } : libraryItem.type === 'stats-card' ? {
          value: '1,234',
          change: '+12%',
          trend: 'up'
        } : libraryItem.type === 'gauge' ? {
          value: 75,
          min: 0,
          max: 100
        } : libraryItem.type === 'metric' ? {
          value: 42,
          target: 50,
          unit: '%'
        } : libraryItem.type === 'table' ? {
          columns: ['Name', 'Value', 'Status'],
          rows: [
            ['Item 1', '100', 'Active'],
            ['Item 2', '200', 'Pending']
          ]
        } : libraryItem.type === 'list' ? {
          items: ['First item', 'Second item', 'Third item']
        } : libraryItem.type === 'timeline' ? {
          events: [
            { date: '2024-01-01', title: 'Event 1', description: 'Description 1' },
            { date: '2024-01-02', title: 'Event 2', description: 'Description 2' }
          ]
        } : libraryItem.type === 'text-block' ? {
          content: 'This is a text block widget. You can add any content here.'
        } : undefined,
        config: libraryItem.type === 'chart' ? {
          chartType: 'bar' as const
        } : undefined
      }
      
      setWidgets([...widgets, newWidget])
    }
  }

  const handleSaveDashboard = async () => {
    try {
      const token = localStorage.getItem('token')
      const endpoint = dashboardId === 'new' 
        ? 'http://localhost:8000/api/v1/dashboards'
        : `http://localhost:8000/api/v1/dashboards/${dashboardId}`
      
      const response = await fetch(endpoint, {
        method: dashboardId === 'new' ? 'POST' : 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: dashboardName,
          widgets,
          theme: DEFAULT_THEME,
          layout: DEFAULT_LAYOUT
        })
      })

      if (response.ok) {
        const data = await response.json()
        if (dashboardId === 'new') {
          router.push(`/dashboard/editor/${data.id}`)
        }
        alert('Dashboard saved successfully!')
      }
    } catch (error) {
      console.error('Failed to save dashboard:', error)
      alert('Failed to save dashboard')
    }
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white border-b border-gray-200">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-3">
            <div className="flex items-center gap-4">
              <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
                ← Back
              </Link>
              <input
                type="text"
                value={dashboardName}
                onChange={(e) => setDashboardName(e.target.value)}
                className="text-xl font-semibold bg-transparent border-b border-transparent hover:border-gray-300 focus:border-purple-600 outline-none px-1"
              />
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsEditing(!isEditing)}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  isEditing 
                    ? 'bg-purple-100 text-purple-700' 
                    : 'bg-gray-100 text-gray-700'
                }`}
              >
                {isEditing ? 'Editing' : 'Preview'}
              </button>
              <button
                onClick={() => setShowWidgetPanel(!showWidgetPanel)}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                {showWidgetPanel ? 'Hide' : 'Show'} Widgets
              </button>
              <button
                onClick={handleSaveDashboard}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                Save Dashboard
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex h-[calc(100vh-64px)]">
        <DragDropContext onDragEnd={handleDragEnd}>
          {showWidgetPanel && isEditing && (
            <div className="w-64 bg-white border-r border-gray-200 p-4 overflow-y-auto">
              <h3 className="font-semibold text-gray-900 mb-4">Widget Library</h3>
              <Droppable droppableId="widget-library" isDropDisabled={false}>
                {(provided) => (
                  <div {...provided.droppableProps} ref={provided.innerRef}>
                    {widgetLibrary.map((item, index) => (
                      <Draggable 
                        key={item.type} 
                        draggableId={`library-${item.type}`} 
                        index={index}
                      >
                        {(provided, snapshot) => (
                          <>
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              onClick={() => handleAddWidget(item.type)}
                              className={`p-3 mb-2 bg-gray-50 rounded-lg cursor-move hover:bg-gray-100 transition-all ${
                                snapshot.isDragging ? 'opacity-50 shadow-lg transform scale-105' : ''
                              }`}
                              style={{
                                ...provided.draggableProps.style,
                                transform: snapshot.isDragging 
                                  ? provided.draggableProps.style?.transform 
                                  : 'none'
                              }}
                            >
                              <div className="flex items-center gap-3">
                                <span className="text-2xl">{item.icon}</span>
                                <div>
                                  <p className="font-medium text-sm">{item.name}</p>
                                  <p className="text-xs text-gray-500">{item.description}</p>
                                </div>
                              </div>
                            </div>
                            {snapshot.isDragging && (
                              <div className="p-3 mb-2 bg-gray-100 border-2 border-dashed border-gray-300 rounded-lg">
                                <div className="flex items-center gap-3 opacity-40">
                                  <span className="text-2xl">{item.icon}</span>
                                  <div>
                                    <p className="font-medium text-sm">{item.name}</p>
                                    <p className="text-xs text-gray-500">{item.description}</p>
                                  </div>
                                </div>
                              </div>
                            )}
                          </>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </div>
          )}

          <div className="flex-1 p-6 overflow-auto">
            <Droppable droppableId="dashboard-canvas">
              {(provided, snapshot) => (
                <div
                  {...provided.droppableProps}
                  ref={provided.innerRef}
                  className={`min-h-full transition-all ${
                    snapshot.isDraggingOver ? 'bg-purple-50 ring-2 ring-purple-400 ring-opacity-50 rounded-lg' : ''
                  }`}
                >
                  {widgets.length === 0 ? (
                    <div className={`h-96 border-2 border-dashed rounded-lg flex items-center justify-center transition-all ${
                      snapshot.isDraggingOver ? 'border-purple-400 bg-purple-50' : 'border-gray-300'
                    }`}>
                      <div className="text-center">
                        <p className="text-gray-500 mb-2">
                          {snapshot.isDraggingOver ? 'Drop widget here' : 'No widgets added yet'}
                        </p>
                        {isEditing && !snapshot.isDraggingOver && (
                          <p className="text-sm text-gray-400">
                            Drag widgets from the library or click to add
                          </p>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="grid grid-cols-12 gap-4">
                      {widgets.map((widget, index) => (
                        <Draggable
                          key={widget.id}
                          draggableId={widget.id}
                          index={index}
                          isDragDisabled={!isEditing}
                        >
                          {(provided, dragSnapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              className={`transition-all ${
                                dragSnapshot.isDragging ? 'shadow-2xl opacity-90 transform rotate-1' : ''
                              }`}
                              style={{
                                gridColumn: `span ${widget.position.w}`,
                                gridRow: `span ${widget.position.h}`,
                                ...provided.draggableProps.style
                              }}
                            >
                              <WidgetRenderer
                                widget={widget}
                                isEditing={isEditing}
                                onEdit={handleEditWidget}
                                onDelete={handleDeleteWidget}
                              />
                            </div>
                          )}
                        </Draggable>
                      ))}
                    </div>
                  )}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </div>
        </DragDropContext>
      </div>
    </div>
  )
}