'use client'
import { motion } from 'framer-motion'
import { Star, Quote } from 'lucide-react'
import { useState, useEffect } from 'react'

const testimonials = [
  {
    name: "Sarah Chen",
    role: "Marketing Director",
    company: "TechFlow Solutions",
    image: "https://i.pravatar.cc/150?img=1",
    rating: 5,
    text: "FormFlow AI transformed our lead qualification process completely. What used to take our team hours now happens in minutes, and our conversion rates increased by 40%.",
    metrics: {
      label: "Conversion Rate",
      value: "+40%",
      period: "in 3 months"
    }
  },
  {
    name: "Michael Rodriguez",
    role: "Fitness Coach",
    company: "Wellness Pro",
    image: "https://i.pravatar.cc/150?img=2",
    rating: 5,
    text: "My clients are blown away by their personalized nutrition dashboards. The AI creates meal plans that would take me 2 hours to build manually. Game changer!",
    metrics: {
      label: "Time Saved",
      value: "20 hrs/week",
      period: "per client"
    }
  },
  {
    name: "Emily Watson",
    role: "Event Planner",
    company: "Dream Events Co",
    image: "https://i.pravatar.cc/150?img=3",
    rating: 5,
    text: "The event registration dashboards are absolutely stunning. Our clients feel VIP from the moment they register. No more boring confirmation emails!",
    metrics: {
      label: "Client Satisfaction",
      value: "98%",
      period: "5-star reviews"
    }
  },
  {
    name: "David Kim",
    role: "Sales Manager",
    company: "CloudTech Inc",
    image: "https://i.pravatar.cc/150?img=4",
    rating: 5,
    text: "The lead scoring is incredibly accurate. We're now focusing on the right prospects and our close rate has doubled. ROI was immediate.",
    metrics: {
      label: "Close Rate",
      value: "+100%",
      period: "since launch"
    }
  },
  {
    name: "Lisa Thompson",
    role: "Customer Success",
    company: "SaaS Startup",
    image: "https://i.pravatar.cc/150?img=5",
    rating: 5,
    text: "Customer feedback analysis is now automated and actionable. We identify issues faster and our NPS score improved by 25 points!",
    metrics: {
      label: "NPS Score",
      value: "+25 pts",
      period: "improvement"
    }
  },
  {
    name: "James Park",
    role: "Agency Owner",
    company: "Digital Marketing Pro",
    image: "https://i.pravatar.cc/150?img=6",
    rating: 5,
    text: "We're offering FormFlow dashboards as a premium service to our clients. It's become a major differentiator and revenue stream for our agency.",
    metrics: {
      label: "New Revenue",
      value: "$15K/mo",
      period: "additional"
    }
  }
]

export default function Testimonials() {
  const [activeTestimonial, setActiveTestimonial] = useState(0)
  const [isAutoPlaying, setIsAutoPlaying] = useState(true)

  useEffect(() => {
    if (!isAutoPlaying) return
    
    const interval = setInterval(() => {
      setActiveTestimonial((prev) => (prev + 1) % testimonials.length)
    }, 5000)
    
    return () => clearInterval(interval)
  }, [isAutoPlaying])

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
            Loved by
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">
              2,500+ Businesses
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            See how companies across industries are transforming their form experiences 
            and driving better results with FormFlow AI.
          </p>
        </motion.div>

        {/* Stats Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="grid md:grid-cols-4 gap-8 mb-20"
        >
          {[
            { label: "Forms Created", value: "50K+", subtext: "and counting" },
            { label: "Time Saved", value: "10K hrs", subtext: "monthly" },
            { label: "Conversion Lift", value: "+35%", subtext: "average" },
            { label: "Client Rating", value: "4.9/5", subtext: "★★★★★" }
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="text-center p-6 rounded-2xl bg-gradient-to-br from-purple-50 to-pink-50"
            >
              <div className="text-3xl font-bold text-gray-900 mb-2">{stat.value}</div>
              <div className="text-gray-600 font-medium mb-1">{stat.label}</div>
              <div className="text-sm text-gray-500">{stat.subtext}</div>
            </motion.div>
          ))}
        </motion.div>

        {/* Main Testimonial Showcase */}
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Testimonial Content */}
            <motion.div
              key={activeTestimonial}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className="order-2 lg:order-1"
            >
              <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-8 rounded-2xl">
                {/* Quote Icon */}
                <div className="w-12 h-12 bg-purple-600 rounded-xl flex items-center justify-center mb-6">
                  <Quote className="w-6 h-6 text-white" />
                </div>
                
                {/* Rating */}
                <div className="flex gap-1 mb-4">
                  {[...Array(testimonials[activeTestimonial].rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                
                {/* Testimonial Text */}
                <blockquote className="text-xl text-gray-800 leading-relaxed mb-6">
                  "{testimonials[activeTestimonial].text}"
                </blockquote>
                
                {/* Metrics */}
                <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 mb-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {testimonials[activeTestimonial].metrics.value}
                    </div>
                    <div className="text-gray-600 font-medium">
                      {testimonials[activeTestimonial].metrics.label}
                    </div>
                    <div className="text-sm text-gray-500">
                      {testimonials[activeTestimonial].metrics.period}
                    </div>
                  </div>
                </div>
                
                {/* Author Info */}
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center">
                    <span className="text-white font-bold">
                      {testimonials[activeTestimonial].name[0]}
                    </span>
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">
                      {testimonials[activeTestimonial].name}
                    </div>
                    <div className="text-gray-600 text-sm">
                      {testimonials[activeTestimonial].role} at {testimonials[activeTestimonial].company}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Testimonial Navigation */}
            <div className="order-1 lg:order-2">
              <div 
                className="space-y-3"
                onMouseEnter={() => setIsAutoPlaying(false)}
                onMouseLeave={() => setIsAutoPlaying(true)}
              >
                {testimonials.map((testimonial, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0.5 }}
                    animate={{ opacity: activeTestimonial === index ? 1 : 0.7 }}
                    transition={{ duration: 0.3 }}
                    className={`p-4 rounded-xl cursor-pointer transition-all ${
                      activeTestimonial === index
                        ? 'bg-purple-100 border-2 border-purple-300 shadow-lg'
                        : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                    }`}
                    onClick={() => setActiveTestimonial(index)}
                  >
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center flex-shrink-0">
                        <span className="text-white font-bold text-sm">
                          {testimonial.name[0]}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-900 text-sm">
                          {testimonial.name}
                        </div>
                        <div className="text-gray-600 text-xs mb-2">
                          {testimonial.role}
                        </div>
                        <div className="text-gray-700 text-sm line-clamp-2">
                          "{testimonial.text}"
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
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
          <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-2xl p-8 text-white">
            <h3 className="text-2xl font-bold mb-4">
              Join thousands of happy customers
            </h3>
            <p className="text-lg opacity-90 mb-6">
              Start your free trial today and see the difference AI-powered dashboards make
            </p>
            <button className="px-8 py-4 bg-white text-gray-900 rounded-full font-semibold text-lg hover:bg-gray-100 transition-colors shadow-lg hover:shadow-xl">
              Start Free Trial →
            </button>
            <p className="text-sm opacity-70 mt-4">
              No credit card required • 14-day free trial • Cancel anytime
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  )
}