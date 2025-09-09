'use client'

import { useState, useEffect } from 'react'

interface WebhookConfig {
  id: string
  name: string
  platform: string
  [key: string]: any
}

interface WebhookLog {
  id: string
  status: string
  request_body: Record<string, any> | null
  response_body: Record<string, any> | null
  error_message: string | null
  ip_address: string | null
  created_at: string
}

interface WebhookLogsProps {
  config: WebhookConfig
}

export default function WebhookLogs({ config }: WebhookLogsProps) {
  const [logs, setLogs] = useState<WebhookLog[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedLog, setSelectedLog] = useState<WebhookLog | null>(null)
  const [showDetails, setShowDetails] = useState(false)

  useEffect(() => {
    fetchLogs()
  }, [config.id])

  const fetchLogs = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(
        `http://localhost:8000/api/v1/webhooks/configs/${config.id}/logs?limit=20`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        const fetchedLogs = await response.json()
        setLogs(fetchedLogs)
      }
    } catch (error) {
      console.error('Failed to fetch webhook logs:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString()
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'bg-green-100 text-green-800'
      case 'error':
        return 'bg-red-100 text-red-800'
      case 'processing':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return '✅'
      case 'error':
        return '❌'
      case 'processing':
        return '⏳'
      default:
        return '❓'
    }
  }

  const truncateJson = (obj: any, maxLength = 100) => {
    if (!obj) return 'N/A'
    const str = JSON.stringify(obj)
    return str.length > maxLength ? str.substring(0, maxLength) + '...' : str
  }

  const clearLogs = async () => {
    if (!confirm('Are you sure you want to clear all logs for this webhook?')) {
      return
    }

    try {
      const token = localStorage.getItem('token')
      // Note: This endpoint would need to be implemented in the backend
      const response = await fetch(
        `http://localhost:8000/api/v1/webhooks/configs/${config.id}/logs`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        setLogs([])
        alert('Logs cleared successfully')
      } else {
        alert('Failed to clear logs')
      }
    } catch (error) {
      console.error('Failed to clear logs:', error)
      alert('Failed to clear logs')
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium">Webhook Logs</h3>
          <p className="text-sm text-gray-600">
            Recent webhook requests and their processing results
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={fetchLogs}
            className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
          >
            🔄 Refresh
          </button>
          {logs.length > 0 && (
            <button
              onClick={clearLogs}
              className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200"
            >
              🗑️ Clear Logs
            </button>
          )}
        </div>
      </div>

      {logs.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">📜</span>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Logs Yet</h3>
          <p className="text-gray-600">
            Webhook requests will appear here once you start receiving data
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {logs.map((log) => (
            <div
              key={log.id}
              className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <span className="text-lg">{getStatusIcon(log.status)}</span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(log.status)}`}>
                    {log.status.toUpperCase()}
                  </span>
                  <span className="text-sm text-gray-500">
                    {formatTimestamp(log.created_at)}
                  </span>
                  {log.ip_address && (
                    <span className="text-xs text-gray-400">
                      from {log.ip_address}
                    </span>
                  )}
                </div>
                <button
                  onClick={() => {
                    setSelectedLog(log)
                    setShowDetails(true)
                  }}
                  className="text-sm text-purple-600 hover:text-purple-700"
                >
                  View Details
                </button>
              </div>

              {log.error_message && (
                <div className="mb-2">
                  <p className="text-sm text-red-600">
                    <strong>Error:</strong> {log.error_message}
                  </p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Request:</span>
                  <div className="font-mono text-xs bg-gray-100 p-2 rounded mt-1">
                    {truncateJson(log.request_body)}
                  </div>
                </div>
                <div>
                  <span className="text-gray-600">Response:</span>
                  <div className="font-mono text-xs bg-gray-100 p-2 rounded mt-1">
                    {truncateJson(log.response_body)}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Log Details Modal */}
      {showDetails && selectedLog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] w-full mx-4 overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h3 className="text-lg font-medium">
                Webhook Log Details - {formatTimestamp(selectedLog.created_at)}
              </h3>
              <button
                onClick={() => setShowDetails(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
              <div className="space-y-6">
                {/* Status and Metadata */}
                <div>
                  <h4 className="font-medium mb-3">Status Information</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Status:</span>
                      <span className={`ml-2 px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(selectedLog.status)}`}>
                        {selectedLog.status.toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">IP Address:</span>
                      <span className="ml-2">{selectedLog.ip_address || 'Unknown'}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Timestamp:</span>
                      <span className="ml-2">{formatTimestamp(selectedLog.created_at)}</span>
                    </div>
                  </div>
                </div>

                {/* Error Message */}
                {selectedLog.error_message && (
                  <div>
                    <h4 className="font-medium mb-2 text-red-600">Error Message</h4>
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                      <p className="text-sm text-red-700">{selectedLog.error_message}</p>
                    </div>
                  </div>
                )}

                {/* Request Body */}
                <div>
                  <h4 className="font-medium mb-2">Request Body</h4>
                  <pre className="text-xs bg-gray-50 p-4 rounded-lg border overflow-x-auto">
                    {selectedLog.request_body 
                      ? JSON.stringify(selectedLog.request_body, null, 2)
                      : 'No request body'
                    }
                  </pre>
                </div>

                {/* Response Body */}
                <div>
                  <h4 className="font-medium mb-2">Response Body</h4>
                  <pre className="text-xs bg-gray-50 p-4 rounded-lg border overflow-x-auto">
                    {selectedLog.response_body 
                      ? JSON.stringify(selectedLog.response_body, null, 2)
                      : 'No response body'
                    }
                  </pre>
                </div>
              </div>
            </div>

            <div className="flex justify-end p-6 border-t border-gray-200">
              <button
                onClick={() => setShowDetails(false)}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}