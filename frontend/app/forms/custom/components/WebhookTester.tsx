'use client'

import { useState } from 'react'

interface WebhookConfig {
  id: string
  name: string
  platform: string
  field_mappings: Record<string, any>
  [key: string]: any
}

interface WebhookTesterProps {
  config: WebhookConfig
}

const SAMPLE_DATA = {
  jotform: {
    submissionID: "123456789",
    formTitle: "Customer Feedback Form",
    createdAt: "2024-01-15T10:30:00Z",
    answers: {
      "q1_name": "Alice Johnson",
      "q2_email": "alice@example.com",
      "q3_rating": "5",
      "q4_feedback": "Excellent service, very satisfied!"
    }
  },
  microsoft_forms: {
    id: "response_abc123",
    title: "Employee Survey",
    submitDate: "2024-01-15T14:20:00Z",
    data: {
      "department": "Engineering",
      "satisfaction": "Very Satisfied",
      "suggestions": "More flexible working hours"
    }
  },
  surveymonkey: {
    survey_title: "Market Research Survey",
    response_id: "resp_xyz789",
    date_created: "2024-01-15T09:15:00Z",
    pages: [
      {
        questions: [
          {
            answers: ["Product A", "Very Likely", "Great quality"]
          }
        ]
      }
    ]
  },
  custom: {
    id: "sub_12345",
    form_title: "Contact Form",
    timestamp: "2024-01-15T12:00:00Z",
    data: {
      name: "Bob Smith",
      email: "bob@company.com",
      message: "Interested in your services",
      phone: "+1-555-0123"
    }
  }
}

interface TestResult {
  success: boolean
  mapped_data?: Record<string, any>
  typeform_format?: Record<string, any>
  field_mapping_results?: Record<string, string>
  error?: string
}

export default function WebhookTester({ config }: WebhookTesterProps) {
  const [testData, setTestData] = useState('')
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<TestResult | null>(null)
  const [selectedSample, setSelectedSample] = useState(config.platform)

  const loadSampleData = (platform: string) => {
    const sample = SAMPLE_DATA[platform as keyof typeof SAMPLE_DATA] || SAMPLE_DATA.custom
    setTestData(JSON.stringify(sample, null, 2))
    setSelectedSample(platform)
  }

  const runTest = async () => {
    setTesting(true)
    setTestResult(null)

    try {
      // Parse test data
      let parsedData
      try {
        parsedData = JSON.parse(testData)
      } catch (error) {
        setTestResult({
          success: false,
          error: 'Invalid JSON format in test data'
        })
        return
      }

      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/v1/webhooks/test', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          webhook_config_id: config.id,
          test_data: parsedData
        })
      })

      if (response.ok) {
        const result = await response.json()
        setTestResult(result)
      } else {
        const error = await response.json()
        setTestResult({
          success: false,
          error: error.detail || 'Test failed'
        })
      }
    } catch (error) {
      console.error('Test failed:', error)
      setTestResult({
        success: false,
        error: 'Network error occurred'
      })
    } finally {
      setTesting(false)
    }
  }

  const sendRealWebhook = async () => {
    if (!testData) {
      alert('Please enter test data first')
      return
    }

    try {
      const parsedData = JSON.parse(testData)
      
      const response = await fetch(config.webhook_url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(parsedData)
      })

      if (response.ok) {
        const result = await response.json()
        alert(`Webhook sent successfully! Status: ${result.status}`)
      } else {
        alert(`Webhook failed with status: ${response.status}`)
      }
    } catch (error) {
      console.error('Failed to send webhook:', error)
      alert('Failed to send webhook')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium mb-2">Test Your Webhook</h3>
        <p className="text-sm text-gray-600">
          Test your field mappings with sample data to ensure everything works correctly
        </p>
      </div>

      {/* Sample Data Selector */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Load Sample Data
        </label>
        <div className="flex gap-2 mb-4">
          {Object.keys(SAMPLE_DATA).map((platform) => (
            <button
              key={platform}
              onClick={() => loadSampleData(platform)}
              className={`px-3 py-2 text-sm rounded-lg ${
                selectedSample === platform
                  ? 'bg-purple-100 text-purple-700'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {platform.replace('_', ' ').toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Test Data Input */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Test Data (JSON)
        </label>
        <textarea
          value={testData}
          onChange={(e) => setTestData(e.target.value)}
          placeholder="Enter your webhook payload JSON here..."
          className="w-full h-64 px-3 py-2 border border-gray-200 rounded-lg font-mono text-sm"
        />
      </div>

      {/* Test Buttons */}
      <div className="flex gap-4">
        <button
          onClick={runTest}
          disabled={testing || !testData}
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {testing ? 'Testing Mappings...' : '🧪 Test Field Mappings'}
        </button>
        
        <button
          onClick={sendRealWebhook}
          disabled={!testData}
          className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
        >
          🚀 Send Real Webhook
        </button>
      </div>

      {/* Test Results */}
      {testResult && (
        <div className={`p-4 rounded-lg ${
          testResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
        }`}>
          <div className="flex items-center mb-3">
            <span className="text-lg mr-2">
              {testResult.success ? '✅' : '❌'}
            </span>
            <h4 className={`font-medium ${
              testResult.success ? 'text-green-800' : 'text-red-800'
            }`}>
              {testResult.success ? 'Test Passed!' : 'Test Failed'}
            </h4>
          </div>

          {testResult.error && (
            <div className="mb-4">
              <p className="text-sm text-red-700 font-medium">Error:</p>
              <p className="text-sm text-red-600">{testResult.error}</p>
            </div>
          )}

          {testResult.field_mapping_results && (
            <div className="mb-4">
              <p className="text-sm font-medium text-gray-700 mb-2">Field Mapping Results:</p>
              <div className="space-y-1">
                {Object.entries(testResult.field_mapping_results).map(([field, result]) => (
                  <div key={field} className="flex items-center text-sm">
                    <span className="w-32 text-gray-600">{field}:</span>
                    <span className={result.startsWith('✓') ? 'text-green-600' : 'text-red-600'}>
                      {result}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {testResult.mapped_data && (
            <div className="mb-4">
              <p className="text-sm font-medium text-gray-700 mb-2">Mapped Data:</p>
              <pre className="text-xs bg-gray-50 p-3 rounded border overflow-x-auto">
                {JSON.stringify(testResult.mapped_data, null, 2)}
              </pre>
            </div>
          )}

          {testResult.typeform_format && (
            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Converted Format:</p>
              <pre className="text-xs bg-gray-50 p-3 rounded border overflow-x-auto">
                {JSON.stringify(testResult.typeform_format, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Instructions */}
      <div className="p-4 bg-blue-50 rounded-lg">
        <h4 className="font-medium text-blue-900 mb-2">📝 Testing Instructions</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li><strong>Test Field Mappings:</strong> Validates your JSONPath expressions without creating a dashboard</li>
          <li><strong>Send Real Webhook:</strong> Sends an actual webhook request that will create a dashboard</li>
          <li><strong>Use sample data:</strong> Click the platform buttons to load realistic test data</li>
          <li><strong>Check results:</strong> Review the mapped data to ensure fields are extracted correctly</li>
        </ul>
      </div>
    </div>
  )
}