import type { Metadata } from 'next'
import { DM_Mono, Inter, Source_Sans_3 } from 'next/font/google'
import { NuqsAdapter } from 'nuqs/adapters/next/app'
import { Toaster } from '@/components/ui/sonner'
import { AuthProvider } from '@/auth'
import './globals.css'

const inter = Inter({
  variable: '--font-inter',
  subsets: ['latin']
})

const sourceSans = Source_Sans_3({
  variable: '--font-source-sans',
  subsets: ['latin']
})

const dmMono = DM_Mono({
  subsets: ['latin'],
  variable: '--font-dm-mono',
  weight: '400'
})

export const metadata: Metadata = {
  title: 'Apollos AI',
  description:
    'Enterprise AI agent platform powered by Agno and Microsoft Entra ID.'
}

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} ${sourceSans.variable} ${dmMono.variable} antialiased`}
      >
        <AuthProvider>
          <NuqsAdapter>{children}</NuqsAdapter>
          <Toaster />
        </AuthProvider>
      </body>
    </html>
  )
}
