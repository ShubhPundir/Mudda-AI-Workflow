'use client';

import Button from '@/components/Button';

interface WorkflowsHeaderProps {
  onGenerateClick: () => void;
}

export default function WorkflowsHeader({ onGenerateClick }: WorkflowsHeaderProps) {
  return (
    <div className="mb-8 flex justify-between items-start">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Workflows</h1>
        <p className="text-gray-500">
          Manage and generate AI-powered workflows for civic issues
        </p>
      </div>
      <Button
        onClick={onGenerateClick}
        variant="primary"
        size="lg"
        className="flex items-center space-x-2"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        <span>Generate Workflow</span>
      </Button>
    </div>
  );
}

