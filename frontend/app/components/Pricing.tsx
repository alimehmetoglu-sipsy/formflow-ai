'use client'
import { motion } from 'framer-motion'
import { Check, Star, ArrowRight } from 'lucide-react'
import { useState } from 'react'

const plans = [
  {
    name: "Starter",
    subtitle: "Perfect for individuals",
    price: "$0",
    period: "forever",
    originalPrice: null,
    features: [
      "3 forms per month",
      "100 submissions/month",
      "5 basic templates",
      "Email support",
      "FormFlow branding",
      "Basic analytics"
    ],
    cta: "Start Free",
    popular: false,
    color: "border-gray-200"
  },
  {
    name: "Pro",
    subtitle: "Most popular choice",
    price: "$17",
    period: "per month",
    originalPrice: "$34",
    features: [
      "Unlimited forms",
      "1,000 submissions/month", 
      "All 50+ templates",
      "Custom branding",
      "Priority support",
      "API access",
      "Advanced analytics",
      "White-label option",
      "Custom domain"
    ],
    cta: "Start 14-Day Trial",
    popular: true,
    color: "border-purple-500"
  },
  {
    name: "Business",
    subtitle: "For growing companies",
    price: "$47",
    period: "per month",
    originalPrice: "$94",
    features: [
      "Everything in Pro",
      "10,000 submissions/month",
      "Custom templates",
      "Dedicated support manager",
      "SLA guarantee (99.9%)",
      "Single Sign-On (SSO)",
      "Advanced integrations",
      "Team collaboration",
      "Custom training session"
    ],
    cta: "Contact Sales",
    popular: false,
    color: "border-gray-200"
  }
]

const faqs = [
  {
    question: "Can I cancel my subscription anytime?",
    answer: "Yes, you can cancel your subscription at any time. No long-term contracts or cancellation fees."
  },
  {
    question: "What happens to my data if I cancel?",
    answer: "Your data is securely stored for 30 days after cancellation, giving you time to export or reactivate."
  },
  {
    question: "Do you offer refunds?",
    answer: "We offer a 30-day money-back guarantee for all paid plans. No questions asked."
  }
]

export default function Pricing() {
  const [isAnnual, setIsAnnual] = useState(false)
  const [openFaq, setOpenFaq] = useState<number | null>(null)

  return (
    <section id="pricing" className="py-24 bg-gradient-to-br from-gray-50 to-white">
      <div className="container mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center px-4 py-2 bg-green-100 text-green-800 rounded-full mb-6">
            <Star className="w-4 h-4 mr-2" />
            <span className="text-sm font-medium">Launch Special: 50% OFF</span>
          </div>
          
          <h2 className="text-4xl lg:text-6xl font-bold text-gray-900 mb-6">
            Simple, Transparent
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">
              Pricing
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Start free, upgrade when you're ready. No hidden fees, no surprises. 
            Cancel anytime.
          </p>
          
          {/* Billing Toggle */}
          <div className="flex items-center justify-center gap-4 mb-12">
            <span className={`text-sm ${!isAnnual ? 'text-gray-900 font-medium' : 'text-gray-500'}`}>
              Monthly
            </span>
            <button
              onClick={() => setIsAnnual(!isAnnual)}
              className="relative inline-flex h-6 w-11 items-center rounded-full bg-purple-600 transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${isAnnual ? 'translate-x-6' : 'translate-x-1'}`} />
            </button>
            <span className={`text-sm ${isAnnual ? 'text-gray-900 font-medium' : 'text-gray-500'}`}>
              Annual
            </span>
            <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
              Save 20%
            </span>
          </div>
        </motion.div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto mb-20">
          {plans.map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              className={`relative bg-white rounded-2xl shadow-lg p-8 border-2 ${plan.color} ${
                plan.popular ? 'scale-105 shadow-2xl' : ''
              }`}
            >
              {/* Popular Badge */}
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <div className="bg-purple-600 text-white px-4 py-2 rounded-full text-sm font-medium">
                    Most Popular
                  </div>
                </div>
              )}

              {/* Plan Header */}
              <div className="text-center mb-8">
                <h3 className="text-xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                <p className="text-gray-600 mb-4">{plan.subtitle}</p>
                
                <div className="mb-4">
                  {plan.originalPrice && (
                    <div className="text-gray-400 line-through text-lg mb-1">
                      {plan.originalPrice}
                    </div>
                  )}
                  <div className="flex items-baseline justify-center gap-1">
                    <span className="text-4xl font-bold text-gray-900">{plan.price}</span>
                    {plan.period !== "forever" && (
                      <span className="text-gray-600">/{plan.period}</span>
                    )}
                  </div>
                  {plan.period === "forever" && (
                    <p className="text-sm text-green-600 font-medium">No credit card required</p>
                  )}
                </div>

                <button 
                  className={`w-full py-3 px-6 rounded-full font-semibold transition-all ${
                    plan.popular 
                      ? 'bg-purple-600 text-white hover:bg-purple-700 shadow-lg hover:shadow-xl' 
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                  }`}
                >
                  {plan.cta}
                  <ArrowRight className="w-4 h-4 ml-2 inline" />
                </button>
              </div>

              {/* Features */}
              <div className="space-y-4">
                {plan.features.map((feature) => (
                  <div key={feature} className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-5 h-5 bg-green-100 rounded-full flex items-center justify-center mt-0.5">
                      <Check className="w-3 h-3 text-green-600" />
                    </div>
                    <span className="text-gray-700">{feature}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Enterprise Banner */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl p-8 text-white text-center mb-16"
        >
          <h3 className="text-2xl font-bold mb-4">Enterprise Solutions</h3>
          <p className="text-lg opacity-90 mb-6">
            Need unlimited everything? Custom integrations? Dedicated support? 
            We've got you covered.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="px-8 py-3 bg-white text-purple-600 rounded-full font-semibold hover:bg-gray-50 transition-colors">
              Contact Sales
            </button>
            <button className="px-8 py-3 border border-white/30 text-white rounded-full font-semibold hover:bg-white/10 transition-colors">
              Schedule Demo
            </button>
          </div>
        </motion.div>

        {/* FAQs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="max-w-2xl mx-auto"
        >
          <h3 className="text-2xl font-bold text-center text-gray-900 mb-8">
            Frequently Asked Questions
          </h3>
          
          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div key={index} className="border border-gray-200 rounded-xl">
                <button
                  onClick={() => setOpenFaq(openFaq === index ? null : index)}
                  className="w-full px-6 py-4 text-left flex justify-between items-center hover:bg-gray-50 rounded-xl transition-colors"
                >
                  <span className="font-medium text-gray-900">{faq.question}</span>
                  <span className={`text-gray-500 transition-transform ${openFaq === index ? 'rotate-180' : ''}`}>
                    ↓
                  </span>
                </button>
                {openFaq === index && (
                  <div className="px-6 pb-4">
                    <p className="text-gray-600">{faq.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}