'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

interface Dashboard {
  id: string
  token?: string
  template_type?: string
  type?: string  // Backward compatibility
  created_at: string
  view_count: number
  dashboard_url?: string
}

export default function DashboardPage() {
  const router = useRouter()
  const [dashboards, setDashboards] = useState<Dashboard[]>([])
  const [loading, setLoading] = useState(true)
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token')
    const userData = localStorage.getItem('user')
    
    if (!token) {
      router.push('/login')
      return
    }

    if (userData) {
      setUser(JSON.parse(userData))
    }

    // Fetch dashboards
    fetchDashboards(token)
  }, [router])

  const fetchDashboards = async (token: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/dashboards/user/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setDashboards(data)
      } else if (response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        router.push('/login')
      }
    } catch (error) {
      console.error('Failed to fetch dashboards:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/')
  }

  const getDashboardIcon = (type?: string) => {
    if (!type) return '📄'
    const icons: { [key: string]: string } = {
      'diet_plan': '🥗',
      'lead_score': '📊',
      'event_plan': '📅',
      'survey_analysis': '📈',
      'feedback_summary': '💬',
    }
    return icons[type] || '📄'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
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
              <span className="text-sm text-gray-600">
                Welcome, {user?.name || 'User'}
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Your Dashboards</h1>
          <p className="text-gray-600">View and manage your AI-generated dashboards</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Dashboards</p>
                <p className="text-3xl font-bold text-gray-900">{dashboards.length}</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <span className="text-2xl">📊</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Views</p>
                <p className="text-3xl font-bold text-gray-900">
                  {dashboards.reduce((acc, d) => acc + d.view_count, 0)}
                </p>
              </div>
              <div className="w-12 h-12 bg-pink-100 rounded-lg flex items-center justify-center">
                <span className="text-2xl">👁️</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Forms</p>
                <p className="text-3xl font-bold text-gray-900">5</p>
              </div>
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <span className="text-2xl">📝</span>
              </div>
            </div>
          </div>
        </div>

        {/* Dashboards Grid */}
        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
          </div>
        ) : dashboards.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {dashboards.map((dashboard) => (
              <div
                key={dashboard.id}
                className="bg-white rounded-xl p-6 shadow-sm hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-100 to-pink-100 rounded-lg flex items-center justify-center">
                    <span className="text-2xl">{getDashboardIcon(dashboard.template_type || dashboard.type)}</span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {dashboard.view_count} views
                  </span>
                </div>
                
                <h3 className="font-semibold text-gray-900 mb-1 capitalize">
                  {(dashboard.template_type || dashboard.type || 'Dashboard').replace('_', ' ')}
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Created {formatDate(dashboard.created_at)}
                </p>
                
                <div className="flex items-center justify-between">
                  <Link 
                    href={`/dashboard/${dashboard.token || dashboard.id}`}
                    className="text-sm font-medium text-purple-600 hover:text-purple-700"
                    onClick={(e) => e.stopPropagation()}
                  >
                    View Dashboard →
                  </Link>
                  <button className="text-sm text-gray-400 hover:text-gray-600">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-20">
            <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-4xl">📭</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No dashboards yet</h3>
            <p className="text-gray-600 mb-6">
              Connect your forms to start generating AI-powered dashboards
            </p>
            <Link
              href="/forms"
              className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all duration-200"
            >
              Connect Your First Form
            </Link>
          </div>
        )}
      </main>
    </div>
  )
}