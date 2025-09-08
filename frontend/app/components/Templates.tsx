'use client'
import { motion } from 'framer-motion'
import { useState } from 'react'
import { ChevronLeft, ChevronRight, ExternalLink } from 'lucide-react'

const templates = [
  {
    id: 1,
    name: "Diet & Nutrition Plan",
    category: "Health & Fitness",
    description: "Transform nutrition surveys into personalized meal plans with calorie tracking, shopping lists, and dietary recommendations.",
    features: ["7-day meal plans", "Calorie breakdown", "Shopping lists", "Dietary restrictions"],
    color: "from-green-500 to-emerald-600",
    preview: {
      title: "Personal Diet Plan",
      stats: [
        { label: "Daily Calories", value: "1,800", color: "bg-green-100 text-green-800" },
        { label: "Protein", value: "135g", color: "bg-blue-100 text-blue-800" },
        { label: "Meals", value: "21", color: "bg-purple-100 text-purple-800" }
      ]
    }
  },
  {
    id: 2,
    name: "Lead Scoring Dashboard",
    category: "Sales & Marketing",
    description: "Convert lead qualification forms into intelligent scoring dashboards with actionable insights and follow-up recommendations.",
    features: ["Lead scoring", "Priority ranking", "Follow-up actions", "Conversion tracking"],
    color: "from-blue-500 to-cyan-600",
    preview: {
      title: "Lead Analysis Report",
      stats: [
        { label: "Lead Score", value: "85/100", color: "bg-green-100 text-green-800" },
        { label: "Priority", value: "High", color: "bg-red-100 text-red-800" },
        { label: "Est. Value", value: "$45K", color: "bg-yellow-100 text-yellow-800" }
      ]
    }
  },
  {
    id: 3,
    name: "Event Registration",
    category: "Events & Conferences",
    description: "Turn event sign-ups into beautiful confirmation pages with QR codes, calendar integration, and attendee management.",
    features: ["QR code tickets", "Calendar sync", "Attendee profiles", "Check-in system"],
    color: "from-purple-500 to-pink-600",
    preview: {
      title: "Event Confirmation",
      stats: [
        { label: "Ticket #", value: "FF-2025", color: "bg-purple-100 text-purple-800" },
        { label: "Date", value: "Feb 15", color: "bg-blue-100 text-blue-800" },
        { label: "Status", value: "Confirmed", color: "bg-green-100 text-green-800" }
      ]
    }
  },
  {
    id: 4,
    name: "Customer Feedback",
    category: "Customer Success",
    description: "Transform feedback forms into actionable insights with sentiment analysis, priority ranking, and response tracking.",
    features: ["Sentiment analysis", "Issue categorization", "Response templates", "Follow-up automation"],
    color: "from-orange-500 to-red-500",
    preview: {
      title: "Feedback Analysis",
      stats: [
        { label: "Satisfaction", value: "4.2/5", color: "bg-green-100 text-green-800" },
        { label: "Issues", value: "2 Found", color: "bg-orange-100 text-orange-800" },
        { label: "Priority", value: "Medium", color: "bg-yellow-100 text-yellow-800" }
      ]
    }
  }
]

export default function Templates() {
  const [activeTemplate, setActiveTemplate] = useState(0)
  const [currentCategory, setCurrentCategory] = useState("All")
  
  const categories = ["All", "Health & Fitness", "Sales & Marketing", "Events & Conferences", "Customer Success"]
  
  const filteredTemplates = currentCategory === "All" 
    ? templates 
    : templates.filter(t => t.category === currentCategory)

  return (
    <section className="py-24 bg-white">
      <div className="container mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl lg:text-6xl font-bold text-gray-900 mb-6">
            Templates That
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">
              Convert Like Crazy
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Choose from our library of high-converting templates, each optimized for specific industries and use cases.
          </p>
          
          {/* Category Filter */}
          <div className="flex flex-wrap justify-center gap-3">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setCurrentCategory(category)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                  currentCategory === category
                    ? 'bg-purple-600 text-white shadow-lg'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Templates Showcase */}
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Template List */}
            <div className="space-y-4">
              {filteredTemplates.map((template, index) => (
                <motion.div
                  key={template.id}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className={`p-6 rounded-2xl cursor-pointer transition-all duration-300 ${
                    activeTemplate === index
                      ? 'bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200 shadow-lg'
                      : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                  }`}
                  onClick={() => setActiveTemplate(index)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="text-lg font-bold text-gray-900">{template.name}</h3>
                      <span className="text-sm text-purple-600 font-medium">{template.category}</span>
                    </div>
                    <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${template.color}`}></div>
                  </div>
                  
                  <p className="text-gray-600 mb-4">{template.description}</p>
                  
                  <div className="flex flex-wrap gap-2">
                    {template.features.map((feature) => (
                      <span
                        key={feature}
                        className="px-3 py-1 bg-white rounded-full text-sm text-gray-600 border border-gray-200"
                      >
                        {feature}
                      </span>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Template Preview */}
            <motion.div
              key={activeTemplate}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              className="bg-white rounded-2xl shadow-2xl overflow-hidden border border-gray-100"
            >
              {/* Preview Header */}
              <div className={`h-2 bg-gradient-to-r ${filteredTemplates[activeTemplate]?.color}`}></div>
              
              <div className="p-8">
                {/* Mock Dashboard */}
                <div className="mb-6">
                  <div className="flex items-center gap-3 mb-6">
                    <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${filteredTemplates[activeTemplate]?.color} flex items-center justify-center`}>
                      <span className="text-white font-bold">📊</span>
                    </div>
                    <div>
                      <h4 className="font-bold text-gray-900">{filteredTemplates[activeTemplate]?.preview.title}</h4>
                      <p className="text-sm text-gray-500">Generated in 45 seconds</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-3 mb-6">
                    {filteredTemplates[activeTemplate]?.preview.stats.map((stat, idx) => (
                      <div key={idx} className="bg-gray-50 p-3 rounded-lg text-center">
                        <div className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${stat.color} mb-1`}>
                          {stat.value}
                        </div>
                        <div className="text-xs text-gray-600">{stat.label}</div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="space-y-2">
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full" style={{width: '75%'}}></div>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full" style={{width: '60%'}}></div>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-green-500 to-emerald-500 rounded-full" style={{width: '90%'}}></div>
                    </div>
                  </div>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">Live Preview</span>
                  <button className="flex items-center gap-2 text-purple-600 hover:text-purple-700 font-medium text-sm">
                    View Full Dashboard
                    <ExternalLink className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mt-20"
        >
          <p className="text-gray-600 mb-6">
            Can't find what you need? We create custom templates for enterprise clients.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="px-8 py-3 bg-purple-600 text-white rounded-full font-semibold hover:bg-purple-700 transition-colors">
              Browse All Templates
            </button>
            <button className="px-8 py-3 border border-gray-300 text-gray-700 rounded-full font-semibold hover:bg-gray-50 transition-colors">
              Request Custom Template
            </button>
          </div>
        </motion.div>
      </div>
    </section>
  )
}