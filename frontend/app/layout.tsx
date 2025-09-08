import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Analytics } from '@vercel/analytics/react'
import { SpeedInsights } from '@vercel/speed-insights/next'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'FormFlow AI - Turn Forms into AI-Powered Dashboards in 60 Seconds',
  description: 'Transform boring form responses into beautiful, intelligent dashboards that your clients will love. Works with Typeform, Google Forms, and more. No coding required.',
  keywords: 'form builder, ai dashboard, typeform alternative, form analytics, ai forms, intelligent dashboards, form automation',
  authors: [{ name: 'FormFlow AI' }],
  creator: 'FormFlow AI',
  publisher: 'FormFlow AI',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://formflow.ai',
    title: 'FormFlow AI - Turn Forms into AI-Powered Dashboards',
    description: 'Transform form responses into beautiful, intelligent dashboards in 60 seconds. No coding required.',
    siteName: 'FormFlow AI',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'FormFlow AI - AI-Powered Form Dashboards',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'FormFlow AI - Turn Forms into AI-Powered Dashboards',
    description: 'Transform form responses into beautiful, intelligent dashboards in 60 seconds.',
    images: ['/twitter-image.png'],
    creator: '@formflowai',
  },
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
  manifest: '/site.webmanifest',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
      </head>
      <body className={`${inter.className} antialiased`}>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  )
}