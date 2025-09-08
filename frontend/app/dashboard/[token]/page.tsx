'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'

export default function DashboardViewPage() {
  const params = useParams()
  const router = useRouter()
  const token = params.token as string
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [dashboardHtml, setDashboardHtml] = useState<string>('')

  useEffect(() => {
    if (!token) {
      setError('Invalid dashboard token')
      setLoading(false)
      return
    }

    fetchDashboard()
  }, [token])

  const fetchDashboard = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/dashboards/view/${token}`)
      
      if (!response.ok) {
        if (response.status === 404) {
          setError('Dashboard not found')
        } else {
          setError('Failed to load dashboard')
        }
        setLoading(false)
        return
      }

      const html = await response.text()
      setDashboardHtml(html)
    } catch (err) {
      console.error('Error fetching dashboard:', err)
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">Loading Dashboard</h1>
          <p className="text-gray-600">Please wait while we fetch your dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">❌</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">Dashboard Error</h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <Link
            href="/dashboard"
            className="inline-flex items-center px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  // Render the dashboard HTML in an iframe for isolation
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center gap-4">
              <Link
                href="/dashboard"
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                ← Back to Dashboards
              </Link>
              <span className="text-gray-400">|</span>
              <span className="text-sm text-gray-600">
                Dashboard Token: <code className="bg-gray-100 px-2 py-1 rounded">{token}</code>
              </span>
            </div>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>
      
      <div className="w-full h-[calc(100vh-73px)]">
        <iframe
          srcDoc={dashboardHtml}
          className="w-full h-full border-0"
          title="Dashboard Content"
          sandbox="allow-scripts allow-same-origin"
        />
      </div>
    </div>
  )
}