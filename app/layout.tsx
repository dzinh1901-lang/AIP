import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AIP - Agentic Market Intelligence Platform',
  description: 'AI-Powered Market Intelligence with multi-model consensus signals for commodities & crypto',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-bg-primary text-white font-sans">
        {children}
      </body>
    </html>
  )
}
