'use client';

import { useState } from 'react';
import Modal from '@/components/Modal';
import Button from '@/components/Button';

interface GenerateWorkflowModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (problemStatement: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

export default function GenerateWorkflowModal({
  isOpen,
  onClose,
  onGenerate,
  isLoading,
  error,
}: GenerateWorkflowModalProps) {
  const [problemStatement, setProblemStatement] = useState('');

  const handleGenerate = async () => {
    if (!problemStatement.trim()) {
      return;
    }
    await onGenerate(problemStatement);
    if (!error) {
      setProblemStatement('');
    }
  };

  const handleClose = () => {
    setProblemStatement('');
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Generate New Workflow"
      size="lg"
    >
      <div className="space-y-5">
        <div>
          <label htmlFor="problem-statement" className="block text-sm font-semibold text-gray-700 mb-2.5">
            Problem Statement
          </label>
          <textarea
            id="problem-statement"
            rows={6}
            value={problemStatement}
            onChange={(e) => setProblemStatement(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all resize-none"
            placeholder="Describe the civic issue you want to resolve (e.g., 'Resolve pothole issue reported in Ward 22')"
          />
        </div>
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg text-sm flex items-center space-x-2">
            <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{error}</span>
          </div>
        )}
        <div className="flex justify-end space-x-3 pt-2">
          <Button
            variant="outline"
            onClick={handleClose}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleGenerate}
            isLoading={isLoading}
            disabled={!problemStatement.trim()}
          >
            Generate
          </Button>
        </div>
      </div>
    </Modal>
  );
}

