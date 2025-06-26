import React from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import { useAuth } from '@/hooks/useAuth'
import Hero from '@/components/home/Hero'
import Features from '@/components/home/Features'
import Pricing from '@/components/home/Pricing'
import Testimonials from '@/components/home/Testimonials'
import CTA from '@/components/home/CTA'
import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'

export default function HomePage() {
  const { user } = useAuth()
  const router = useRouter()

  // Redirect to dashboard if user is already logged in
  React.useEffect(() => {
    if (user) {
      router.push('/dashboard')
    }
  }, [user, router])

  return (
    <>
      <Head>
        <title>OSINT-AI Platform - Advanced Open Source Intelligence with AI</title>
        <meta
          name="description"
          content="Automate OSINT investigations with AI-powered analysis. Search people, emails, domains with advanced intelligence gathering."
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
        <Header />
        
        <main>
          <Hero />
          <Features />
          <Pricing />
          <Testimonials />
          <CTA />
        </main>

        <Footer />
      </div>
    </>
  )
}
