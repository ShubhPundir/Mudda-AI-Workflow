import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Sidebar from '@/components/Sidebar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Mudda AI Workflow System',
  description: 'AI-powered workflow generation for civic issue resolution',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} antialiased`}>
        <Sidebar />
        <main className="ml-64 min-h-screen bg-gradient-to-br from-blue-50/30 via-white to-indigo-50/20">
          {children}
        </main>
      </body>
    </html>
  )
}

