'use client'
import { motion } from 'framer-motion'
import { ChevronDown, HelpCircle } from 'lucide-react'
import { useState } from 'react'

const faqs = [
  {
    category: "Getting Started",
    questions: [
      {
        question: "How quickly can I set up my first dashboard?",
        answer: "You can create your first AI-powered dashboard in under 5 minutes. Simply connect your form builder (like Typeform), choose a template, and we'll handle the rest. The AI processing happens automatically when someone submits your form."
      },
      {
        question: "Do I need any technical knowledge?",
        answer: "Not at all! FormFlow AI is designed for non-technical users. Everything is point-and-click, with an intuitive interface. If you can use Google Docs, you can use FormFlow AI."
      },
      {
        question: "Which form builders do you support?",
        answer: "We support 20+ form builders including Typeform, Google Forms, JotForm, Wufoo, Airtable, and more. We're constantly adding new integrations based on user requests."
      }
    ]
  },
  {
    category: "AI & Templates",
    questions: [
      {
        question: "How accurate is the AI processing?",
        answer: "Our AI uses GPT-4 and achieves 95%+ accuracy in form analysis and content generation. The system improves over time as it learns from your specific use cases and feedback."
      },
      {
        question: "Can I customize the dashboard templates?",
        answer: "Absolutely! You can customize colors, fonts, layouts, and content. Pro users get access to custom CSS and our template builder. Enterprise users can create completely custom templates."
      },
      {
        question: "What types of forms work best?",
        answer: "FormFlow AI works with any form, but excels with surveys, lead qualification, event registration, customer feedback, health assessments, and consultation requests. The more context in responses, the better the AI output."
      }
    ]
  },
  {
    category: "Pricing & Plans",
    questions: [
      {
        question: "Is there really a free plan?",
        answer: "Yes! Our Starter plan is completely free forever with no credit card required. You get 3 forms and 100 submissions per month, plus access to basic templates. Perfect for trying out the platform."
      },
      {
        question: "Can I change plans anytime?",
        answer: "Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately, and we'll prorate any billing differences. No long-term contracts or cancellation fees."
      },
      {
        question: "What's included in the 14-day trial?",
        answer: "The free trial gives you full access to our Pro plan features: unlimited forms, all templates, custom branding, API access, and priority support. No credit card required to start."
      }
    ]
  },
  {
    category: "Security & Privacy",
    questions: [
      {
        question: "How secure is my data?",
        answer: "We're SOC 2 Type II compliant with enterprise-grade security. All data is encrypted in transit and at rest, stored on AWS with regular backups. We never sell or share your data with third parties."
      },
      {
        question: "Are you GDPR compliant?",
        answer: "Yes, we're fully GDPR compliant. We provide data processing agreements, support data portability requests, and allow users to delete their data at any time. EU data stays within EU borders."
      },
      {
        question: "Who can see my dashboards?",
        answer: "Only people with the specific dashboard link can view it. You control access completely. Pro users can password-protect dashboards and set expiration dates for additional security."
      }
    ]
  }
]

export default function FAQ() {
  const [activeCategory, setActiveCategory] = useState(0)
  const [openQuestions, setOpenQuestions] = useState<number[]>([])

  const toggleQuestion = (questionIndex: number) => {
    setOpenQuestions(prev => 
      prev.includes(questionIndex) 
        ? prev.filter(i => i !== questionIndex)
        : [...prev, questionIndex]
    )
  }

  return (
    <section id="faq" className="py-24 bg-gray-50">
      <div className="container mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="w-16 h-16 bg-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <HelpCircle className="w-8 h-8 text-purple-600" />
          </div>
          
          <h2 className="text-4xl lg:text-6xl font-bold text-gray-900 mb-6">
            Frequently Asked
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">
              Questions
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Got questions? We've got answers. If you can't find what you're looking for, 
            our support team is here to help.
          </p>
        </motion.div>

        <div className="max-w-4xl mx-auto">
          {/* Category Tabs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="flex flex-wrap justify-center gap-2 mb-12"
          >
            {faqs.map((category, index) => (
              <button
                key={category.category}
                onClick={() => {
                  setActiveCategory(index)
                  setOpenQuestions([]) // Close all questions when switching categories
                }}
                className={`px-6 py-3 rounded-full text-sm font-medium transition-all ${
                  activeCategory === index
                    ? 'bg-purple-600 text-white shadow-lg'
                    : 'bg-white text-gray-600 hover:bg-gray-100 shadow-sm'
                }`}
              >
                {category.category}
              </button>
            ))}
          </motion.div>

          {/* FAQ Content */}
          <motion.div
            key={activeCategory}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="space-y-4"
          >
            {faqs[activeCategory].questions.map((faq, questionIndex) => (
              <motion.div
                key={questionIndex}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: questionIndex * 0.1 }}
                className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden"
              >
                <button
                  onClick={() => toggleQuestion(questionIndex)}
                  className="w-full px-8 py-6 text-left flex justify-between items-start hover:bg-gray-50 transition-colors"
                >
                  <span className="font-semibold text-gray-900 pr-4">
                    {faq.question}
                  </span>
                  <ChevronDown 
                    className={`w-5 h-5 text-gray-500 flex-shrink-0 transition-transform duration-300 ${
                      openQuestions.includes(questionIndex) ? 'rotate-180' : ''
                    }`} 
                  />
                </button>
                
                <motion.div
                  initial={false}
                  animate={{ 
                    height: openQuestions.includes(questionIndex) ? 'auto' : 0,
                    opacity: openQuestions.includes(questionIndex) ? 1 : 0
                  }}
                  transition={{ duration: 0.3, ease: 'easeInOut' }}
                  className="overflow-hidden"
                >
                  <div className="px-8 pb-6">
                    <p className="text-gray-600 leading-relaxed">
                      {faq.answer}
                    </p>
                  </div>
                </motion.div>
              </motion.div>
            ))}
          </motion.div>
        </div>

        {/* Contact Support */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mt-20"
        >
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100 max-w-2xl mx-auto">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Still have questions?
            </h3>
            <p className="text-gray-600 mb-6">
              Our support team is here to help. Get in touch and we'll get back to you 
              within 24 hours (usually much faster).
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="px-6 py-3 bg-purple-600 text-white rounded-full font-medium hover:bg-purple-700 transition-colors">
                Contact Support
              </button>
              <button className="px-6 py-3 border border-gray-300 text-gray-700 rounded-full font-medium hover:bg-gray-50 transition-colors">
                Schedule Demo Call
              </button>
            </div>
            <div className="flex items-center justify-center gap-8 mt-6 pt-6 border-t border-gray-100">
              <div className="text-center">
                <div className="text-lg font-bold text-gray-900">2 min</div>
                <div className="text-sm text-gray-600">Avg. response time</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-gray-900">99%</div>
                <div className="text-sm text-gray-600">Satisfaction score</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-gray-900">24/7</div>
                <div className="text-sm text-gray-600">Availability</div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}