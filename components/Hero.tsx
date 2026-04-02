'use client'
import { motion } from 'framer-motion'
import Link from 'next/link'
import dynamic from 'next/dynamic'
import { Suspense } from 'react'
import { ArrowRight, BarChart2, TrendingUp, Cpu } from 'lucide-react'

const Globe = dynamic(() => import('./Globe'), { ssr: false })

export default function Hero() {
  return (
    <section className="min-h-screen flex items-center pt-16 bg-bg-base relative overflow-hidden">
      {/* Subtle background pattern */}
      <div className="absolute inset-0 pointer-events-none">
        <div
          className="absolute inset-0 opacity-[0.025]"
          style={{
            backgroundImage: `radial-gradient(circle at 1px 1px, #2F6BFF 1px, transparent 0)`,
            backgroundSize: '32px 32px',
          }}
        />
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-primary/5 rounded-full blur-3xl -translate-y-1/3 translate-x-1/3" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-gold/5 rounded-full blur-3xl translate-y-1/3 -translate-x-1/3" />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full py-16">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left: copy */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, delay: 0.1 }}
          >
            {/* Status badge */}
            <div className="inline-flex items-center gap-2 bg-primary-light border border-primary/20 rounded-full px-4 py-1.5 mb-6">
              <span className="w-2 h-2 rounded-full bg-success animate-pulse-dot" />
              <span className="text-primary text-sm font-semibold">Live Market Intelligence</span>
            </div>

            <h1 className="text-5xl lg:text-6xl font-bold leading-[1.12] mb-6 text-text-base tracking-tight">
              The System That{' '}
              <span className="text-primary-gradient">Thinks</span>
              <br />
              For You
            </h1>

            <p className="text-text-muted text-lg mb-8 max-w-lg leading-relaxed">
              50+ AI models reach consensus on every signal. AIP translates noisy market data
              into clear, confident intelligence — for commodities, crypto, and beyond.
            </p>

            {/* UX philosophy quick-answers */}
            <div className="grid grid-cols-2 gap-3 mb-8">
              {[
                { q: 'What is happening?', a: 'Live market pulse' },
                { q: 'Why is it happening?', a: 'AI-sourced reasoning' },
                { q: 'What should I do?', a: 'Consensus signal' },
                { q: 'How confident?', a: 'Model agreement score' },
              ].map(({ q, a }) => (
                <div key={q} className="light-card rounded-xl p-3">
                  <div className="text-xs text-text-muted mb-0.5">{q}</div>
                  <div className="text-sm font-semibold text-text-base">{a}</div>
                </div>
              ))}
            </div>

            <div className="flex flex-wrap gap-3">
              <Link
                href="/dashboard"
                className="flex items-center gap-2 bg-primary hover:bg-primary/90 text-white px-6 py-3 rounded-xl font-semibold transition-all shadow-primary hover:shadow-lg hover:-translate-y-0.5"
              >
                Open Dashboard
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="#features"
                className="flex items-center gap-2 border border-border-base bg-bg-card hover:bg-bg-base px-6 py-3 rounded-xl text-text-base font-semibold transition-all hover:-translate-y-0.5"
              >
                <BarChart2 className="w-4 h-4 text-primary" />
                See Features
              </Link>
            </div>

            {/* Mini stats */}
            <div className="flex gap-8 mt-10 pt-8 border-t border-border-base">
              {[
                { icon: Cpu, label: '50+ AI Models', sub: 'In consensus' },
                { icon: TrendingUp, label: '4 Markets', sub: 'MVP launch · expanding' },
              ].map(({ icon: Icon, label, sub }) => (
                <div key={label} className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg bg-primary-light flex items-center justify-center">
                    <Icon className="w-4 h-4 text-primary" />
                  </div>
                  <div>
                    <div className="text-text-base font-semibold text-sm">{label}</div>
                    <div className="text-text-muted text-xs">{sub}</div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Right: Globe (retains dark bg — intentional dark analytical zone) */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="relative"
          >
            <div className="absolute -inset-4 bg-gradient-to-br from-primary/8 to-gold/5 rounded-[2rem] blur-2xl" />
            <div className="relative globe-container border border-border-base">
              <Suspense
                fallback={
                  <div className="w-full h-[500px] flex items-center justify-center bg-dark-bg">
                    <div className="text-primary text-sm animate-pulse">Loading globe…</div>
                  </div>
                }
              >
                <Globe />
              </Suspense>
            </div>
            <p className="absolute -bottom-6 left-0 right-0 text-center text-xs text-text-muted">
              Drag to rotate · Hover hubs for live data
            </p>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
