'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function FormsPage() {
  const router = useRouter()

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
    }
  }, [router])

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
                href="/dashboard"
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                ← Back to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Choose Your Form Platform
          </h1>
          <p className="text-xl text-gray-600">
            Connect your favorite form builder to start generating AI-powered dashboards
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Typeform Card */}
          <Link href="/forms/connect" className="group">
            <div className="bg-white rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1">
              <div className="flex items-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-r from-purple-600 to-purple-400 rounded-xl flex items-center justify-center">
                  <span className="text-2xl font-bold text-white">T</span>
                </div>
                <div className="ml-4">
                  <h2 className="text-2xl font-bold text-gray-900">Typeform</h2>
                  <span className="inline-block px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm mt-1">
                    Recommended
                  </span>
                </div>
              </div>
              
              <p className="text-gray-600 mb-6">
                Beautiful, conversational forms with powerful webhook integration. Perfect for surveys, feedback, and data collection.
              </p>
              
              <div className="space-y-2 mb-6">
                <div className="flex items-center text-sm text-gray-700">
                  <span className="text-green-500 mr-2">✓</span>
                  Real-time webhook delivery
                </div>
                <div className="flex items-center text-sm text-gray-700">
                  <span className="text-green-500 mr-2">✓</span>
                  Rich response data
                </div>
                <div className="flex items-center text-sm text-gray-700">
                  <span className="text-green-500 mr-2">✓</span>
                  Easy setup process
                </div>
              </div>
              
              <div className="inline-flex items-center text-purple-600 group-hover:text-purple-700 font-semibold">
                Connect Typeform
                <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </Link>

          {/* Google Forms Card */}
          <Link href="/forms/google" className="group">
            <div className="bg-white rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1">
              <div className="flex items-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-blue-400 rounded-xl flex items-center justify-center">
                  <span className="text-2xl font-bold text-white">G</span>
                </div>
                <div className="ml-4">
                  <h2 className="text-2xl font-bold text-gray-900">Google Forms</h2>
                  <span className="inline-block px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm mt-1">
                    Free
                  </span>
                </div>
              </div>
              
              <p className="text-gray-600 mb-6">
                Free and familiar forms integrated with Google Workspace. Great for teams already using Google tools.
              </p>
              
              <div className="space-y-2 mb-6">
                <div className="flex items-center text-sm text-gray-700">
                  <span className="text-green-500 mr-2">✓</span>
                  Completely free to use
                </div>
                <div className="flex items-center text-sm text-gray-700">
                  <span className="text-green-500 mr-2">✓</span>
                  Google Workspace integration
                </div>
                <div className="flex items-center text-sm text-gray-700">
                  <span className="text-green-500 mr-2">✓</span>
                  Apps Script automation
                </div>
              </div>
              
              <div className="inline-flex items-center text-blue-600 group-hover:text-blue-700 font-semibold">
                Connect Google Forms
                <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </Link>
        </div>

        {/* Coming Soon Section */}
        <div className="mt-12 bg-white/60 backdrop-blur-sm rounded-2xl p-8">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Coming Soon</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4">
              <div className="w-12 h-12 bg-gray-200 rounded-lg mx-auto mb-2"></div>
              <span className="text-sm text-gray-500">Jotform</span>
            </div>
            <div className="text-center p-4">
              <div className="w-12 h-12 bg-gray-200 rounded-lg mx-auto mb-2"></div>
              <span className="text-sm text-gray-500">Microsoft Forms</span>
            </div>
            <div className="text-center p-4">
              <div className="w-12 h-12 bg-gray-200 rounded-lg mx-auto mb-2"></div>
              <span className="text-sm text-gray-500">SurveyMonkey</span>
            </div>
            <div className="text-center p-4">
              <div className="w-12 h-12 bg-gray-200 rounded-lg mx-auto mb-2"></div>
              <span className="text-sm text-gray-500">Airtable Forms</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}