'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { dashboardTemplates } from '@/lib/templates'
import { DashboardTemplate } from '@/types/dashboard'

export default function TemplateGalleryPage() {
  const router = useRouter()
  const [selectedTemplate, setSelectedTemplate] = useState<DashboardTemplate | null>(null)
  const [showPreview, setShowPreview] = useState(false)
  const [filter, setFilter] = useState<string>('all')

  const categories = [
    { id: 'all', name: 'All Templates', icon: '🎨' },
    { id: 'survey_analysis', name: 'Survey Analysis', icon: '📊' },
    { id: 'customer_feedback', name: 'Customer Feedback', icon: '💬' },
    { id: 'lead_scoring', name: 'Lead Scoring', icon: '🎯' },
    { id: 'event_registration', name: 'Event Registration', icon: '📅' },
    { id: 'employee_feedback', name: 'Employee Feedback', icon: '👔' },
    { id: 'product_research', name: 'Product Research', icon: '🔬' },
    { id: 'nps_analysis', name: 'NPS Analysis', icon: '📈' },
    { id: 'custom', name: 'Custom', icon: '✨' }
  ]

  const filteredTemplates = filter === 'all' 
    ? dashboardTemplates 
    : dashboardTemplates.filter(t => t.category === filter)

  const handlePreview = (template: DashboardTemplate) => {
    setSelectedTemplate(template)
    setShowPreview(true)
  }

  const handleApplyTemplate = (template: DashboardTemplate) => {
    localStorage.setItem('selectedTemplate', JSON.stringify(template))
    router.push('/dashboard/editor/new')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-red-50">
      <header className="bg-white/80 backdrop-blur-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <Link href="/dashboard" className="flex items-center">
                <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl flex items-center justify-center">
                  <span className="text-xl font-bold text-white">F</span>
                </div>
                <span className="ml-3 text-xl font-bold text-gray-900">FormFlow AI</span>
              </Link>
              <span className="ml-4 text-gray-500">/</span>
              <span className="ml-4 text-lg font-semibold text-gray-700">Dashboard Templates</span>
            </div>
            <Link 
              href="/dashboard"
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              ← Back to Dashboard
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Choose a Template</h1>
          <p className="text-gray-600">Select a pre-built template to get started quickly, or create your own from scratch</p>
        </div>

        <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
          {categories.map(category => (
            <button
              key={category.id}
              onClick={() => setFilter(category.id)}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 whitespace-nowrap transition-all ${
                filter === category.id 
                  ? 'bg-purple-600 text-white' 
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              <span>{category.icon}</span>
              <span className="text-sm font-medium">{category.name}</span>
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTemplates.map(template => (
            <div 
              key={template.id}
              className="bg-white rounded-xl shadow-sm hover:shadow-lg transition-all duration-200 overflow-hidden group cursor-pointer"
              onClick={() => handlePreview(template)}
            >
              <div className="aspect-video bg-gradient-to-br from-purple-100 to-pink-100 flex items-center justify-center relative">
                <span className="text-6xl">{template.icon}</span>
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-all duration-200 flex items-center justify-center">
                  <span className="text-white bg-purple-600 px-4 py-2 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity">
                    Preview Template
                  </span>
                </div>
              </div>
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{template.name}</h3>
                <p className="text-sm text-gray-600 mb-4">{template.description}</p>
                <div className="flex gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleApplyTemplate(template)
                    }}
                    className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
                  >
                    Use Template
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handlePreview(template)
                    }}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
                  >
                    Preview
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>

      {showPreview && selectedTemplate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200 flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                  <span>{selectedTemplate.icon}</span>
                  {selectedTemplate.name}
                </h2>
                <p className="text-gray-600 mt-1">{selectedTemplate.description}</p>
              </div>
              <button
                onClick={() => setShowPreview(false)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
              <div className="mb-4">
                <h3 className="font-semibold text-gray-900 mb-2">Included Widgets ({selectedTemplate.widgets.length})</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {Array.from(new Set(selectedTemplate.widgets.map(w => w.type))).map(type => (
                    <div key={type} className="bg-gray-100 px-3 py-2 rounded-lg text-sm">
                      {type.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-8">
                <div className="aspect-video bg-white rounded-lg shadow-sm flex items-center justify-center">
                  <p className="text-gray-500">Template Preview</p>
                </div>
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 flex justify-end gap-3">
              <button
                onClick={() => setShowPreview(false)}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  handleApplyTemplate(selectedTemplate)
                }}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                Use This Template
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}