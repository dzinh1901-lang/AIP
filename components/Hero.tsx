'use client'
import { motion } from 'framer-motion'
import Link from 'next/link'
import dynamic from 'next/dynamic'
import { Suspense } from 'react'
import { ArrowRight, BarChart2, TrendingUp } from 'lucide-react'

const Globe = dynamic(() => import('./Globe'), { ssr: false })

export default function Hero() {
  return (
    <section className="min-h-screen flex items-center pt-16 relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-accent-blue/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent-purple/5 rounded-full blur-3xl" />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left content */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <div className="inline-flex items-center gap-2 bg-accent-blue/10 border border-accent-blue/20 rounded-full px-4 py-1.5 mb-6">
              <span className="w-2 h-2 rounded-full bg-accent-green animate-pulse" />
              <span className="text-accent-blue text-sm font-medium">Live Market Intelligence</span>
            </div>

            <h1 className="text-5xl lg:text-6xl font-bold leading-tight mb-6">
              <span className="text-white">AI-Powered</span>
              <br />
              <span className="gradient-text">Market Intelligence</span>
            </h1>

            <p className="text-gray-400 text-lg mb-8 max-w-lg leading-relaxed">
              Harness the power of 50+ AI models working in consensus to deliver real-time signals
              for commodities, crypto, and global markets. Make smarter decisions with multi-model
              validation.
            </p>

            <div className="flex flex-wrap gap-4 mb-10">
              <Link
                href="/login"
                className="flex items-center gap-2 bg-gradient-to-r from-accent-blue to-accent-purple px-6 py-3 rounded-lg text-white font-medium hover:opacity-90 transition-all hover:scale-105"
              >
                Get Started
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="#markets"
                className="flex items-center gap-2 border border-accent-blue/30 px-6 py-3 rounded-lg text-accent-blue font-medium hover:bg-accent-blue/10 transition-all"
              >
                <BarChart2 className="w-4 h-4" />
                View Markets
              </Link>
            </div>

            <div className="flex gap-8">
              {[
                { icon: TrendingUp, label: '50+ AI Models', value: 'In Consensus' },
                { icon: BarChart2, label: '200+ Markets', value: 'Covered' },
              ].map(({ icon: Icon, label, value }) => (
                <div key={label} className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-accent-blue/10 border border-accent-blue/20 flex items-center justify-center">
                    <Icon className="w-5 h-5 text-accent-blue" />
                  </div>
                  <div>
                    <div className="text-white font-semibold text-sm">{label}</div>
                    <div className="text-gray-500 text-xs">{value}</div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Right: 3D Globe */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="relative"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-accent-blue/10 to-accent-purple/10 rounded-3xl blur-xl" />
            <div className="relative rounded-3xl overflow-hidden border border-accent-blue/20">
              <Suspense fallback={
                <div className="w-full h-[500px] flex items-center justify-center bg-bg-card">
                  <div className="text-accent-blue animate-pulse">Loading Globe...</div>
                </div>
              }>
                <Globe />
              </Suspense>
            </div>
            <div className="absolute bottom-4 left-0 right-0 text-center text-xs text-gray-500">
              Hover over market hubs to see live data
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
