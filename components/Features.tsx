'use client'
import { motion } from 'framer-motion'
import { Brain, Activity, Globe2 } from 'lucide-react'

const features = [
  {
    icon: Brain,
    title: 'Multi-Model AI Consensus',
    description:
      'Signals from 50+ specialized AI models — GPT, Claude, Gemini, and proprietary models — filtered by consensus. Only high-conviction signals surface.',
    badge: 'Core Intelligence',
    badgeColor: 'bg-primary-light text-primary',
    iconBg: 'bg-primary-light',
    iconColor: 'text-primary',
  },
  {
    icon: Activity,
    title: 'Real-Time Analytics',
    description:
      'Sub-100ms market data processing. Live sentiment analysis, price action detection, and anomaly scoring running continuously across tracked assets.',
    badge: 'Speed',
    badgeColor: 'bg-success-light text-success',
    iconBg: 'bg-success-light',
    iconColor: 'text-success',
  },
  {
    icon: Globe2,
    title: 'Global Market Coverage',
    description:
      'MVP covers Oil, Gold, BTC and ETH — with architecture built to scale to equities, forex, and 200+ additional instruments.',
    badge: 'Expanding',
    badgeColor: 'bg-gold-light text-gold',
    iconBg: 'bg-gold-light',
    iconColor: 'text-gold',
  },
]

export default function Features() {
  return (
    <section id="features" className="py-24 px-4 bg-bg-base">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <span className="inline-block bg-primary-light text-primary text-xs font-semibold uppercase tracking-widest px-3 py-1 rounded-full mb-4">
            Platform Features
          </span>
          <h2 className="text-4xl font-bold text-text-base mb-4 tracking-tight">
            Intelligence at Every Layer
          </h2>
          <p className="text-text-muted max-w-xl mx-auto text-lg">
            AIP answers the four questions that matter: what, why, what to do, and how confident.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="light-card light-card-hover rounded-2xl p-7"
            >
              <div className="flex items-start justify-between mb-5">
                <div className={`w-12 h-12 rounded-xl ${feature.iconBg} flex items-center justify-center`}>
                  <feature.icon className={`w-6 h-6 ${feature.iconColor}`} />
                </div>
                <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${feature.badgeColor}`}>
                  {feature.badge}
                </span>
              </div>
              <h3 className="text-lg font-bold text-text-base mb-3">{feature.title}</h3>
              <p className="text-text-muted leading-relaxed text-sm">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
