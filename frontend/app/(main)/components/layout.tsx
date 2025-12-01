import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Components - Mudda AI Workflow System',
  description: 'Manage API components for workflow integration',
}

export default function ComponentsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <>{children}</>
}

