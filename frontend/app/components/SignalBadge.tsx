'use client'

import clsx from 'clsx'

interface SignalBadgeProps {
  signal: string
  size?: 'sm' | 'md' | 'lg'
}

const SIGNAL_STYLES: Record<string, string> = {
  BUY:  'bg-emerald-100 text-emerald-700 border border-emerald-300 ring-1 ring-emerald-200',
  SELL: 'bg-red-100 text-red-700 border border-red-300 ring-1 ring-red-200',
  HOLD: 'bg-amber-100 text-amber-700 border border-amber-300 ring-1 ring-amber-200',
}

const SIZES: Record<string, string> = {
  sm: 'text-[10px] px-1.5 py-0.5',
  md: 'text-xs px-2.5 py-1',
  lg: 'text-sm px-3.5 py-1.5',
}

export default function SignalBadge({ signal, size = 'md' }: SignalBadgeProps) {
  const sig = signal?.toUpperCase() || 'HOLD'
  const colorClass = SIGNAL_STYLES[sig] || SIGNAL_STYLES.HOLD

  return (
    <span
      className={clsx(
        'inline-flex items-center font-bold rounded-full tracking-wider leading-none',
        colorClass,
        SIZES[size]
      )}
    >
      {sig}
    </span>
  )
}
