'use client'

import { useState, useEffect } from 'react'

interface WebhookConfig {
  id: string
  name: string
  platform: string
  field_mappings: Record<string, any>
  [key: string]: any
}

interface FieldMapperProps {
  config: WebhookConfig
  onUpdate: (mappings: Record<string, any>) => void
}

const REQUIRED_FIELDS = [
  {
    key: 'form_title',
    label: 'Form Title',
    description: 'The title/name of the form',
    example: '$.form.title'
  },
  {
    key: 'submission_id',
    label: 'Submission ID',
    description: 'Unique identifier for this submission',
    example: '$.id'
  },
  {
    key: 'submitted_at',
    label: 'Submitted At',
    description: 'When the form was submitted (ISO timestamp)',
    example: '$.timestamp'
  },
  {
    key: 'answers',
    label: 'Form Answers',
    description: 'The actual form responses/answers',
    example: '$.data'
  }
]

const PLATFORM_EXAMPLES = {
  jotform: {
    form_title: '$.formTitle',
    submission_id: '$.submissionID',
    submitted_at: '$.createdAt',
    answers: '$.answers'
  },
  microsoft_forms: {
    form_title: '$.title',
    submission_id: '$.id',
    submitted_at: '$.submitDate',
    answers: '$.data'
  },
  surveymonkey: {
    form_title: '$.survey_title',
    submission_id: '$.response_id',
    submitted_at: '$.date_created',
    answers: '$.pages[*].questions[*].answers'
  },
  custom: {
    form_title: '$.form_title',
    submission_id: '$.id',
    submitted_at: '$.timestamp',
    answers: '$.data'
  }
}

export default function FieldMapper({ config, onUpdate }: FieldMapperProps) {
  const [mappings, setMappings] = useState<Record<string, any>>(config.field_mappings || {})
  const [saving, setSaving] = useState(false)
  const [showJsonEditor, setShowJsonEditor] = useState(false)
  const [jsonInput, setJsonInput] = useState('')

  useEffect(() => {
    setMappings(config.field_mappings || {})
  }, [config.field_mappings])

  const handleFieldChange = (fieldKey: string, value: string) => {
    const newMappings = {
      ...mappings,
      [fieldKey]: value
    }
    setMappings(newMappings)
  }

  const handleSaveMappings = async () => {
    setSaving(true)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://localhost:8000/api/v1/webhooks/configs/${config.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ field_mappings: mappings })
      })

      if (response.ok) {
        onUpdate(mappings)
        alert('Field mappings saved successfully!')
      } else {
        alert('Failed to save field mappings')
      }
    } catch (error) {
      console.error('Failed to save mappings:', error)
      alert('Failed to save field mappings')
    } finally {
      setSaving(false)
    }
  }

  const loadPlatformPreset = () => {
    const preset = PLATFORM_EXAMPLES[config.platform as keyof typeof PLATFORM_EXAMPLES] || PLATFORM_EXAMPLES.custom
    setMappings(preset)
  }

  const handleJsonImport = () => {
    try {
      const parsed = JSON.parse(jsonInput)
      setMappings(parsed)
      setShowJsonEditor(false)
      setJsonInput('')
    } catch (error) {
      alert('Invalid JSON format')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium">Field Mapping</h3>
          <p className="text-sm text-gray-600">
            Map your form platform's fields to FormFlow AI's expected format
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={loadPlatformPreset}
            className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
          >
            Load {config.platform} Preset
          </button>
          <button
            onClick={() => setShowJsonEditor(!showJsonEditor)}
            className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
          >
            {showJsonEditor ? 'Hide' : 'Show'} JSON Editor
          </button>
        </div>
      </div>

      {/* JSON Editor */}
      {showJsonEditor && (
        <div className="p-4 border border-gray-200 rounded-lg bg-gray-50">
          <label className="block text-sm font-medium mb-2">Import JSON Mapping</label>
          <textarea
            value={jsonInput}
            onChange={(e) => setJsonInput(e.target.value)}
            placeholder='{"form_title": "$.title", "submission_id": "$.id", ...}'
            className="w-full h-32 px-3 py-2 border border-gray-200 rounded font-mono text-sm"
          />
          <div className="flex gap-2 mt-2">
            <button
              onClick={handleJsonImport}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Import JSON
            </button>
            <button
              onClick={() => setJsonInput(JSON.stringify(mappings, null, 2))}
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              Export Current
            </button>
          </div>
        </div>
      )}

      {/* Field Mapping Form */}
      <div className="space-y-4">
        {REQUIRED_FIELDS.map((field) => (
          <div key={field.key} className="grid grid-cols-12 gap-4 items-start">
            <div className="col-span-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {field.label}
                <span className="text-red-500">*</span>
              </label>
              <p className="text-xs text-gray-500">{field.description}</p>
            </div>
            
            <div className="col-span-6">
              <input
                type="text"
                value={mappings[field.key] || ''}
                onChange={(e) => handleFieldChange(field.key, e.target.value)}
                placeholder={field.example}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg font-mono text-sm"
              />
            </div>

            <div className="col-span-2">
              <div className="text-xs text-gray-500">
                Example:<br />
                <code className="bg-gray-100 px-1 rounded">{field.example}</code>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* JSONPath Help */}
      <div className="p-4 bg-blue-50 rounded-lg">
        <h4 className="font-medium text-blue-900 mb-2">💡 JSONPath Tips</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li><code>$.field</code> - Access field at root level</li>
          <li><code>$.data.answers</code> - Access nested field</li>
          <li><code>$.items[0]</code> - Access first item in array</li>
          <li><code>$.items[*].value</code> - Access all values in array</li>
          <li><code>$.*</code> - Access all fields at root level</li>
        </ul>
      </div>

      {/* Sample Webhook Data */}
      <div className="p-4 border border-gray-200 rounded-lg">
        <h4 className="font-medium mb-2">Expected Webhook Structure for {config.platform}</h4>
        <pre className="text-xs bg-gray-50 p-3 rounded overflow-x-auto">
{config.platform === 'jotform' ? `{
  "submissionID": "123456789",
  "formTitle": "Contact Form",
  "createdAt": "2024-01-01T12:00:00Z",
  "answers": {
    "q1_name": "John Doe",
    "q2_email": "john@example.com"
  }
}` : config.platform === 'microsoft_forms' ? `{
  "id": "response_123",
  "title": "Feedback Form",
  "submitDate": "2024-01-01T12:00:00Z",
  "data": {
    "question1": "Very satisfied",
    "question2": "Great service!"
  }
}` : `{
  "id": "submission_123",
  "form_title": "Custom Form",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "name": "John Doe",
    "email": "john@example.com"
  }
}`}
        </pre>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSaveMappings}
          disabled={saving}
          className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
        >
          {saving ? 'Saving...' : 'Save Mappings'}
        </button>
      </div>
    </div>
  )
}