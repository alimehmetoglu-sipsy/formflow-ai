'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function GoogleFormsConnectPage() {
  const router = useRouter()
  const [webhookUrl, setWebhookUrl] = useState('')
  const [scriptContent, setScriptContent] = useState('')
  const [copied, setCopied] = useState(false)
  const [copiedScript, setCopiedScript] = useState(false)
  const [user, setUser] = useState<any>(null)
  const [activeTab, setActiveTab] = useState<'webhook' | 'script'>('webhook')

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
      const baseUrl = window.location.origin.replace('3000', '8000')
      const googleWebhookUrl = `${baseUrl}/api/v1/webhooks/google-forms?user_id=${parsedUser.id}`
      setWebhookUrl(googleWebhookUrl)
      
      // Generate Google Apps Script content
      const script = generateGoogleAppsScript(googleWebhookUrl)
      setScriptContent(script)
    }
  }, [router])

  const generateGoogleAppsScript = (webhookUrl: string) => {
    return `// FormFlow AI - Google Forms Integration Script
// This script sends form responses to FormFlow AI for dashboard generation

function onFormSubmit(e) {
  // Get form and response details
  var form = FormApp.getActiveForm();
  var formId = form.getId();
  var formTitle = form.getTitle();
  var response = e.response;
  
  // Get all answers
  var itemResponses = response.getItemResponses();
  var answers = {};
  
  for (var i = 0; i < itemResponses.length; i++) {
    var itemResponse = itemResponses[i];
    var question = itemResponse.getItem().getTitle();
    var answer = itemResponse.getResponse();
    
    // Create a safe key for the question
    var questionKey = 'q_' + (i + 1) + '_' + question.substring(0, 50).replace(/[^a-zA-Z0-9]/g, '_');
    
    // Handle different response types
    if (Array.isArray(answer)) {
      answers[questionKey] = { choiceAnswers: { answers: answer.map(a => ({ value: a })) } };
    } else {
      answers[questionKey] = { textAnswers: { answers: [{ value: String(answer) }] } };
    }
  }
  
  // Prepare webhook payload
  var payload = {
    formId: formId,
    formTitle: formTitle,
    response: {
      responseId: response.getId(),
      createTime: new Date().toISOString(),
      lastSubmittedTime: response.getTimestamp().toISOString(),
      answers: answers
    },
    eventType: 'form_response'
  };
  
  // Send to FormFlow AI
  var options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(payload),
    'muteHttpExceptions': true
  };
  
  try {
    var response = UrlFetchApp.fetch('${webhookUrl}', options);
    console.log('FormFlow AI Response:', response.getContentText());
  } catch (error) {
    console.error('Error sending to FormFlow AI:', error);
  }
}

// Setup function - Run this once to install the trigger
function setupFormTrigger() {
  var form = FormApp.getActiveForm();
  ScriptApp.newTrigger('onFormSubmit')
    .forForm(form)
    .onFormSubmit()
    .create();
  
  SpreadsheetApp.getUi().alert('✅ FormFlow AI integration installed successfully!');
}`
  }

  const copyToClipboard = (text: string, type: 'url' | 'script') => {
    navigator.clipboard.writeText(text)
    if (type === 'url') {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } else {
      setCopiedScript(true)
      setTimeout(() => setCopiedScript(false), 2000)
    }
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
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
              <svg className="w-7 h-7 text-blue-600" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 3h5v2h-5V6zm0 3h5v2h-5V9zm-5 5h5v2H7v-2zm0-3h5v2H7v-2zm0-3h5v2H7V6zm10 8h-5v-2h5v2z"/>
              </svg>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Connect Google Forms</h1>
              <p className="text-gray-600">
                Choose your preferred integration method
              </p>
            </div>
          </div>

          {/* Tab Buttons */}
          <div className="flex gap-2 mb-8 mt-8">
            <button
              onClick={() => setActiveTab('script')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                activeTab === 'script'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Apps Script (Recommended)
            </button>
            <button
              onClick={() => setActiveTab('webhook')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                activeTab === 'webhook'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Direct Webhook
            </button>
          </div>

          {/* Script Method */}
          {activeTab === 'script' && (
            <div className="space-y-6">
              <div className="bg-green-50 rounded-lg p-4 mb-6">
                <div className="flex items-start gap-3">
                  <span className="text-green-600 text-xl">✨</span>
                  <div>
                    <p className="font-semibold text-green-900">Recommended Method</p>
                    <p className="text-green-700 text-sm">
                      Automatic integration using Google Apps Script - works with all Google Forms features
                    </p>
                  </div>
                </div>
              </div>

              {/* Step 1 */}
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-blue-600 font-semibold">1</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-2">Open Your Google Form</h3>
                  <p className="text-gray-600 mb-3">
                    Navigate to your Google Form and click the three dots menu → Script editor
                  </p>
                  <a
                    href="https://docs.google.com/forms"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-blue-600 hover:text-blue-700"
                  >
                    Go to Google Forms →
                  </a>
                </div>
              </div>

              {/* Step 2 */}
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                  <span className="text-purple-600 font-semibold">2</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-2">Copy & Paste the Script</h3>
                  <div className="bg-gray-50 rounded-lg p-4 mb-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-600">Google Apps Script</span>
                      <button
                        onClick={() => copyToClipboard(scriptContent, 'script')}
                        className="px-3 py-1 text-sm bg-purple-600 text-white rounded hover:bg-purple-700 transition-colors"
                      >
                        {copiedScript ? '✓ Copied!' : 'Copy Script'}
                      </button>
                    </div>
                    <pre className="text-xs text-gray-700 overflow-x-auto max-h-48 overflow-y-auto">
                      <code>{scriptContent.split('\n').slice(0, 15).join('\n')}...</code>
                    </pre>
                  </div>
                  <p className="text-sm text-gray-600">
                    Replace all existing code in the Script Editor with this script
                  </p>
                </div>
              </div>

              {/* Step 3 */}
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-10 h-10 bg-pink-100 rounded-full flex items-center justify-center">
                  <span className="text-pink-600 font-semibold">3</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-2">Run Setup Function</h3>
                  <ol className="list-decimal list-inside space-y-1 text-gray-600 text-sm">
                    <li>Save the script (Ctrl+S or Cmd+S)</li>
                    <li>Click "Run" → Select "setupFormTrigger"</li>
                    <li>Grant necessary permissions when prompted</li>
                    <li>You'll see a success message when complete</li>
                  </ol>
                </div>
              </div>

              {/* Step 4 */}
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <span className="text-green-600 font-semibold">✓</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-2">All Set!</h3>
                  <p className="text-gray-600 mb-4">
                    Your Google Form now automatically sends responses to FormFlow AI
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Webhook Method */}
          {activeTab === 'webhook' && (
            <div className="space-y-6">
              <div className="bg-yellow-50 rounded-lg p-4 mb-6">
                <div className="flex items-start gap-3">
                  <span className="text-yellow-600 text-xl">⚠️</span>
                  <div>
                    <p className="font-semibold text-yellow-900">Advanced Method</p>
                    <p className="text-yellow-700 text-sm">
                      Requires manual API calls or third-party integration tools like Zapier
                    </p>
                  </div>
                </div>
              </div>

              {/* Webhook URL */}
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-blue-600 font-semibold">1</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-2">Your Google Forms Webhook URL</h3>
                  <div className="bg-gray-50 rounded-lg p-4 mb-3">
                    <div className="flex items-center gap-2">
                      <input
                        type="text"
                        value={webhookUrl}
                        readOnly
                        className="flex-1 bg-white border border-gray-200 rounded px-3 py-2 text-sm font-mono text-gray-700"
                      />
                      <button
                        onClick={() => copyToClipboard(webhookUrl, 'url')}
                        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                      >
                        {copied ? '✓ Copied!' : 'Copy'}
                      </button>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600">
                    Use this URL when setting up webhook integrations with Google Forms
                  </p>
                </div>
              </div>

              {/* Integration Options */}
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                  <span className="text-purple-600 font-semibold">2</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-2">Integration Options</h3>
                  <div className="space-y-3">
                    <div className="border rounded-lg p-3">
                      <h4 className="font-medium text-gray-800">Option A: Zapier</h4>
                      <p className="text-sm text-gray-600">
                        Create a Zap that triggers on new Google Form responses and sends to webhook URL
                      </p>
                    </div>
                    <div className="border rounded-lg p-3">
                      <h4 className="font-medium text-gray-800">Option B: Make (Integromat)</h4>
                      <p className="text-sm text-gray-600">
                        Set up a scenario to watch Google Forms and POST to the webhook
                      </p>
                    </div>
                    <div className="border rounded-lg p-3">
                      <h4 className="font-medium text-gray-800">Option C: Custom Script</h4>
                      <p className="text-sm text-gray-600">
                        Use the Apps Script method above for the easiest integration
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Additional Info */}
          <div className="mt-12 p-6 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-2 flex items-center">
              <span className="text-2xl mr-2">💡</span>
              Google Forms Integration Benefits
            </h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li>• Works with all Google Forms question types</li>
              <li>• Automatic response processing with AI</li>
              <li>• No coding required with Apps Script method</li>
              <li>• Real-time dashboard generation</li>
              <li>• Supports file uploads and multi-page forms</li>
            </ul>
          </div>

          {/* Navigation Buttons */}
          <div className="mt-8 flex gap-4">
            <Link
              href="/dashboard"
              className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all duration-200"
            >
              View Your Dashboards
            </Link>
            <Link
              href="/forms/connect"
              className="inline-flex items-center px-6 py-3 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 transition-all duration-200"
            >
              Connect Typeform Instead
            </Link>
          </div>
        </div>
      </main>
    </div>
  )
}