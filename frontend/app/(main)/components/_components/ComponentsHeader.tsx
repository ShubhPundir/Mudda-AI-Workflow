'use client';

import Button from '@/components/Button';

interface ComponentsHeaderProps {
  onCreateClick: () => void;
}

export default function ComponentsHeader({ onCreateClick }: ComponentsHeaderProps) {
  return (
    <div className="mb-8 flex justify-between items-start">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Components</h1>
        <p className="text-gray-500">
          Manage API components for workflow integration
        </p>
      </div>
      <Button
        onClick={onCreateClick}
        variant="primary"
        size="lg"
        className="flex items-center space-x-2"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        <span>Create Component</span>
      </Button>
    </div>
  );
}

