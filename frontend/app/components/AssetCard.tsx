'use client'

import SignalBadge from './SignalBadge'

interface Asset {
  symbol: string
  name: string
  price: number
  change_1h?: number
  change_24h?: number
  volume_24h?: number
  asset_type: string
}

interface Consensus {
  asset: string
  final_signal: string
  confidence: number
  agreement_level: string
  models?: Record<string, { signal: string; confidence: number; reasoning: string[] }>
  dissenting_models?: string[]
}

interface AssetCardProps {
  asset: Asset
  consensus?: Consensus
}

function formatPrice(price: number): string {
  if (price >= 1000) return `$${price.toLocaleString('en-US', { maximumFractionDigits: 0 })}`
  if (price >= 1) return `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  return `$${price.toFixed(4)}`
}

function formatChange(change?: number): string {
  if (change == null) return '—'
  return `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`
}

const ASSET_EMOJIS: Record<string, string> = {
  BTC: '₿', ETH: 'Ξ', GOLD: '🥇', OIL: '🛢',
}

const AGREEMENT_BADGE: Record<string, string> = {
  high:   'bg-emerald-50 text-emerald-700 border border-emerald-200',
  medium: 'bg-amber-50 text-amber-700 border border-amber-200',
  low:    'bg-red-50 text-red-700 border border-red-200',
}

const BAR_COLOR: Record<string, string> = {
  BUY: 'bg-emerald-500', SELL: 'bg-red-500', HOLD: 'bg-amber-400',
}

export default function AssetCard({ asset, consensus }: AssetCardProps) {
  const signal = (consensus?.final_signal || 'HOLD').toUpperCase()
  const confidence = consensus?.confidence || 0
  const agreementLevel = consensus?.agreement_level || 'low'
  const emoji = ASSET_EMOJIS[asset.symbol] || '•'

  const isPositive24h = (asset.change_24h ?? 0) >= 0

  return (
    <div className="card p-5 flex flex-col gap-3 hover:border-indigo-200 group">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-slate-100 flex items-center justify-center text-lg border border-slate-200">
            {emoji}
          </div>
          <div>
            <p className="font-bold text-slate-900 text-base leading-tight">{asset.symbol}</p>
            <p className="text-slate-400 text-xs">{asset.name}</p>
          </div>
        </div>
        <SignalBadge signal={signal} size="md" />
      </div>

      {/* Price */}
      <div>
        <div className="text-2xl font-mono font-bold text-slate-900">
          {formatPrice(asset.price)}
        </div>
        <div className="flex gap-3 text-xs mt-1">
          <span className="text-slate-400">
            1h:&nbsp;
            <span className={(asset.change_1h ?? 0) >= 0 ? 'text-emerald-600 font-semibold' : 'text-red-600 font-semibold'}>
              {formatChange(asset.change_1h)}
            </span>
          </span>
          <span className="text-slate-400">
            24h:&nbsp;
            <span className={isPositive24h ? 'text-emerald-600 font-semibold' : 'text-red-600 font-semibold'}>
              {formatChange(asset.change_24h)}
            </span>
          </span>
        </div>
      </div>

      {/* AI Confidence section */}
      {consensus && (
        <div className="border-t border-slate-100 pt-3 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-500 font-medium">AI Confidence</span>
            <span className="font-bold text-slate-800">{(confidence * 100).toFixed(0)}%</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-1.5">
            <div
              className={`h-1.5 rounded-full transition-all duration-500 ${BAR_COLOR[signal] || BAR_COLOR.HOLD}`}
              style={{ width: `${confidence * 100}%` }}
            />
          </div>
          <div className="flex justify-between items-center">
            <span className="text-slate-400 text-xs">Agreement</span>
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${AGREEMENT_BADGE[agreementLevel] || AGREEMENT_BADGE.low}`}>
              {agreementLevel.toUpperCase()}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
