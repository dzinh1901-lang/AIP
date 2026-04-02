'use client'
import { motion } from 'framer-motion'
import AIConsensusCard, { sampleConsensusData } from './AIConsensusCard'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'

export default function ConsensusPreview() {
  return (
    <section id="markets" className="py-24 px-4 bg-bg-base">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12"
        >
          <div>
            <span className="inline-block bg-gold-light text-gold text-xs font-semibold uppercase tracking-widest px-3 py-1 rounded-full mb-4">
              Signature Feature
            </span>
            <h2 className="text-4xl font-bold text-text-base mb-3 tracking-tight">
              The AI Consensus Card
            </h2>
            <p className="text-text-muted max-w-xl text-lg">
              Most platforms show data. AIP shows <em>thinking</em>. Every signal comes with a
              full breakdown of which models agreed, disagreed, and why.
            </p>
          </div>
          <Link
            href="/dashboard"
            className="flex-shrink-0 flex items-center gap-2 bg-primary hover:bg-primary/90 text-white px-5 py-2.5 rounded-xl font-semibold text-sm transition-all shadow-primary self-start md:self-auto"
          >
            View Live Dashboard
            <ArrowRight className="w-4 h-4" />
          </Link>
        </motion.div>

        {/* Cards grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {sampleConsensusData.map((data, i) => (
            <motion.div
              key={data.asset}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.45, delay: i * 0.08 }}
            >
              <AIConsensusCard data={data} />
            </motion.div>
          ))}
        </div>

        {/* Callout */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-10 light-card rounded-2xl p-6 flex flex-col sm:flex-row items-start sm:items-center gap-4"
        >
          <div className="flex-1">
            <div className="font-semibold text-text-base mb-1">Every screen answers four questions</div>
            <div className="text-text-muted text-sm flex flex-wrap gap-x-6 gap-y-1 mt-2">
              <span>① What is happening?</span>
              <span>② Why is it happening?</span>
              <span>③ What should I do?</span>
              <span>④ How confident is it?</span>
            </div>
          </div>
          <Link
            href="/dashboard"
            className="flex-shrink-0 flex items-center gap-1.5 text-primary font-semibold text-sm hover:underline"
          >
            Open Dashboard <ArrowRight className="w-4 h-4" />
          </Link>
        </motion.div>
      </div>
    </section>
  )
}
