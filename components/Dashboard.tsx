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
  DollarSign,
  Signal,
  Globe2,
  Cpu,
  User,
  ChevronDown,
  Construction,
  Menu,
  X,
} from 'lucide-react'

const navItems = [
  { icon: LayoutDashboard, label: 'Overview', active: true },
  { icon: BarChart2, label: 'Markets', active: false },
  { icon: Activity, label: 'Analytics', active: false },
  { icon: Bell, label: 'Alerts', active: false },
  { icon: Settings, label: 'Settings', active: false },
]

const statCards = [
  {
    label: 'Portfolio Value',
    value: '$124,580',
    change: '+12.4%',
    positive: true,
    icon: DollarSign,
    color: 'from-accent-blue to-blue-600',
  },
  {
    label: 'Active Signals',
    value: '23',
    change: '+5 today',
    positive: true,
    icon: Signal,
    color: 'from-accent-purple to-purple-600',
  },
  {
    label: 'Markets Tracked',
    value: '204',
    change: 'All active',
    positive: true,
    icon: Globe2,
    color: 'from-accent-green to-green-600',
  },
  {
    label: 'AI Models Active',
    value: '52',
    change: 'Full consensus',
    positive: true,
    icon: Cpu,
    color: 'from-orange-400 to-orange-600',
  },
]

const tableAssets = [
  { name: 'Bitcoin', symbol: 'BTC', price: '$67,420', change: '+3.2%', positive: true, marketCap: '$1.32T', volume: '$38.2B' },
  { name: 'Ethereum', symbol: 'ETH', price: '$3,580', change: '+2.8%', positive: true, marketCap: '$430B', volume: '$18.4B' },
  { name: 'WTI Crude Oil', symbol: 'OIL', price: '$85.20', change: '+2.3%', positive: true, marketCap: 'N/A', volume: '$12.1B' },
  { name: 'Gold', symbol: 'XAU', price: '$2,150', change: '+0.8%', positive: true, marketCap: 'N/A', volume: '$8.7B' },
  { name: 'Solana', symbol: 'SOL', price: '$142.50', change: '+5.2%', positive: true, marketCap: '$62.4B', volume: '$4.1B' },
  { name: 'Silver', symbol: 'XAG', price: '$24.80', change: '+1.5%', positive: true, marketCap: 'N/A', volume: '$2.3B' },
  { name: 'XRP', symbol: 'XRP', price: '$0.582', change: '+1.8%', positive: true, marketCap: '$31.8B', volume: '$1.9B' },
  { name: 'Natural Gas', symbol: 'NGAS', price: '$2.85', change: '-0.9%', positive: false, marketCap: 'N/A', volume: '$1.1B' },
]

export default function Dashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-bg-primary flex">
      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-bg-secondary border-r border-white/5 transform transition-transform duration-300 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:relative lg:translate-x-0 flex flex-col`}
      >
        <div className="p-6 border-b border-white/5">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold gradient-text">AIP</span>
          </Link>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => (
            <button
              key={item.label}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                item.active
                  ? 'bg-accent-blue/10 text-accent-blue border border-accent-blue/20'
                  : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'
              }`}
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-white/5">
          <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/5 cursor-pointer">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
            <div>
              <div className="text-white text-sm font-medium">Demo User</div>
              <div className="text-gray-600 text-xs">demo@aip.io</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Navbar */}
        <header className="h-16 border-b border-white/5 bg-bg-secondary flex items-center justify-between px-6">
          <button
            className="lg:hidden text-gray-500 hover:text-white"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>

          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-accent-green animate-pulse" />
            <span className="text-gray-400 text-sm">All systems operational</span>
          </div>

          <div className="flex items-center gap-4">
            <button className="relative text-gray-500 hover:text-white">
              <Bell className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-accent-red rounded-full text-[8px] flex items-center justify-center text-white">3</span>
            </button>
            <div className="flex items-center gap-2 cursor-pointer hover:text-white text-gray-400 transition-colors">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
              <span className="text-sm text-gray-300">Demo User</span>
              <ChevronDown className="w-4 h-4" />
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <main className="flex-1 p-6 overflow-auto">
          {/* Under construction banner */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 glass-card rounded-xl p-4 border border-accent-purple/30 flex items-center gap-3"
          >
            <Construction className="w-5 h-5 text-accent-purple flex-shrink-0" />
            <div>
              <span className="text-accent-purple font-semibold">Dashboard Under Construction</span>
              <span className="text-gray-400 text-sm ml-2">
                Full analytics, AI signals, and market intelligence features coming soon.
              </span>
            </div>
          </motion.div>

          {/* Page title */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-white">Overview</h1>
            <p className="text-gray-500 text-sm mt-1">Welcome back, Demo User</p>
          </div>

          {/* Stat Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-8">
            {statCards.map((card, index) => (
              <motion.div
                key={card.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="glass-card rounded-xl p-5"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-gray-500 text-sm">{card.label}</span>
                  <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${card.color} flex items-center justify-center`}>
                    <card.icon className="w-4 h-4 text-white" />
                  </div>
                </div>
                <div className="text-2xl font-bold text-white mb-1">{card.value}</div>
                <div className={`text-xs font-medium flex items-center gap-1 ${card.positive ? 'text-accent-green' : 'text-accent-red'}`}>
                  {card.positive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                  {card.change}
                </div>
              </motion.div>
            ))}
          </div>

          {/* Markets Table */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="glass-card rounded-xl overflow-hidden"
          >
            <div className="p-5 border-b border-white/5 flex items-center justify-between">
              <h2 className="text-white font-semibold">Markets</h2>
              <span className="text-xs text-accent-blue bg-accent-blue/10 border border-accent-blue/20 rounded-full px-3 py-1">
                Live
              </span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/5">
                    <th className="text-left py-3 px-5 text-gray-500 text-xs font-medium uppercase">Asset</th>
                    <th className="text-right py-3 px-5 text-gray-500 text-xs font-medium uppercase">Price</th>
                    <th className="text-right py-3 px-5 text-gray-500 text-xs font-medium uppercase">24h Change</th>
                    <th className="text-right py-3 px-5 text-gray-500 text-xs font-medium uppercase hidden md:table-cell">Market Cap</th>
                    <th className="text-right py-3 px-5 text-gray-500 text-xs font-medium uppercase hidden lg:table-cell">Volume</th>
                  </tr>
                </thead>
                <tbody>
                  {tableAssets.map((asset) => (
                    <tr
                      key={asset.symbol}
                      className="border-b border-white/5 hover:bg-white/2 transition-colors"
                    >
                      <td className="py-4 px-5">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-accent-blue/20 to-accent-purple/20 border border-white/10 flex items-center justify-center text-xs font-bold text-accent-blue">
                            {asset.symbol.slice(0, 2)}
                          </div>
                          <div>
                            <div className="text-white text-sm font-medium">{asset.name}</div>
                            <div className="text-gray-600 text-xs">{asset.symbol}</div>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-5 text-right text-white text-sm font-medium">{asset.price}</td>
                      <td className="py-4 px-5 text-right">
                        <span className={`text-sm font-medium flex items-center justify-end gap-1 ${asset.positive ? 'text-accent-green' : 'text-accent-red'}`}>
                          {asset.positive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                          {asset.change}
                        </span>
                      </td>
                      <td className="py-4 px-5 text-right text-gray-500 text-sm hidden md:table-cell">{asset.marketCap}</td>
                      <td className="py-4 px-5 text-right text-gray-500 text-sm hidden lg:table-cell">{asset.volume}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        </main>
      </div>
    </div>
  )
}
