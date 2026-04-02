import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AIP — Market Intelligence Platform',
  description: 'Agentic Multi-Model Market Intelligence Platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased" style={{ background: 'var(--color-bg)', color: 'var(--color-text-primary)' }}>
        {children}
      </body>
    </html>
  )
}
