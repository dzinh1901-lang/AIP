import Navbar from '@/components/Navbar'
import Hero from '@/components/Hero'
import MarketTicker from '@/components/MarketTicker'
import Features from '@/components/Features'
import Stats from '@/components/Stats'
import Footer from '@/components/Footer'

export default function Home() {
  return (
    <main className="min-h-screen bg-bg-primary">
      <Navbar />
      <Hero />
      <MarketTicker />
      <Features />
      <Stats />
      <Footer />
    </main>
  )
}
