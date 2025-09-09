export type WidgetSize = 'small' | 'medium' | 'large' | 'full-width'

export type WidgetType = 
  | 'chart' 
  | 'stats-card' 
  | 'table' 
  | 'text-block' 
  | 'metric' 
  | 'list' 
  | 'timeline'
  | 'gauge'

export type ChartType = 
  | 'bar' 
  | 'line' 
  | 'pie' 
  | 'area' 
  | 'donut' 
  | 'scatter'
  | 'radar'

export interface WidgetConfiguration {
  id: string
  type: WidgetType
  size: WidgetSize
  title: string
  description?: string
  position: {
    x: number
    y: number
    w: number
    h: number
  }
  data?: any
  config?: {
    chartType?: ChartType
    color?: string
    icon?: string
    showLegend?: boolean
    showGrid?: boolean
    [key: string]: any
  }
}

export interface ThemeConfiguration {
  id: string
  name: string
  primaryColor: string
  secondaryColor: string
  accentColor: string
  backgroundColor: string
  textColor: string
  borderRadius: 'none' | 'small' | 'medium' | 'large'
  shadowIntensity: 'none' | 'light' | 'medium' | 'heavy'
  fontFamily: string
  fontSize: 'small' | 'medium' | 'large'
}

export interface DashboardTemplate {
  id: string
  name: string
  description: string
  category: TemplateCategory
  thumbnail?: string
  icon: string
  widgets: WidgetConfiguration[]
  theme: ThemeConfiguration
  layout: LayoutConfiguration
  isCustom?: boolean
  createdBy?: string
  createdAt?: string
  tags?: string[]
}

export type TemplateCategory = 
  | 'survey_analysis'
  | 'customer_feedback'
  | 'lead_scoring'
  | 'event_registration'
  | 'employee_feedback'
  | 'product_research'
  | 'nps_analysis'
  | 'custom'
  | 'sales'
  | 'marketing'
  | 'hr'
  | 'analytics'

export interface LayoutConfiguration {
  type: 'grid' | 'freeform'
  columns: number
  rows?: number
  gap: number
  padding: number
  responsive: boolean
}

export interface Dashboard {
  id: string
  name: string
  description?: string
  templateId?: string
  widgets: WidgetConfiguration[]
  theme: ThemeConfiguration
  layout: LayoutConfiguration
  userId: string
  createdAt: string
  updatedAt: string
  isPublic?: boolean
  shareUrl?: string
  viewCount?: number
}

export interface CustomTemplate extends DashboardTemplate {
  userId: string
  isPublic: boolean
  usageCount: number
  rating?: number
}

export interface WidgetLibraryItem {
  type: WidgetType
  name: string
  description: string
  icon: string
  defaultSize: WidgetSize
  minSize: { w: number; h: number }
  maxSize: { w: number; h: number }
  configurable: boolean
  preview?: string
}

export interface DragDropContext {
  isDragging: boolean
  draggedWidget?: WidgetConfiguration
  dropTarget?: { x: number; y: number }
}

export interface TemplatePreview {
  template: DashboardTemplate
  isLoading?: boolean
  onApply: (template: DashboardTemplate) => void
  onCustomize: (template: DashboardTemplate) => void
  onPreview: (template: DashboardTemplate) => void
}

export const DEFAULT_THEME: ThemeConfiguration = {
  id: 'default',
  name: 'Default',
  primaryColor: '#6366f1',
  secondaryColor: '#8b5cf6',
  accentColor: '#ec4899',
  backgroundColor: '#ffffff',
  textColor: '#1f2937',
  borderRadius: 'medium',
  shadowIntensity: 'light',
  fontFamily: 'Inter, system-ui, sans-serif',
  fontSize: 'medium'
}

export const DEFAULT_LAYOUT: LayoutConfiguration = {
  type: 'grid',
  columns: 12,
  gap: 16,
  padding: 20,
  responsive: true
}