'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function ConnectFormsPage() {
  const router = useRouter()
  const [webhookUrl, setWebhookUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)
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
      const parsedUser = JSON.parse(userData)
      setUser(parsedUser)
      // Generate webhook URL with user ID
      setWebhookUrl(`${window.location.origin.replace('3000', '8000')}/api/v1/webhooks/typeform?user_id=${parsedUser.id}`)
    }
  }, [router])

  const copyToClipboard = () => {
    navigator.clipboard.writeText(webhookUrl)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
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
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Connect Your Typeform</h1>
          <p className="text-gray-600 mb-8">
            Follow these steps to connect your Typeform and start generating AI-powered dashboards
          </p>

          {/* Steps */}
          <div className="space-y-6">
            {/* Step 1 */}
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                <span className="text-purple-600 font-semibold">1</span>
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-2">Copy Your Webhook URL</h3>
                <div className="bg-gray-50 rounded-lg p-4 mb-3">
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      value={webhookUrl}
                      readOnly
                      className="flex-1 bg-white border border-gray-200 rounded px-3 py-2 text-sm font-mono text-gray-700"
                    />
                    <button
                      onClick={copyToClipboard}
                      className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 transition-colors"
                    >
                      {copied ? '✓ Copied!' : 'Copy'}
                    </button>
                  </div>
                </div>
                <p className="text-sm text-gray-600">
                  This unique URL includes your user ID to associate submissions with your account
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-10 h-10 bg-pink-100 rounded-full flex items-center justify-center">
                <span className="text-pink-600 font-semibold">2</span>
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-2">Open Your Typeform</h3>
                <p className="text-gray-600 mb-3">
                  Log in to your Typeform account and open the form you want to connect
                </p>
                <a
                  href="https://admin.typeform.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-purple-600 hover:text-purple-700"
                >
                  Go to Typeform →
                </a>
              </div>
            </div>

            {/* Step 3 */}
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <span className="text-red-600 font-semibold">3</span>
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-2">Configure Webhook</h3>
                <ol className="list-decimal list-inside space-y-2 text-gray-600 mb-3">
                  <li>Navigate to <strong>Connect → Webhooks</strong> in your form settings</li>
                  <li>Click <strong>Add a webhook</strong></li>
                  <li>Paste the webhook URL from Step 1</li>
                  <li>Test the connection (optional)</li>
                  <li>Toggle the webhook to <strong>ON</strong></li>
                </ol>
              </div>
            </div>

            {/* Step 4 */}
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 font-semibold">✓</span>
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-2">You're All Set!</h3>
                <p className="text-gray-600 mb-4">
                  New form submissions will automatically generate AI-powered dashboards
                </p>
                <Link
                  href="/dashboard"
                  className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all duration-200"
                >
                  View Your Dashboards
                </Link>
              </div>
            </div>
          </div>

          {/* Additional Info */}
          <div className="mt-12 p-6 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-2 flex items-center">
              <span className="text-2xl mr-2">💡</span>
              Pro Tips
            </h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li>• Each form submission creates a unique dashboard</li>
              <li>• Dashboards are generated using AI based on your form responses</li>
              <li>• You can connect multiple forms using the same webhook URL</li>
              <li>• Dashboard templates are automatically selected based on form content</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  )
}