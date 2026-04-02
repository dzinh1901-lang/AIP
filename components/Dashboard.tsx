'use client'
import { useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import {
  Zap,
  LayoutDashboard,
  BarChart2,
  Activity,
  Bell,
  Settings,
  TrendingUp,
  TrendingDown,
  Signal,
  Globe2,
  Cpu,
  Menu,
  X,
  ChevronRight,
  Newspaper,
  AlertCircle,
} from 'lucide-react'
import AIConsensusCard, { sampleConsensusData } from './AIConsensusCard'

const navItems = [
  { icon: LayoutDashboard, label: 'Overview', active: true },
  { icon: BarChart2, label: 'Markets', active: false },
  { icon: Activity, label: 'Analytics', active: false },
  { icon: Bell, label: 'Alerts', active: false },
  { icon: Settings, label: 'Settings', active: false },
]

const mvpAssets: Array<{
  name: string
  symbol: string
  price: number
  change: number
  positive: boolean
  signal: 'BUY' | 'HOLD' | 'SELL'
  confidence: number
}> = [
  {
    name: 'Bitcoin',
    symbol: 'BTC',
    price: 67420,
    change: 3.2,
    positive: true,
    signal: 'BUY' as const,
    confidence: 68,
  },
  {
    name: 'Ethereum',
    symbol: 'ETH',
    price: 3580,
    change: 2.8,
    positive: true,
    signal: 'BUY' as const,
    confidence: 71,
  },
  {
    name: 'WTI Crude Oil',
    symbol: 'OIL',
    price: 85.2,
    change: 2.3,
    positive: true,
    signal: 'HOLD' as const,
    confidence: 55,
  },
  {
    name: 'Gold',
    symbol: 'XAU',
    price: 2150,
    change: 0.8,
    positive: true,
    signal: 'BUY' as const,
    confidence: 74,
  },
]

const liveAlerts = [
  {
    type: 'signal',
    asset: 'BTC',
    message: 'Consensus shifted to BUY — 3 of 3 models aligned',
    time: '2m ago',
    severity: 'success',
  },
  {
    type: 'price',
    asset: 'GOLD',
    message: 'Gold broke $2,150 resistance — watching for continuation',
    time: '8m ago',
    severity: 'info',
  },
  {
    type: 'macro',
    asset: 'OIL',
    message: 'Mixed consensus on Oil — models diverging on supply data',
    time: '15m ago',
    severity: 'warning',
  },
  {
    type: 'signal',
    asset: 'ETH',
    message: 'High-conviction BUY signal — DeFi activity spiking',
    time: '22m ago',
    severity: 'success',
  },
]

const dailyBriefs = [
  {
    title: 'BTC holding above 200-day MA',
    body: 'On-chain accumulation patterns remain strong. Institutional flow positive for the third consecutive week.',
    asset: 'BTC',
    time: 'Today, 08:00',
  },
  {
    title: 'Gold approaching $2,200 target',
    body: 'Dollar weakness and geopolitical tensions continuing to support safe-haven demand. AI models at 74% buy confidence.',
    asset: 'GOLD',
    time: 'Today, 06:30',
  },
  {
    title: 'Oil consensus split — wait for data',
    body: 'Rising inventory data conflicts with strong industrial demand signals. Models suggest holding until EIA report.',
    asset: 'OIL',
    time: 'Yesterday',
  },
]

const alertSeverityStyles: Record<string, string> = {
  success: 'bg-success-light text-success border-success/20',
  info: 'bg-primary-light text-primary border-primary/20',
  warning: 'bg-gold-light text-gold border-gold/20',
  danger: 'bg-danger-light text-danger border-danger/20',
}

const signalBadgeStyle: Record<string, string> = {
  BUY: 'badge-buy',
  SELL: 'badge-sell',
  HOLD: 'badge-hold',
}

function formatPrice(p: number) {
  if (p < 100) return `$${p.toFixed(2)}`
  return `$${p.toLocaleString('en-US', { maximumFractionDigits: 0 })}`
}

export default function Dashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-bg-base flex">
      {/* ── Sidebar (Light Zone) ── */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-60 bg-bg-card border-r border-border-base flex flex-col transform transition-transform duration-300 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:relative lg:translate-x-0`}
      >
        {/* Logo */}
        <div className="h-16 px-5 border-b border-border-base flex items-center">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center">
              <Zap className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="text-lg font-bold text-primary-gradient">AIP</span>
          </Link>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-0.5">
          {navItems.map((item) => (
            <button
              key={item.label}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                item.active
                  ? 'bg-primary-light text-primary'
                  : 'text-text-muted hover:text-text-base hover:bg-bg-base'
              }`}
            >
              <item.icon className="w-4 h-4 flex-shrink-0" />
              {item.label}
            </button>
          ))}
        </nav>

        {/* Status */}
        <div className="px-5 py-4 border-t border-border-base">
          <div className="flex items-center gap-2 text-xs text-text-muted">
            <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
            All systems live
          </div>
        </div>
      </aside>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* ── Main ── */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar (Light Zone) */}
        <header className="h-16 bg-bg-card border-b border-border-base flex items-center justify-between px-5 gap-4">
          <button
            className="lg:hidden text-text-muted hover:text-text-base"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label="Toggle sidebar"
          >
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>

          {/* Market pulse pills */}
          <div className="hidden md:flex items-center gap-2 overflow-x-auto">
            {mvpAssets.map((a) => (
              <div key={a.symbol} className="flex items-center gap-1.5 light-card rounded-full px-3 py-1">
                <span className="text-xs font-bold text-text-base">{a.symbol}</span>
                <span className="text-xs text-text-muted">{formatPrice(a.price)}</span>
                <span className={`text-xs font-semibold ${a.positive ? 'text-success' : 'text-danger'}`}>
                  {a.positive ? '+' : ''}{a.change.toFixed(1)}%
                </span>
              </div>
            ))}
          </div>

          <div className="flex items-center gap-3 ml-auto">
            <button className="relative text-text-muted hover:text-text-base">
              <Bell className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-danger rounded-full text-[9px] flex items-center justify-center text-white font-bold">3</span>
            </button>
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-full bg-primary flex items-center justify-center text-white text-xs font-bold">
                D
              </div>
              <span className="text-sm text-text-base font-medium hidden sm:block">Demo</span>
            </div>
          </div>
        </header>

        {/* ── Dashboard Content ── */}
        <main className="flex-1 overflow-auto">

          {/* ── Section 1: Asset Overview Grid (Light Zone) ── */}
          <div className="p-5 border-b border-border-base">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-xl font-bold text-text-base">Overview</h1>
                <p className="text-sm text-text-muted">Today, {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
                <span className="text-xs text-text-muted font-medium">Live</span>
              </div>
            </div>

            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {mvpAssets.map((asset, i) => (
                <motion.div
                  key={asset.symbol}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.07 }}
                  className="light-card light-card-hover rounded-xl p-4"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <div className="text-xs text-text-muted">{asset.name}</div>
                      <div className="font-bold text-text-base text-sm">{asset.symbol}</div>
                    </div>
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${signalBadgeStyle[asset.signal]}`}>
                      {asset.signal}
                    </span>
                  </div>
                  <div className="text-2xl font-bold text-text-base mb-1">{formatPrice(asset.price)}</div>
                  <div className={`flex items-center gap-1 text-xs font-semibold ${asset.positive ? 'text-success' : 'text-danger'}`}>
                    {asset.positive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                    {asset.positive ? '+' : ''}{asset.change}% today
                  </div>
                  <div className="mt-3">
                    <div className="flex justify-between text-xs text-text-muted mb-1">
                      <span>AI Confidence</span>
                      <span>{asset.confidence}%</span>
                    </div>
                    <div className="consensus-bar">
                      <motion.div
                        className={`consensus-bar-fill ${asset.signal === 'BUY' ? 'bg-success' : asset.signal === 'SELL' ? 'bg-danger' : 'bg-gold'}`}
                        initial={{ width: 0 }}
                        animate={{ width: `${asset.confidence}%` }}
                        transition={{ duration: 0.7, delay: 0.3 + i * 0.07 }}
                      />
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* ── Section 2: AI Consensus + Live Alerts (mixed zones) ── */}
          <div className="grid lg:grid-cols-3 gap-0 border-b border-border-base">
            {/* AI Consensus Cards — Light */}
            <div className="lg:col-span-2 p-5 border-r border-border-base">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-primary" />
                  <h2 className="font-bold text-text-base">AI Consensus</h2>
                </div>
                <span className="text-xs text-text-muted">4 assets · updated live</span>
              </div>
              <div className="grid sm:grid-cols-2 gap-4">
                {sampleConsensusData.map((d, i) => (
                  <motion.div
                    key={d.asset}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 + i * 0.08 }}
                  >
                    <AIConsensusCard data={d} />
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Live Alerts — Light */}
            <div className="p-5">
              <div className="flex items-center gap-2 mb-4">
                <Bell className="w-4 h-4 text-primary" />
                <h2 className="font-bold text-text-base">Live Alerts</h2>
                <span className="ml-auto text-xs bg-danger-light text-danger font-semibold px-2 py-0.5 rounded-full">
                  {liveAlerts.length} new
                </span>
              </div>
              <div className="space-y-3">
                {liveAlerts.map((alert, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.15 + i * 0.07 }}
                    className={`rounded-xl p-3 border ${alertSeverityStyles[alert.severity]}`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-1.5 mb-0.5">
                          <AlertCircle className="w-3 h-3 flex-shrink-0" />
                          <span className="font-semibold text-xs">{alert.asset}</span>
                        </div>
                        <p className="text-xs leading-relaxed">{alert.message}</p>
                      </div>
                    </div>
                    <div className="text-xs mt-1.5 opacity-60">{alert.time}</div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>

          {/* ── Section 3: Analytics Panel (Dark Zone) ── */}
          <div className="dark-panel border-b border-dark-border p-5">
            <div className="flex items-center gap-2 mb-5">
              <Activity className="w-4 h-4 text-primary" />
              <h2 className="font-bold text-white">Analytics Panel</h2>
              <span className="ml-2 text-xs bg-white/10 text-white/60 px-2 py-0.5 rounded-full">
                Deep analysis zone
              </span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
              {[
                { icon: Signal, label: 'Active Signals', value: '23', sub: '+5 today', color: 'text-primary' },
                { icon: Globe2, label: 'Markets Live', value: '4', sub: 'MVP scope', color: 'text-gold' },
                { icon: Cpu, label: 'AI Models', value: '52', sub: 'Full consensus', color: 'text-success' },
                { icon: TrendingUp, label: 'Hit Rate (7d)', value: '71%', sub: 'BUY signals', color: 'text-success' },
              ].map(({ icon: Icon, label, value, sub, color }, i) => (
                <motion.div
                  key={label}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 + i * 0.06 }}
                  className="dark-panel-card rounded-xl p-4"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Icon className={`w-4 h-4 ${color}`} />
                    <span className="text-white/50 text-xs">{label}</span>
                  </div>
                  <div className="text-2xl font-bold text-white">{value}</div>
                  <div className={`text-xs mt-1 ${color}`}>{sub}</div>
                </motion.div>
              ))}
            </div>

            {/* Placeholder chart area */}
            <div className="dark-panel-card rounded-xl p-5 flex items-center justify-center h-32">
              <div className="text-center">
                <BarChart2 className="w-8 h-8 text-white/20 mx-auto mb-2" />
                <p className="text-white/30 text-sm">Interactive charts — coming next</p>
              </div>
            </div>
          </div>

          {/* ── Section 4: Daily Brief (Light Zone) ── */}
          <div className="p-5">
            <div className="flex items-center gap-2 mb-4">
              <Newspaper className="w-4 h-4 text-primary" />
              <h2 className="font-bold text-text-base">Daily Brief</h2>
              <span className="ml-auto text-xs text-text-muted">AI-generated · updated at 08:00</span>
            </div>
            <div className="grid md:grid-cols-3 gap-4">
              {dailyBriefs.map((brief, i) => (
                <motion.div
                  key={brief.title}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 + i * 0.07 }}
                  className="light-card light-card-hover rounded-xl p-4"
                >
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div>
                      <span className="text-xs font-semibold text-primary bg-primary-light px-2 py-0.5 rounded-full">{brief.asset}</span>
                    </div>
                    <span className="text-xs text-text-muted flex-shrink-0">{brief.time}</span>
                  </div>
                  <h3 className="text-sm font-bold text-text-base mb-2">{brief.title}</h3>
                  <p className="text-xs text-text-muted leading-relaxed">{brief.body}</p>
                  <button className="mt-3 flex items-center gap-1 text-xs text-primary font-medium hover:underline">
                    Read more <ChevronRight className="w-3 h-3" />
                  </button>
                </motion.div>
              ))}
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
