'use client'
import { motion } from 'framer-motion'
import { ArrowRight, Play, Star } from 'lucide-react'
import { useState } from 'react'
import Image from 'next/image'

export default function Hero() {
  const [videoOpen, setVideoOpen] = useState(false)
  
  return (
    <section className="relative min-h-screen bg-gradient-to-br from-purple-600 via-pink-500 to-red-500 text-white overflow-hidden">
      {/* Animated background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
        <div className="absolute top-40 left-40 w-80 h-80 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
      </div>

      {/* Navigation */}
      <nav className="relative z-20 container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
              <span className="text-purple-600 font-bold text-lg">F</span>
            </div>
            <span className="text-xl font-bold">FormFlow AI</span>
          </div>
          <div className="hidden md:flex items-center space-x-8">
            <a href="#features" className="hover:text-purple-200 transition-colors">Features</a>
            <a href="#pricing" className="hover:text-purple-200 transition-colors">Pricing</a>
            <a href="#faq" className="hover:text-purple-200 transition-colors">FAQ</a>
            <a href="/login" className="px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full hover:bg-white/30 transition-all">
              Login
            </a>
          </div>
        </div>
      </nav>
      
      <div className="relative z-10 container mx-auto px-4 py-12 lg:py-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-4xl mx-auto"
        >
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="inline-flex items-center px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full mb-8"
          >
            <span className="animate-pulse w-2 h-2 bg-green-400 rounded-full mr-2"></span>
            <span className="text-sm font-medium">🚀 Launch Special: 50% OFF First Month</span>
          </motion.div>
          
          {/* Headline */}
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="text-4xl md:text-6xl lg:text-7xl font-bold mb-8 leading-tight"
          >
            Turn Any Form Into an
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-pink-400 animate-pulse">
              AI-Powered Dashboard
            </span>
            in 60 Seconds
          </motion.h1>
          
          {/* Subheadline */}
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.8 }}
            className="text-xl lg:text-2xl mb-10 opacity-90 max-w-3xl mx-auto leading-relaxed"
          >
            Transform boring form responses into beautiful, intelligent dashboards 
            that wow your clients. Works with Typeform, Google Forms & more. 
            <strong>No coding required.</strong>
          </motion.p>
          
          {/* CTA Buttons */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.8 }}
            className="flex flex-col sm:flex-row gap-4 justify-center mb-16"
          >
            <motion.button
              whileHover={{ scale: 1.05, boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)" }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-4 bg-white text-purple-600 rounded-full font-semibold text-lg shadow-xl hover:shadow-2xl transition-all flex items-center justify-center gap-2 hover-lift"
            >
              Start Free Trial
              <ArrowRight className="w-5 h-5" />
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setVideoOpen(true)}
              className="px-8 py-4 bg-white/20 backdrop-blur-sm rounded-full font-semibold text-lg hover:bg-white/30 transition-all flex items-center justify-center gap-2 border border-white/30"
            >
              <Play className="w-5 h-5" />
              Watch Demo (2 min)
            </motion.button>
          </motion.div>
          
          {/* Social Proof */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.0, duration: 0.8 }}
            className="flex flex-col md:flex-row items-center justify-center gap-8 mb-12"
          >
            <div className="flex items-center gap-4">
              <div className="flex -space-x-2">
                {[1,2,3,4,5].map(i => (
                  <div key={i} className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 border-2 border-white flex items-center justify-center">
                    <span className="text-white text-sm font-semibold">{i}</span>
                  </div>
                ))}
              </div>
              <div className="text-left">
                <div className="flex gap-1">
                  {[1,2,3,4,5].map(i => (
                    <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <p className="text-sm opacity-80">Loved by 2,500+ users</p>
              </div>
            </div>
            
            <div className="flex items-center gap-6 text-sm opacity-80">
              <span>✅ No credit card required</span>
              <span>⚡ Setup in 60 seconds</span>
              <span>🔒 SOC 2 compliant</span>
            </div>
          </motion.div>
        </motion.div>
        
        {/* Dashboard Preview */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2, duration: 0.8 }}
          className="relative max-w-6xl mx-auto"
        >
          <div className="absolute inset-0 bg-gradient-to-t from-purple-600/50 to-transparent z-10 rounded-xl"></div>
          
          {/* Placeholder dashboard image */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-8 shadow-2xl border border-white/20">
            <div className="bg-white rounded-lg p-6 shadow-lg">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                  <span className="text-white font-bold text-lg">📊</span>
                </div>
                <div>
                  <h3 className="text-gray-900 font-semibold text-lg">Diet Plan Dashboard</h3>
                  <p className="text-gray-600 text-sm">Generated in 45 seconds</p>
                </div>
              </div>
              
              <div className="grid md:grid-cols-3 gap-4 mb-6">
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">1,800</div>
                  <div className="text-gray-600 text-sm">Daily Calories</div>
                </div>
                <div className="bg-pink-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-pink-600">7 Days</div>
                  <div className="text-gray-600 text-sm">Meal Plan</div>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">42</div>
                  <div className="text-gray-600 text-sm">Shopping Items</div>
                </div>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                  <span className="text-gray-700 text-sm">Breakfast: Oatmeal with berries (350 cal)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                  <span className="text-gray-700 text-sm">Lunch: Grilled chicken salad (450 cal)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-purple-400 rounded-full"></div>
                  <span className="text-gray-700 text-sm">Dinner: Salmon with vegetables (550 cal)</span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
      
      {/* Video Modal */}
      {videoOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
          <div className="bg-white rounded-xl p-8 max-w-2xl w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold text-gray-900">FormFlow Demo</h3>
              <button 
                onClick={() => setVideoOpen(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <Play className="w-16 h-16 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-600">Demo video will be embedded here</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  )
}