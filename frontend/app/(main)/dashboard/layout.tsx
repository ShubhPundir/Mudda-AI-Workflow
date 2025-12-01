import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Dashboard - Mudda AI Workflow System',
  description: 'Overview of workflow analytics and active issues',
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <>{children}</>
}

