'use client'
import { motion } from 'framer-motion'
import { ChevronDown, ChevronUp, Cpu } from 'lucide-react'
import { useState } from 'react'

interface ModelVote {
  name: string
  signal: 'BUY' | 'HOLD' | 'SELL'
  confidence: number
}

interface ConsensusData {
  asset: string
  assetName: string
  signal: 'BUY' | 'HOLD' | 'SELL'
  overallConfidence: number
  agreement: 'High' | 'Medium' | 'Low'
  models: ModelVote[]
  reasoning?: string
}

const signalColors: Record<string, { badge: string; bar: string; text: string }> = {
  BUY: { badge: 'badge-buy', bar: 'bg-success', text: 'text-success' },
  SELL: { badge: 'badge-sell', bar: 'bg-danger', text: 'text-danger' },
  HOLD: { badge: 'badge-hold', bar: 'bg-gold', text: 'text-gold' },
}

const agreementColor: Record<string, string> = {
  High: 'text-success',
  Medium: 'text-gold',
  Low: 'text-danger',
}

function SignalBadge({ signal }: { signal: 'BUY' | 'HOLD' | 'SELL' }) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${signalColors[signal].badge}`}>
      {signal}
    </span>
  )
}

export default function AIConsensusCard({
  data,
  className = '',
}: {
  data: ConsensusData
  className?: string
}) {
  const [expanded, setExpanded] = useState(false)

  const buyCount = data.models.filter((m) => m.signal === 'BUY').length
  const sellCount = data.models.filter((m) => m.signal === 'SELL').length
  const holdCount = data.models.filter((m) => m.signal === 'HOLD').length
  const total = data.models.length

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className={`light-card rounded-2xl overflow-hidden ${className}`}
    >
      {/* Header */}
      <div className="px-5 py-4 border-b border-border-base flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary-light flex items-center justify-center flex-shrink-0">
            <Cpu className="w-5 h-5 text-primary" />
          </div>
          <div>
            <div className="text-xs text-text-muted font-medium mb-0.5">AI Consensus</div>
            <div className="font-bold text-text-base leading-tight">
              {data.asset}
              <span className="text-text-muted font-normal ml-1.5 text-sm">{data.assetName}</span>
            </div>
          </div>
        </div>
        <div className="flex flex-col items-end gap-1">
          <SignalBadge signal={data.signal} />
          <span className="text-xs text-text-muted">{data.overallConfidence}% confidence</span>
        </div>
      </div>

      {/* Confidence bar */}
      <div className="px-5 pt-4 pb-3">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-text-muted">Overall Confidence</span>
          <span className={`text-sm font-bold ${signalColors[data.signal].text}`}>
            {data.overallConfidence}%
          </span>
        </div>
        <div className="consensus-bar">
          <motion.div
            className={`consensus-bar-fill ${signalColors[data.signal].bar}`}
            initial={{ width: 0 }}
            animate={{ width: `${data.overallConfidence}%` }}
            transition={{ duration: 0.8, delay: 0.2 }}
          />
        </div>
      </div>

      {/* Vote breakdown */}
      <div className="px-5 pb-4">
        <div className="flex gap-2 mb-4">
          {[
            { label: 'BUY', count: buyCount, color: 'bg-success-light text-success' },
            { label: 'HOLD', count: holdCount, color: 'bg-gold-light text-gold' },
            { label: 'SELL', count: sellCount, color: 'bg-danger-light text-danger' },
          ].map(({ label, count, color }) => (
            <div
              key={label}
              className={`flex-1 rounded-lg px-2 py-1.5 text-center text-xs font-medium ${color}`}
            >
              <div className="text-base font-bold">{count}</div>
              <div>{label}</div>
            </div>
          ))}
        </div>

        <div className="flex items-center justify-between">
          <div className="text-xs text-text-muted">
            Agreement:{' '}
            <span className={`font-semibold ${agreementColor[data.agreement]}`}>
              {data.agreement}
            </span>
          </div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-xs text-primary font-medium hover:underline"
          >
            {expanded ? 'Hide models' : `View ${total} models`}
            {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
        </div>
      </div>

      {/* Expanded model breakdown */}
      {expanded && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="border-t border-border-base"
        >
          <div className="px-5 py-3 space-y-2.5">
            {data.models.map((model) => (
              <div key={model.name} className="flex items-center gap-3">
                <div className="w-1.5 h-1.5 rounded-full bg-text-muted/40 flex-shrink-0" />
                <span className="text-sm text-text-base flex-1 font-medium">{model.name}</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 consensus-bar">
                    <div
                      className={`consensus-bar-fill ${signalColors[model.signal].bar}`}
                      style={{ width: `${model.confidence}%` }}
                    />
                  </div>
                  <span className="text-xs text-text-muted w-8 text-right">{model.confidence}%</span>
                  <SignalBadge signal={model.signal} />
                </div>
              </div>
            ))}
          </div>
          {data.reasoning && (
            <div className="px-5 pb-4">
              <div className="bg-primary-light rounded-lg p-3 text-xs text-primary leading-relaxed">
                <span className="font-semibold">AI Reasoning: </span>
                {data.reasoning}
              </div>
            </div>
          )}
        </motion.div>
      )}
    </motion.div>
  )
}

// Sample data export for reuse across pages
export const sampleConsensusData: ConsensusData[] = [
  {
    asset: 'BTC',
    assetName: 'Bitcoin',
    signal: 'BUY',
    overallConfidence: 68,
    agreement: 'Medium',
    models: [
      { name: 'Model A — Trend', signal: 'BUY', confidence: 75 },
      { name: 'Model B — Sentiment', signal: 'HOLD', confidence: 60 },
      { name: 'Model C — On-chain', signal: 'BUY', confidence: 70 },
    ],
    reasoning:
      'Strong accumulation pattern detected on-chain. Trend models confirm breakout above 200-day MA. Sentiment model neutral pending macro data.',
  },
  {
    asset: 'GOLD',
    assetName: 'Gold',
    signal: 'BUY',
    overallConfidence: 74,
    agreement: 'High',
    models: [
      { name: 'Model A — Macro', signal: 'BUY', confidence: 80 },
      { name: 'Model B — Technical', signal: 'BUY', confidence: 72 },
      { name: 'Model C — Flow', signal: 'BUY', confidence: 70 },
    ],
    reasoning:
      'Dollar weakness and elevated geopolitical risk driving safe-haven demand. Technical breakout above $2,100 resistance confirmed by flow data.',
  },
  {
    asset: 'OIL',
    assetName: 'WTI Crude',
    signal: 'HOLD',
    overallConfidence: 55,
    agreement: 'Low',
    models: [
      { name: 'Model A — Supply', signal: 'SELL', confidence: 65 },
      { name: 'Model B — Demand', signal: 'BUY', confidence: 58 },
      { name: 'Model C — Momentum', signal: 'HOLD', confidence: 50 },
    ],
    reasoning:
      'Conflicting signals between supply-side pressure (rising inventories) and demand-side support (strong industrial data). Wait for clearer direction.',
  },
  {
    asset: 'ETH',
    assetName: 'Ethereum',
    signal: 'BUY',
    overallConfidence: 71,
    agreement: 'High',
    models: [
      { name: 'Model A — DeFi', signal: 'BUY', confidence: 78 },
      { name: 'Model B — Technical', signal: 'BUY', confidence: 68 },
      { name: 'Model C — Sentiment', signal: 'BUY', confidence: 67 },
    ],
    reasoning:
      'ETH staking yields remain attractive. DeFi TVL rising. Technical structure bullish above key support at $3,200.',
  },
]
