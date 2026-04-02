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
  { symbol: 'NAT.GAS', price: 2.85, change: 4.1, type: 'commodity' },
  { symbol: 'BNB/USD', price: 412, change: 2.4, type: 'crypto' },
  { symbol: 'COPPER', price: 4.12, change: -0.8, type: 'commodity' },
  { symbol: 'WHEAT', price: 548, change: -1.2, type: 'commodity' },
  { symbol: 'DOGE/USD', price: 0.128, change: 6.4, type: 'crypto' },
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
    <div className="w-full overflow-hidden bg-bg-secondary border-y border-accent-blue/10 py-3">
      <div
        className="flex gap-8 whitespace-nowrap"
        style={{
          animation: 'ticker 40s linear infinite',
          display: 'flex',
          width: 'max-content',
        }}
      >
        {doubled.map((item, index) => (
          <div key={`${item.symbol}-${index}`} className="flex items-center gap-3 px-2">
            <span className="text-gray-400 text-sm font-medium">{item.symbol}</span>
            <span className="text-white text-sm font-bold">${formatPrice(item.price)}</span>
            <span
              className={`flex items-center gap-0.5 text-xs font-medium ${
                item.change >= 0 ? 'text-accent-green' : 'text-accent-red'
              }`}
            >
              {item.change >= 0 ? (
                <TrendingUp className="w-3 h-3" />
              ) : (
                <TrendingDown className="w-3 h-3" />
              )}
              {Math.abs(item.change).toFixed(2)}%
            </span>
            <span className="text-gray-700">|</span>
          </div>
        ))}
      </div>
    </div>
  )
}
