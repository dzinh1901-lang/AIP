import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AIP — Agentic Market Intelligence Platform',
  description: 'Multi-model AI consensus signals for commodities & crypto. Real-time intelligence for smarter market decisions.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-bg-base text-text-base font-sans antialiased">
        {children}
      </body>
    </html>
  )
}
