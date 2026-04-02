'use client'
import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

const stats = [
  { value: 50, suffix: '+', label: 'AI Models', description: 'Specialized models in consensus' },
  { value: 4, suffix: '', label: 'MVP Markets', description: 'Oil · Gold · BTC · ETH' },
  { value: 99.9, suffix: '%', label: 'Uptime', description: 'Enterprise-grade reliability' },
  { value: 100, suffix: 'ms', label: 'Latency', description: 'Sub-100ms signal delivery', prefix: '<' },
]

function AnimatedNumber({ value, suffix, prefix }: { value: number; suffix: string; prefix?: string }) {
  const [current, setCurrent] = useState(0)

  useEffect(() => {
    const duration = 1800
    const steps = 60
    const increment = value / steps
    let step = 0
    const timer = setInterval(() => {
      step++
      setCurrent(Math.min(step * increment, value))
      if (step >= steps) clearInterval(timer)
    }, duration / steps)
    return () => clearInterval(timer)
  }, [value])

  const display = value % 1 !== 0 ? current.toFixed(1) : Math.round(current).toString()

  return (
    <span>
      {prefix && <span>{prefix}</span>}
      {display}
      <span>{suffix}</span>
    </span>
  )
}

export default function Stats() {
  return (
    <section className="py-16 px-4 bg-bg-card border-y border-border-base">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: index * 0.08 }}
              className="text-center"
            >
              <div className="text-4xl lg:text-5xl font-bold text-gold mb-2 tracking-tight">
                <AnimatedNumber value={stat.value} suffix={stat.suffix} prefix={stat.prefix} />
              </div>
              <div className="text-text-base font-semibold mb-1 text-sm">{stat.label}</div>
              <div className="text-text-muted text-xs">{stat.description}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
