'use client'

import SignalBadge from './SignalBadge'

interface ModelResult {
  signal: string
  confidence: number
  reasoning: string[]
}

interface ConsensusData {
  asset: string
  final_signal: string
  confidence: number
  agreement_level: string
  models?: Record<string, ModelResult>
  dissenting_models?: string[]
}

interface ConsensusViewProps {
  consensus: ConsensusData[]
}

const MODEL_ICONS: Record<string, string> = {
  openai: '🤖',
  claude: '🧠',
  gemini: '💎',
  consensus: '⚖️',
}

const MODEL_LABELS: Record<string, string> = {
  openai: 'GPT-5.4',
  claude: 'Claude Opus 4.6',
  gemini: 'Gemini 3.1 Pro',
  consensus: 'Consensus',
}

const MODEL_COLORS: Record<string, string> = {
  openai: 'border-violet-200 bg-violet-50',
  claude: 'border-orange-200 bg-orange-50',
  gemini: 'border-sky-200 bg-sky-50',
  consensus: 'border-indigo-300 bg-indigo-50 ring-1 ring-indigo-200',
}

const MODEL_ICON_BG: Record<string, string> = {
  openai: 'bg-violet-100 text-violet-700',
  claude: 'bg-orange-100 text-orange-700',
  gemini: 'bg-sky-100 text-sky-700',
  consensus: 'bg-indigo-100 text-indigo-700',
}

const AGREEMENT_STYLES: Record<string, string> = {
  high:   'bg-emerald-100 text-emerald-700 border border-emerald-200',
  medium: 'bg-amber-100 text-amber-700 border border-amber-200',
  low:    'bg-red-100 text-red-700 border border-red-200',
}

const BAR_COLOR: Record<string, string> = {
  BUY: 'bg-emerald-500', SELL: 'bg-red-500', HOLD: 'bg-amber-400',
}

function ModelVoteCard({ modelName, result, isFinal = false }: {
  modelName: string
  result: ModelResult
  isFinal?: boolean
}) {
  const sig = (result.signal || 'HOLD').toUpperCase()
  const pct = (result.confidence * 100).toFixed(0)

  return (
    <div className={`rounded-xl border p-3 flex flex-col gap-2 transition-all ${MODEL_COLORS[modelName] || 'border-slate-200 bg-slate-50'}`}>
      {/* Model header */}
      <div className="flex items-center gap-2">
        <span className={`w-7 h-7 rounded-lg flex items-center justify-center text-sm font-bold flex-shrink-0 ${MODEL_ICON_BG[modelName] || 'bg-slate-100 text-slate-600'}`}>
          {MODEL_ICONS[modelName] || '🤖'}
        </span>
        <div className="min-w-0 flex-1">
          <p className="text-xs font-bold text-slate-700 truncate">
            {MODEL_LABELS[modelName] || modelName}
          </p>
          {isFinal && (
            <p className="text-[10px] text-indigo-500 font-semibold uppercase tracking-wide">Final Vote</p>
          )}
        </div>
      </div>

      {/* Signal + confidence */}
      <div className="flex items-center gap-2">
        <SignalBadge signal={sig} size="sm" />
        <span className="text-xs font-semibold text-slate-600">{pct}%</span>
      </div>

      {/* Confidence bar */}
      <div className="w-full bg-white/70 rounded-full h-1">
        <div
          className={`h-1 rounded-full transition-all duration-500 ${BAR_COLOR[sig] || BAR_COLOR.HOLD}`}
          style={{ width: `${result.confidence * 100}%` }}
        />
      </div>

      {/* Top reasoning point */}
      {result.reasoning && result.reasoning[0] && (
        <p className="text-[10px] text-slate-500 leading-snug line-clamp-2">
          {result.reasoning[0]}
        </p>
      )}
    </div>
  )
}

function AssetConsensusBlock({ item }: { item: ConsensusData }) {
  const sig = (item.final_signal || 'HOLD').toUpperCase()
  const models = Object.entries(item.models || {})

  return (
    <div className="border border-slate-200 rounded-xl overflow-hidden">
      {/* Asset header strip */}
      <div className="flex items-center justify-between px-4 py-3 bg-slate-50 border-b border-slate-200">
        <div className="flex items-center gap-2.5">
          <span className="font-bold text-slate-900 text-sm">{item.asset}</span>
          <SignalBadge signal={sig} size="md" />
        </div>
        <div className="flex items-center gap-3">
          <div className="text-right">
            <p className="text-[10px] text-slate-400 uppercase tracking-wide">Confidence</p>
            <p className="text-sm font-bold text-slate-800">{(item.confidence * 100).toFixed(0)}%</p>
          </div>
          <span className={`text-[10px] font-bold px-2 py-1 rounded-full ${AGREEMENT_STYLES[item.agreement_level] || AGREEMENT_STYLES.low}`}>
            {item.agreement_level?.toUpperCase()} AGREEMENT
          </span>
        </div>
      </div>

      {/* Model voting cards grid */}
      <div className="p-3 bg-white">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {models.map(([model, result]) => (
            <ModelVoteCard key={model} modelName={model} result={result} />
          ))}
          <ModelVoteCard
            modelName="consensus"
            isFinal
            result={{
              signal: item.final_signal,
              confidence: item.confidence,
              reasoning: [
                item.dissenting_models && item.dissenting_models.length > 0
                  ? `Dissent from: ${item.dissenting_models.join(', ')}`
                  : 'All models aligned',
              ],
            }}
          />
        </div>
      </div>
    </div>
  )
}

export default function ConsensusView({ consensus }: ConsensusViewProps) {
  if (!consensus || consensus.length === 0) {
    return (
      <div className="card p-5">
        <div className="flex items-center gap-2 mb-4">
          <span className="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-600 flex items-center justify-center text-sm">⚖️</span>
          <h2 className="font-bold text-slate-900">AI Consensus</h2>
        </div>
        <div className="text-center text-slate-400 text-sm py-8">
          Awaiting model consensus…
        </div>
      </div>
    )
  }

  return (
    <div className="card p-5">
      <div className="flex items-center gap-2 mb-4">
        <span className="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-600 flex items-center justify-center text-sm">⚖️</span>
        <div>
          <h2 className="font-bold text-slate-900 leading-tight">AI Consensus</h2>
          <p className="text-xs text-slate-400">Multi-model debate &amp; voting</p>
        </div>
      </div>
      <div className="space-y-3">
        {consensus.map((item) => (
          <AssetConsensusBlock key={item.asset} item={item} />
        ))}
      </div>
    </div>
  )
}
