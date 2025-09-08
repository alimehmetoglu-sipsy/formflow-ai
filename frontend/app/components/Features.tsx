'use client'
import { motion } from 'framer-motion'
import { Bot, Zap, Palette, Link, BarChart3, Shield } from 'lucide-react'

const features = [
  {
    icon: Bot,
    title: "AI-Powered Processing",
    description: "GPT-4 analyzes form responses and generates intelligent insights automatically. From diet plans to lead scoring, our AI understands context.",
    color: "from-purple-500 to-purple-600"
  },
  {
    icon: Zap,
    title: "Instant Dashboards",
    description: "Beautiful dashboards generated in under 60 seconds after form submission. Your clients see results immediately, not tomorrow.",
    color: "from-yellow-500 to-orange-500"
  },
  {
    icon: Palette,
    title: "Customizable Templates",
    description: "Choose from 50+ pre-built templates or create your own. Every dashboard is pixel-perfect and mobile-responsive.",
    color: "from-pink-500 to-rose-500"
  },
  {
    icon: Link,
    title: "Universal Integration",
    description: "Works seamlessly with Typeform, Google Forms, Airtable, and 20+ other form builders. One-click connection.",
    color: "from-blue-500 to-cyan-500"
  },
  {
    icon: BarChart3,
    title: "Advanced Analytics",
    description: "Track views, engagement, conversion rates, and user behavior. Optimize your forms with data-driven insights.",
    color: "from-green-500 to-emerald-500"
  },
  {
    icon: Shield,
    title: "Enterprise Security",
    description: "SOC 2 Type II compliant with end-to-end encryption, GDPR compliance, and enterprise-grade security controls.",
    color: "from-gray-700 to-gray-800"
  }
]

export default function Features() {
  return (
    <section id="features" className="py-24 bg-gray-50">
      <div className="container mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <h2 className="text-4xl lg:text-6xl font-bold text-gray-900 mb-6">
            Everything You Need to
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">
              Wow Your Clients
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Stop sending boring form confirmations. Create intelligent, beautiful dashboards 
            that turn every form submission into a memorable experience.
          </p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="group"
              >
                <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 border border-gray-100">
                  {/* Icon */}
                  <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                  
                  {/* Content */}
                  <h3 className="text-xl font-bold text-gray-900 mb-4">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {feature.description}
                  </p>
                  
                  {/* Hover indicator */}
                  <div className="mt-6 flex items-center text-purple-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <span className="text-sm font-medium">Learn more</span>
                    <svg className="w-4 h-4 ml-2 transform group-hover:translate-x-1 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                    </svg>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mt-20"
        >
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl p-8 text-white">
            <h3 className="text-2xl font-bold mb-4">
              Ready to transform your forms?
            </h3>
            <p className="text-lg opacity-90 mb-6">
              Join 2,500+ businesses creating amazing form experiences
            </p>
            <button className="px-8 py-4 bg-white text-purple-600 rounded-full font-semibold text-lg hover:bg-gray-50 transition-colors shadow-lg hover:shadow-xl">
              Start Your Free Trial →
            </button>
          </div>
        </motion.div>
      </div>
    </section>
  )
}