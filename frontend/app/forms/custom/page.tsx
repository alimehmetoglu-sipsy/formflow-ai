'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import FieldMapper from './components/FieldMapper'
import WebhookTester from './components/WebhookTester'
import WebhookLogs from './components/WebhookLogs'

interface WebhookConfig {
  id: string
  name: string
  webhook_token: string
  webhook_url: string
  platform: string
  field_mappings: Record<string, any>
  is_active: boolean
  created_at: string
  updated_at: string
}

interface PlatformPreset {
  [key: string]: Record<string, string>
}

const PLATFORM_OPTIONS = [
  { value: 'custom', label: 'Custom Platform', icon: '🔧' },
  { value: 'jotform', label: 'JotForm', icon: '📝' },
  { value: 'microsoft_forms', label: 'Microsoft Forms', icon: '📋' },
  { value: 'surveymonkey', label: 'SurveyMonkey', icon: '🐵' },
  { value: 'airtable', label: 'Airtable Forms', icon: '📊' },
  { value: 'cognito', label: 'Cognito Forms', icon: '🧠' },
  { value: 'wpforms', label: 'WPForms', icon: '🏗️' }
]

export default function CustomWebhookPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [webhookConfigs, setWebhookConfigs] = useState<WebhookConfig[]>([])
  const [platformPresets, setPlatformPresets] = useState<PlatformPreset>({})
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [selectedConfig, setSelectedConfig] = useState<WebhookConfig | null>(null)
  const [activeTab, setActiveTab] = useState<'config' | 'test' | 'logs'>('config')
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    platform: 'custom',
    field_mappings: {} as Record<string, any>,
    signature_secret: '',
    is_active: true
  })

  useEffect(() => {
    const token = localStorage.getItem('token')
    const userData = localStorage.getItem('user')
    
    if (!token) {
      router.push('/login')
      return
    }

    if (userData) {
      setUser(JSON.parse(userData))
    }

    fetchWebhookConfigs()
    fetchPlatformPresets()
  }, [router])

  const fetchWebhookConfigs = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/v1/webhooks/configs', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const configs = await response.json()
        setWebhookConfigs(configs)
        if (configs.length > 0 && !selectedConfig) {
          setSelectedConfig(configs[0])
        }
      }
    } catch (error) {
      console.error('Failed to fetch webhook configs:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchPlatformPresets = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/webhooks/presets')
      if (response.ok) {
        const data = await response.json()
        setPlatformPresets(data.presets)
      }
    } catch (error) {
      console.error('Failed to fetch platform presets:', error)
    }
  }

  const handleCreateConfig = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreating(true)

    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/v1/webhooks/configs', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      })

      if (response.ok) {
        const newConfig = await response.json()
        setWebhookConfigs([...webhookConfigs, newConfig])
        setSelectedConfig(newConfig)
        // Reset form
        setFormData({
          name: '',
          platform: 'custom',
          field_mappings: {},
          signature_secret: '',
          is_active: true
        })
      } else {
        const error = await response.json()
        alert(`Failed to create webhook: ${error.detail}`)
      }
    } catch (error) {
      console.error('Failed to create webhook config:', error)
      alert('Failed to create webhook configuration')
    } finally {
      setCreating(false)
    }
  }

  const handlePlatformChange = (platform: string) => {
    setFormData(prev => ({
      ...prev,
      platform,
      field_mappings: platformPresets[platform] || {}
    }))
  }

  const copyWebhookUrl = (url: string) => {
    navigator.clipboard.writeText(url)
    // Could add toast notification here
  }

  const toggleWebhookStatus = async (config: WebhookConfig) => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://localhost:8000/api/v1/webhooks/configs/${config.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_active: !config.is_active })
      })

      if (response.ok) {
        const updatedConfig = await response.json()
        setWebhookConfigs(configs => 
          configs.map(c => c.id === config.id ? updatedConfig : c)
        )
        if (selectedConfig?.id === config.id) {
          setSelectedConfig(updatedConfig)
        }
      }
    } catch (error) {
      console.error('Failed to toggle webhook status:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-red-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-red-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <Link href="/" className="flex items-center">
                <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl flex items-center justify-center">
                  <span className="text-xl font-bold text-white">F</span>
                </div>
                <span className="ml-3 text-xl font-bold text-gray-900">FormFlow AI</span>
              </Link>
            </div>

            <div className="flex items-center gap-4">
              <Link
                href="/forms"
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                ← Back to Forms
              </Link>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Custom Webhook Integration</h1>
          <p className="text-gray-600">
            Connect any form platform by configuring custom webhooks with field mapping
          </p>
        </div>

        <div className="grid grid-cols-12 gap-8">
          {/* Left Sidebar - Webhook Configs */}
          <div className="col-span-4">
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold mb-4">Your Webhooks</h2>

              {/* Create New Webhook Form */}
              <form onSubmit={handleCreateConfig} className="mb-6 p-4 bg-gray-50 rounded-lg">
                <h3 className="font-medium mb-3">Create New Webhook</h3>
                
                <div className="space-y-3">
                  <input
                    type="text"
                    placeholder="Webhook name"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg"
                    required
                  />
                  
                  <select
                    value={formData.platform}
                    onChange={(e) => handlePlatformChange(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg"
                  >
                    {PLATFORM_OPTIONS.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.icon} {option.label}
                      </option>
                    ))}
                  </select>
                  
                  <button
                    type="submit"
                    disabled={creating || !formData.name}
                    className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
                  >
                    {creating ? 'Creating...' : 'Create Webhook'}
                  </button>
                </div>
              </form>

              {/* Webhook List */}
              <div className="space-y-3">
                {webhookConfigs.map((config) => (
                  <div
                    key={config.id}
                    onClick={() => setSelectedConfig(config)}
                    className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      selectedConfig?.id === config.id
                        ? 'border-purple-500 bg-purple-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium">{config.name}</h3>
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${
                          config.is_active
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        {config.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 capitalize">{config.platform.replace('_', ' ')}</p>
                  </div>
                ))}

                {webhookConfigs.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <p>No webhooks configured yet</p>
                    <p className="text-sm">Create your first webhook above</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Main Content Area */}
          <div className="col-span-8">
            {selectedConfig ? (
              <div className="bg-white rounded-xl shadow-sm">
                {/* Tab Navigation */}
                <div className="border-b border-gray-200">
                  <div className="flex">
                    {[
                      { key: 'config', label: 'Configuration', icon: '⚙️' },
                      { key: 'test', label: 'Test', icon: '🧪' },
                      { key: 'logs', label: 'Logs', icon: '📜' }
                    ].map((tab) => (
                      <button
                        key={tab.key}
                        onClick={() => setActiveTab(tab.key as any)}
                        className={`px-6 py-4 font-medium ${
                          activeTab === tab.key
                            ? 'text-purple-600 border-b-2 border-purple-600'
                            : 'text-gray-600 hover:text-gray-900'
                        }`}
                      >
                        {tab.icon} {tab.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="p-6">
                  {activeTab === 'config' && (
                    <div className="space-y-6">
                      {/* Webhook URL */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Webhook URL
                        </label>
                        <div className="flex items-center gap-2">
                          <input
                            type="text"
                            value={selectedConfig.webhook_url}
                            readOnly
                            className="flex-1 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg font-mono text-sm"
                          />
                          <button
                            onClick={() => copyWebhookUrl(selectedConfig.webhook_url)}
                            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                          >
                            Copy
                          </button>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          Use this URL as the webhook endpoint in your form platform
                        </p>
                      </div>

                      {/* Status Toggle */}
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-medium">Webhook Status</h3>
                          <p className="text-sm text-gray-600">
                            {selectedConfig.is_active ? 'Webhook is active and receiving requests' : 'Webhook is disabled'}
                          </p>
                        </div>
                        <button
                          onClick={() => toggleWebhookStatus(selectedConfig)}
                          className={`px-4 py-2 rounded-lg font-medium ${
                            selectedConfig.is_active
                              ? 'bg-red-100 text-red-700 hover:bg-red-200'
                              : 'bg-green-100 text-green-700 hover:bg-green-200'
                          }`}
                        >
                          {selectedConfig.is_active ? 'Disable' : 'Enable'}
                        </button>
                      </div>

                      {/* Field Mapping */}
                      <FieldMapper
                        config={selectedConfig}
                        onUpdate={(mappings) => {
                          setSelectedConfig(prev => prev ? { ...prev, field_mappings: mappings } : null)
                        }}
                      />
                    </div>
                  )}

                  {activeTab === 'test' && (
                    <WebhookTester config={selectedConfig} />
                  )}

                  {activeTab === 'logs' && (
                    <WebhookLogs config={selectedConfig} />
                  )}
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-xl shadow-sm p-12 text-center">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🔗</span>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Webhook Selected</h3>
                <p className="text-gray-600">
                  Create or select a webhook configuration to get started
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}