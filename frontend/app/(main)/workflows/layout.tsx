import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Workflows - Mudda AI Workflow System',
  description: 'Manage and generate AI-powered workflows for civic issues',
}

export default function WorkflowsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <>{children}</>
}

