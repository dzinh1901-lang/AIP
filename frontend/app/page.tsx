'use client'

import { useEffect, useState, useCallback } from 'react'
import AssetCard from './components/AssetCard'
import AlertFeed from './components/AlertFeed'
import AnalyticsPanel from './components/AnalyticsPanel'
import ConsensusView from './components/ConsensusView'
import BriefPanel from './components/BriefPanel'
import AgentsPanel from './components/AgentsPanel'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const REFRESH_DELAY_MS = 3000
const BRIEF_GENERATION_DELAY_MS = 5000

function authHeaders(): HeadersInit {
  if (typeof window === 'undefined') return {}
  const token = localStorage.getItem('aip_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

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

interface MarketContext {
  usd_index?: number
  bond_yield_10y?: number
  vix?: number
  news_sentiment?: number
  on_chain_activity?: number
}

interface Brief {
  content: string
  key_signals?: { asset: string; signal: string; confidence: number }[]
  risks?: string[]
  date?: string
}

interface FullData {
  assets: Asset[]
  context: MarketContext | null
  signals: unknown[]
  consensus: Consensus[]
  alerts: unknown[]
  model_outputs: unknown[]
}

function formatNumber(n?: number, decimals = 2): string {
  if (n == null) return '—'
  return n.toFixed(decimals)
}

// ── Contrast Zone 1: Top navigation bar ──────────────────────────────────────
function TopBar({ context, lastUpdated, onRefresh, refreshing }: {
  context: MarketContext | null
  lastUpdated: Date | null
  onRefresh: () => void
  refreshing: boolean
}) {
  const sentimentLabel = (s?: number) => {
    if (s == null) return '—'
    if (s > 0.1) return 'Positive'
    if (s < -0.1) return 'Negative'
    return 'Neutral'
  }
  const sentimentColor = (s?: number) => {
    if (s == null) return 'text-slate-400'
    if (s > 0.1) return 'text-emerald-600'
    if (s < -0.1) return 'text-red-600'
    return 'text-amber-600'
  }

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
      <div className="max-w-screen-2xl mx-auto px-5 h-14 flex items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center gap-3 flex-shrink-0">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center shadow-sm">
            <span className="text-white text-xs font-black tracking-tight">AIP</span>
          </div>
          <div className="hidden sm:block">
            <p className="font-bold text-slate-900 text-sm leading-tight">AIP</p>
            <p className="text-slate-400 text-[10px] leading-tight">Market Intelligence Platform</p>
          </div>
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse ml-1" title="Live" />
        </div>

        {/* Market macro strip */}
        <div className="hidden md:flex items-center gap-4 text-xs flex-1 justify-center">
          {context?.usd_index != null && (
            <span className="flex items-center gap-1 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1">
              <span className="text-slate-400 font-medium">DXY</span>
              <span className="font-mono font-bold text-slate-700">{formatNumber(context.usd_index)}</span>
            </span>
          )}
          {context?.bond_yield_10y != null && (
            <span className="flex items-center gap-1 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1">
              <span className="text-slate-400 font-medium">10Y</span>
              <span className="font-mono font-bold text-slate-700">{formatNumber(context.bond_yield_10y)}%</span>
            </span>
          )}
          {context?.vix != null && (
            <span className="flex items-center gap-1 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1">
              <span className="text-slate-400 font-medium">VIX</span>
              <span className="font-mono font-bold text-slate-700">{formatNumber(context.vix, 1)}</span>
            </span>
          )}
          {context?.news_sentiment != null && (
            <span className="flex items-center gap-1 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1">
              <span className="text-slate-400 font-medium">Sentiment</span>
              <span className={`font-semibold ${sentimentColor(context.news_sentiment)}`}>
                {sentimentLabel(context.news_sentiment)}
              </span>
            </span>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {lastUpdated && (
            <span className="hidden sm:block text-[10px] text-slate-400">
              {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          <a
            href="/login"
            className="px-3 py-1.5 text-xs rounded-lg border border-slate-200 text-slate-500 hover:border-indigo-300 hover:text-indigo-600 font-medium transition-colors"
          >
            Sign in
          </a>
          <button
            onClick={onRefresh}
            disabled={refreshing}
            className="px-3 py-1.5 text-xs rounded-lg bg-indigo-600 text-white font-semibold hover:bg-indigo-700 transition-colors disabled:opacity-50"
          >
            {refreshing ? '⟳ Refreshing…' : '⟳ Refresh'}
          </button>
        </div>
      </div>
    </header>
  )
}

// ── Contrast Zone 2: Hero stats strip ────────────────────────────────────────
function StatsStrip({ assets, consensus }: { assets: Asset[]; consensus: Consensus[] }) {
  const buyCount  = consensus.filter(c => c.final_signal?.toUpperCase() === 'BUY').length
  const sellCount = consensus.filter(c => c.final_signal?.toUpperCase() === 'SELL').length
  const holdCount = consensus.filter(c => c.final_signal?.toUpperCase() === 'HOLD').length
  const avgConf   = consensus.length
    ? consensus.reduce((a, c) => a + (c.confidence || 0), 0) / consensus.length
    : 0

  const stats = [
    { label: 'Tracked Assets', value: assets.length.toString(), sub: 'crypto + commodities' },
    { label: 'BUY Signals',    value: buyCount.toString(),  sub: 'bullish consensus',  color: 'text-emerald-600' },
    { label: 'SELL Signals',   value: sellCount.toString(), sub: 'bearish consensus',  color: 'text-red-600' },
    { label: 'HOLD Signals',   value: holdCount.toString(), sub: 'neutral consensus',  color: 'text-amber-600' },
    { label: 'Avg. AI Conf.',  value: `${(avgConf * 100).toFixed(0)}%`, sub: 'multi-model mean' },
  ]

  return (
    <div className="bg-gradient-to-r from-indigo-600 to-violet-600 text-white">
      <div className="max-w-screen-2xl mx-auto px-5 py-4">
        <div className="flex items-center justify-between flex-wrap gap-3">
          {stats.map((s, i) => (
            <div key={i} className="text-center min-w-[80px]">
              <p className={`text-2xl font-black ${s.color || 'text-white'}`}>{s.value}</p>
              <p className="text-xs font-semibold text-indigo-200">{s.label}</p>
              <p className="text-[10px] text-indigo-300">{s.sub}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function Home() {
  const [data, setData]             = useState<FullData | null>(null)
  const [brief, setBrief]           = useState<Brief | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [loading, setLoading]       = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [briefLoading, setBriefLoading] = useState(false)
  const [error, setError]           = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/full`, { headers: authHeaders() })
      if (!res.ok) throw new Error(`API error ${res.status}`)
      const json = await res.json()
      setData(json)
      setLastUpdated(new Date())
      setError(null)
    } catch {
      setError('Cannot connect to backend API. Make sure it is running.')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  const fetchBrief = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/brief`, { headers: authHeaders() })
      if (res.ok) setBrief(await res.json())
    } catch {}
  }, [])

  const handleRefresh = useCallback(async () => {
    setRefreshing(true)
    await fetch(`${API_URL}/api/refresh`, {
      method: 'POST',
      headers: authHeaders(),
    }).catch(() => {})
    setTimeout(fetchData, REFRESH_DELAY_MS)
  }, [fetchData])

  const handleGenerateBrief = useCallback(async () => {
    setBriefLoading(true)
    await fetch(`${API_URL}/api/brief/generate`, {
      method: 'POST',
      headers: authHeaders(),
    }).catch(() => {})
    setTimeout(async () => {
      await fetchBrief()
      setBriefLoading(false)
    }, BRIEF_GENERATION_DELAY_MS)
  }, [fetchBrief])

  useEffect(() => {
    fetchData()
    fetchBrief()
    const interval = setInterval(fetchData, 60000)
    return () => clearInterval(interval)
  }, [fetchData, fetchBrief])

  const consensus = data?.consensus || []

  return (
    <div className="min-h-screen" style={{ background: 'var(--color-bg)' }}>
      {/* Zone 1 – Sticky top nav */}
      <TopBar
        context={data?.context || null}
        lastUpdated={lastUpdated}
        onRefresh={handleRefresh}
        refreshing={refreshing}
      />

      {/* Zone 2 – Indigo hero stats strip (only when data loaded) */}
      {!loading && data && (
        <StatsStrip assets={data.assets} consensus={consensus} />
      )}

      {/* Zone 3 – Main light dashboard */}
      <main className="max-w-screen-2xl mx-auto px-4 py-6 space-y-6">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm flex items-start gap-2">
            <span className="text-red-500 mt-0.5">⚠️</span>
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin w-10 h-10 border-2 border-indigo-500 border-t-transparent rounded-full mx-auto mb-3" />
              <p className="text-slate-500 text-sm font-medium">Loading market intelligence…</p>
            </div>
          </div>
        ) : (
          <>
            {/* Row 1 – Asset Grid + Alert Feed */}
            <section>
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
                <div className="lg:col-span-3">
                  <p className="section-label mb-3">Assets</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
                    {(data?.assets || []).map(asset => (
                      <AssetCard
                        key={asset.symbol}
                        asset={asset}
                        consensus={consensus.find(c => c.asset === asset.symbol)}
                      />
                    ))}
                  </div>
                </div>
                <div className="lg:col-span-1">
                  <p className="section-label mb-3">Alerts</p>
                  <div className="h-80 lg:h-[calc(100%-2rem)]">
                    <AlertFeed apiUrl={API_URL} />
                  </div>
                </div>
              </div>
            </section>

            {/* Row 2 – Analytics + AI Consensus Cards */}
            <section>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <AnalyticsPanel
                  apiUrl={API_URL}
                  symbols={(data?.assets || []).map(a => a.symbol)}
                />
                <ConsensusView consensus={consensus} />
              </div>
            </section>

            {/* Zone 4 – Dark contrast strip: Daily Intelligence Brief */}
            <section className="rounded-2xl overflow-hidden border border-slate-700">
              <div className="bg-slate-900 px-5 py-3 flex items-center justify-between border-b border-slate-800">
                <p className="section-label text-slate-400">Daily Intelligence Brief</p>
                <button
                  onClick={handleGenerateBrief}
                  disabled={briefLoading}
                  className="px-3 py-1.5 text-xs rounded-lg bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 hover:bg-indigo-500/30 font-semibold transition-colors disabled:opacity-50"
                >
                  {briefLoading ? '⟳ Generating…' : '✦ Generate Brief'}
                </button>
              </div>
              <BriefPanel brief={brief} loading={briefLoading} />
            </section>

            {/* Row 4 – Model Performance table */}
            <ModelPerformancePanel apiUrl={API_URL} />

            {/* Row 5 – AI Agent Team */}
            <AgentsPanel apiUrl={API_URL} />
          </>
        )}
      </main>
    </div>
  )
}

// ── Model Performance panel ───────────────────────────────────────────────────

function ModelPerformancePanel({ apiUrl }: { apiUrl: string }) {
  const [perf, setPerf] = useState<{
    model_name: string; asset: string; total_predictions: number;
    accuracy: number; weight: number
  }[]>([])

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`${apiUrl}/api/performance`)
        if (res.ok) setPerf(await res.json())
      } catch {}
    }
    load()
    const interval = setInterval(load, 30000)
    return () => clearInterval(interval)
  }, [apiUrl])

  if (perf.length === 0) return null

  return (
    <div className="card p-5">
      <div className="flex items-center gap-2 mb-4">
        <span className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center text-sm border border-amber-200">📈</span>
        <div>
          <h2 className="font-bold text-slate-900 leading-tight">Model Performance &amp; Weights</h2>
          <p className="text-xs text-slate-400">Live accuracy tracking across AI models</p>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-100">
              <th className="section-label text-left py-2 pr-4">Model</th>
              <th className="section-label text-left py-2 pr-4">Asset</th>
              <th className="section-label text-right py-2 pr-4">Predictions</th>
              <th className="section-label text-right py-2 pr-4">Accuracy</th>
              <th className="section-label text-right py-2">Weight</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {perf.map((p, i) => (
              <tr key={i} className="text-slate-700 hover:bg-slate-50 transition-colors">
                <td className="py-2.5 pr-4 font-semibold capitalize text-slate-900">{p.model_name}</td>
                <td className="py-2.5 pr-4 text-slate-500">{p.asset}</td>
                <td className="py-2.5 pr-4 text-right font-mono text-slate-700">{p.total_predictions}</td>
                <td className="py-2.5 pr-4 text-right font-mono text-slate-700">{(p.accuracy * 100).toFixed(1)}%</td>
                <td className="py-2.5 text-right font-mono">
                  <span className={
                    p.weight > 1 ? 'text-emerald-600 font-bold' :
                    p.weight < 1 ? 'text-red-600 font-bold' :
                    'text-slate-400'
                  }>
                    {p.weight.toFixed(2)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
