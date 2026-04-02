'use client'
import { motion } from 'framer-motion'
import { Brain, Activity, Globe2 } from 'lucide-react'

const features = [
  {
    icon: Brain,
    title: 'Multi-Model AI Consensus',
    description:
      'Our platform aggregates signals from 50+ specialized AI models including GPT-4, Claude, Gemini, and proprietary models. Consensus-based validation filters noise and surfaces high-conviction signals.',
    color: 'from-accent-blue to-blue-600',
    glow: 'shadow-accent-blue/20',
  },
  {
    icon: Activity,
    title: 'Real-Time Analytics',
    description:
      'Sub-100ms latency on market data processing. Live sentiment analysis, price action detection, and anomaly detection running continuously across all tracked markets.',
    color: 'from-accent-purple to-purple-600',
    glow: 'shadow-accent-purple/20',
  },
  {
    icon: Globe2,
    title: 'Global Market Coverage',
    description:
      'Track commodities, cryptocurrencies, forex, and equities across 200+ markets worldwide. From oil futures in Dubai to crypto derivatives in Singapore.',
    color: 'from-accent-green to-green-600',
    glow: 'shadow-accent-green/20',
  },
]

export default function Features() {
  return (
    <section id="features" className="py-24 px-4">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="text-accent-blue text-sm font-medium uppercase tracking-widest">
            Platform Features
          </span>
          <h2 className="text-4xl font-bold text-white mt-3 mb-4">
            Intelligence at Every Layer
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            AIP combines cutting-edge AI with real-time market data to give you an unfair
            advantage in any market condition.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.15 }}
              whileHover={{ y: -8, scale: 1.02 }}
              className={`glass-card rounded-2xl p-8 hover:border-accent-blue/30 transition-all duration-300 shadow-xl ${feature.glow}`}
            >
              <div
                className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-6 shadow-lg`}
              >
                <feature.icon className="w-7 h-7 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
              <p className="text-gray-400 leading-relaxed">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
