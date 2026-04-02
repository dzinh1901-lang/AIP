'use client'
import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

const stats = [
  { value: 50, suffix: '+', label: 'AI Models', description: 'Specialized models in consensus' },
  { value: 200, suffix: '+', label: 'Markets', description: 'Global coverage across asset classes' },
  { value: 99.9, suffix: '%', label: 'Uptime', description: 'Enterprise-grade reliability' },
  { value: 100, suffix: 'ms', label: 'Latency', description: 'Sub-100ms signal delivery', prefix: '<' },
]

function AnimatedNumber({ value, suffix, prefix }: { value: number; suffix: string; prefix?: string }) {
  const [current, setCurrent] = useState(0)

  useEffect(() => {
    const duration = 2000
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
      {prefix && <span className="text-accent-blue">{prefix}</span>}
      {display}
      <span className="text-accent-blue">{suffix}</span>
    </span>
  )
}

export default function Stats() {
  return (
    <section className="py-16 px-4 border-y border-accent-blue/10 bg-bg-secondary/50">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="text-center"
            >
              <div className="text-4xl lg:text-5xl font-bold text-white mb-2">
                <AnimatedNumber value={stat.value} suffix={stat.suffix} prefix={stat.prefix} />
              </div>
              <div className="text-accent-blue font-semibold mb-1">{stat.label}</div>
              <div className="text-gray-500 text-sm">{stat.description}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
