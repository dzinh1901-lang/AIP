'use client'
import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface TickerItem {
  symbol: string
  price: number
  change: number
  type: 'commodity' | 'crypto'
}

const initialMarkets: TickerItem[] = [
  { symbol: 'BTC/USD', price: 67420, change: 3.2, type: 'crypto' },
  { symbol: 'ETH/USD', price: 3580, change: 2.8, type: 'crypto' },
  { symbol: 'SOL/USD', price: 142.5, change: 5.2, type: 'crypto' },
  { symbol: 'XRP/USD', price: 0.582, change: 1.8, type: 'crypto' },
  { symbol: 'OIL/WTI', price: 85.2, change: 2.3, type: 'commodity' },
  { symbol: 'GOLD', price: 2150, change: 0.8, type: 'commodity' },
  { symbol: 'SILVER', price: 24.8, change: 1.5, type: 'commodity' },
  { symbol: 'NAT.GAS', price: 2.85, change: -0.9, type: 'commodity' },
  { symbol: 'BNB/USD', price: 412, change: 2.4, type: 'crypto' },
  { symbol: 'COPPER', price: 4.12, change: -0.8, type: 'commodity' },
]

function formatPrice(price: number): string {
  if (price < 1) return price.toFixed(4)
  if (price < 100) return price.toFixed(2)
  if (price < 10000) return price.toFixed(1)
  return price.toLocaleString('en-US', { maximumFractionDigits: 0 })
}

export default function MarketTicker() {
  const [markets, setMarkets] = useState<TickerItem[]>(initialMarkets)

  useEffect(() => {
    const interval = setInterval(() => {
      setMarkets(prev =>
        prev.map(item => ({
          ...item,
          price: item.price * (1 + (Math.random() - 0.5) * 0.002),
          change: item.change + (Math.random() - 0.5) * 0.1,
        }))
      )
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  const doubled = [...markets, ...markets]

  return (
    <div className="w-full overflow-hidden bg-bg-card border-y border-border-base py-2.5">
      {/* Label */}
      <div className="flex items-center">
        <div className="hidden sm:flex items-center gap-2 px-4 border-r border-border-base mr-4 flex-shrink-0">
          <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
          <span className="text-xs font-semibold text-text-muted uppercase tracking-wide whitespace-nowrap">
            Live
          </span>
        </div>
        <div
          className="flex gap-8 whitespace-nowrap"
          style={{
            animation: 'ticker 40s linear infinite',
            display: 'flex',
            width: 'max-content',
          }}
        >
          {doubled.map((item, index) => (
            <div key={`${item.symbol}-${index}`} className="flex items-center gap-2.5">
              <span className={`text-xs font-semibold px-1.5 py-0.5 rounded ${
                item.type === 'commodity'
                  ? 'bg-gold-light text-gold'
                  : 'bg-primary-light text-primary'
              }`}>
                {item.type === 'commodity' ? 'C' : 'Ξ'}
              </span>
              <span className="text-sm font-semibold text-text-base">{item.symbol}</span>
              <span className="text-sm text-text-base">${formatPrice(item.price)}</span>
              <span className={`flex items-center gap-0.5 text-xs font-semibold ${
                item.change >= 0 ? 'text-success' : 'text-danger'
              }`}>
                {item.change >= 0 ? (
                  <TrendingUp className="w-3 h-3" />
                ) : (
                  <TrendingDown className="w-3 h-3" />
                )}
                {Math.abs(item.change).toFixed(2)}%
              </span>
              <span className="text-border-base text-base select-none">·</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
